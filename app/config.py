import os


class Config(object):
    ENV = os.environ.get('ENV') or 'dev'
    BACKUP_S3_BUCKET = os.environ.get('BACKUP_S3_BUCKET')
    # uses internal kube config if not passed in
    KUBE_CONFIG_PATH = os.environ.get('KUBE_CONFIG_PATH')
    DOGSTATSD_HOST_IP = os.environ.get('DOGSTATSD_HOST_IP')
    DOGSTATSD_HOST_PORT = os.environ.get('DOGSTATSD_HOST_PORT')
    DD_API_KEY = os.environ.get('DD_API_KEY')
    DD_APP_KEY = os.environ.get('DD_APP_KEY')
    CONFIG_PATH = os.environ.get(
        'CONFIG_PATH') or '/etc/secrets_manager/config.yaml'
    SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")
    SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
    SLACK_USERNAME = os.environ.get("SLACK_USERNAME")
