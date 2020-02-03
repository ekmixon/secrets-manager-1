import ast
import base64
import io
import os

import boto3
import yaml
from botocore.exceptions import ClientError
from datadog import statsd
from kubernetes import client

from app.config import Config
from app.utils.notify import slack_message
from flask import current_app
from app.secretsmanager.aws_secret import AWSSecret, MalformedSecret


def get_kube_secret(namespace, name):
    api = client.CoreV1Api()
    query = "metadata.name=" + name
    secrets = api.list_namespaced_secret(namespace, field_selector=query)
    return secrets


def get_kube_secret_data(namespace, name):
    secrets = get_kube_secret(namespace, name)
    return secrets.items[0].data


def parse_query(data):

    secrets_data_dict_conversion = ast.literal_eval(data)

    secret_data_dict_encoded = {}
    for key, value in secrets_data_dict_conversion.items():
        secret_data_dict_encoded[key] = base64.b64encode(
            value.encode()).decode("utf-8")

    return secret_data_dict_encoded


def get_k8s_secrets_config(secrets_name, namespace, data, modified_time):
    secrets_config = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": secrets_name,
            "namespace": namespace,
            "labels": {
                "aws_last_modified": modified_time
            }
        },
        "type": "Opaque",
        "data": data
    }
    return secrets_config


def apply_k8s_secrets(secrets_name, namespace, secrets_config):
    api = client.CoreV1Api()
    try:
        api.create_namespaced_secret(namespace, secrets_config)
        current_app.logger.info(f"Secret created: {secrets_name}")
    except client.rest.ApiException:
        api.replace_namespaced_secret(secrets_name, namespace, secrets_config)
        current_app.logger.info(f"Secret modified: {secrets_name}")


def get_secret_manager_client():
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    return client


def describe_aws_secret(secret_name):
    client = get_secret_manager_client()
    response = client.describe_secret(
        SecretId=secret_name
    )
    return response


def get_aws_secret(secret_name):
    client = get_secret_manager_client()
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these
        # fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            return decoded_binary_secret


def get_all_aws_secrets():
    client = get_secret_manager_client()

    def get_token(data):
        return data.get('NextToken', None)
    try:
        secrets_per_request = 30
        secrets = []

        data = client.list_secrets(MaxResults=secrets_per_request)
        secrets += data['SecretList']
        next_token = get_token(data)
        while next_token:
            data = client.list_secrets(
                MaxResults=secrets_per_request,
                NextToken=next_token)
            next_token = get_token(data)
            secrets += data['SecretList']
        return secrets
    except ClientError as e:
        raise e


def parse_secrets(config, secrets):
    secret_config = []
    for secret in secrets:
        if config is None:
            obj = {
                "aws_secret_manager_name": secret.aws_name,
                "namespace": secret.env,
                "secret_name": secret.name
            }
            secret_config.append(obj)
        else:
            secret_manager_envs = config['secret_manager_envs']
            for secret_manager_env in secret_manager_envs:
                secret_manager_env_name = secret_manager_env['name']
                if secret.env == secret_manager_env_name:
                    namespaces = secret_manager_env.get('namespaces')
                    if namespaces is None:
                        namespaces = [secret_manager_env_name]
                    for namespace in namespaces:
                        obj = {
                            "aws_secret_manager_name": secret.aws_name,
                            "namespace": namespace,
                            "secret_name": secret.name
                        }
                        secret_config.append(obj)

    return secret_config


def backup_secrets(file_name, data):
    current_app.logger.info(f"Trying to back up secrets {file_name}")
    with io.StringIO() as f:
        yaml.dump(data, f, default_flow_style=False)
        session = boto3.session.Session()
        s3 = session.resource("s3")
        bucket_name = Config.BACKUP_S3_BUCKET
        bucket = s3.Bucket(bucket_name)
        f.seek(0)
        bucket.Object(key=file_name).put(Body=f.read())
    current_app.logger.info(f"Secrets backed up {file_name}")


def compare_secrets(
        config,
        incoming_secrets,
        current_secrets,
        env,
        secret_name,
        secret_store):
    def notify(key, status):
        message = f":key: secret: `{key}` *{status}* in `{env}`, " \
                  f"secret-name: `{secret_name}`," \
                  f" secret-store: `{secret_store}`"
        slack_message(message)

    if (incoming_secrets != current_secrets):
        for key, value in incoming_secrets.items():
            try:
                if (value != current_secrets[key]):
                    notify(key, "updated")
            except KeyError:
                notify(key, "added")
        for key, value in current_secrets.items():
            try:
                incoming_secrets[key]
            except KeyError:
                notify(key, "deleted")


def load_yaml_file(file):
    if os.path.isfile(file):
        with open(file, 'r') as stream:
            return yaml.safe_load(stream)
    else:
        return None


def parse_secrets_config(secrets_config_data_config, secret_names):
    secret_objs = []
    ignored_secrets = []
    for secret_name in secret_names:
        try:
            aws_secret_obj = AWSSecret(secret_name)
            secret_objs.append(aws_secret_obj)
        except MalformedSecret:
            ignored_secrets.append(secret_name)

    secrets_config = parse_secrets(secrets_config_data_config, secret_objs)

    custom_secrets = []
    if secrets_config_data_config is not None:
        custom_secrets = secrets_config_data_config.get('custom_secrets') or []
    env_config = secrets_config + custom_secrets
    return env_config, ignored_secrets


def healthcheck():
    run()
    return True, "secretsmanager ok"


def run():
    config_file = Config.CONFIG_PATH
    secrets_config_data = load_yaml_file(config_file)
    secrets_config_data_config = None
    if secrets_config_data is not None:
        secrets_config_data_config = secrets_config_data.get('config')

    env = Config.ENV

    secret_names = get_all_aws_secrets()

    env_config, ignored_secrets = parse_secrets_config(
        secrets_config_data_config, secret_names)

    for s in ignored_secrets:
        current_app.logger.info(
            f"Ignoring malformed secret name: {s['Name']}")

    for c in env_config:
        aws_secret_manager_name = c["aws_secret_manager_name"]
        secret_name = c["secret_name"]
        namespace = c["namespace"]

        # See when AWS secrets manager was last changed
        aws_secret_info = describe_aws_secret(aws_secret_manager_name)
        aws_last_modified_time_obj = aws_secret_info['LastChangedDate']
        aws_last_modified_time = aws_last_modified_time_obj.strftime(
            "%Y-%m-%d_%H-%M-%S")

        # Grab kubernetes secrets
        try:
            k8s_secret = get_kube_secret(namespace, secret_name)
        except client.rest.ApiException:
            k8s_secret = None
        try:
            k8s_last_modufied_time = \
                k8s_secret.items[0].metadata.labels['aws_last_modified']
        except (TypeError, IndexError, AttributeError):
            k8s_last_modufied_time = None
        try:
            k8s_secret_data = k8s_secret.items[0].data
        except (TypeError, IndexError, AttributeError):
            k8s_secret_data = {}
        if k8s_secret_data is None:
            k8s_secret_data = {}

        needs_an_update = (aws_last_modified_time != k8s_last_modufied_time)

        config_logging = c.copy()
        config_logging["aws_last_updated"] = aws_last_modified_time
        config_logging["k8s_last_updated"] = k8s_last_modufied_time
        config_logging["needs_update"] = needs_an_update
        current_app.logger.info(f"Checking {config_logging}")

        if (needs_an_update):
            # Get and parse aws secrets
            secret = get_aws_secret(aws_secret_manager_name)

            secrets_data = parse_query(secret)

            # Log and notify change
            compare_secrets(
                secrets_config_data_config,
                secrets_data,
                k8s_secret_data,
                env,
                secret_name,
                aws_secret_manager_name)

            # Create k8s config
            secrets_config = get_k8s_secrets_config(
                secret_name, namespace, secrets_data, aws_last_modified_time)
            # Apply secrets to k8s
            apply_k8s_secrets(secret_name, namespace, secrets_config)
            # Backup secrets to s3
            file_name = "{}-{}.yml".format(secret_name, env)
            if Config.BACKUP_S3_BUCKET is not None:
                backup_secrets(file_name, secrets_config)

            if (secrets_data != k8s_secret_data):
                statsd.increment(
                    'secretupdated.{}'.format(env), tags=[
                        "secretname:{}".format(secret_name)])
    statsd.increment('Secrets_Updated')


def main():
    run()


if __name__ == "__main__":
    main()
