# Secrets Manager

## Introduction
Secrets manager is a service written for Kubernetes. Secrets manager is simple, customizable, and secure.

Users create secrets in AWS secrets manager service, and secret manager automatically applies these secrets into Kubernetes. It lets AWS handle the security of the secrets, and Secrets manager does the Kubernetes management. It's simple design lets you install and forget.


## Design
The green box is secrets manager. It pulls secrets from AWS Secrets Manager, converts them to Kubernetes secrets, and applies them into Kubernetes.

![Arch Logo](/images/arch.png)

## Installation
### Prerequisites
Make sure the secrets manager pods has access to read AWS secrets manager. Pass in `AWS_SECRET_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY` to the pod if needed.

### Default Installation
 **WARNING**, this will pull all secrets from AWS with names matching `<secret>/<name>` and apply them. Do with caution.

See [example_k8s_config.yaml](https://github.com/limebike/secrets-manager/blob/master/example/example_k8s_config.yaml). Run `kubectl apply -f example/example_k8s_config.yaml`

### One namespace installation
This will only apply secrets into the default namespace if named `default/<name>`. See [example_one_namespace_k8s_config.yaml](https://github.com/limebike/secrets-manager/blob/master/example/example_one_namespace_config.yaml). Run `kubectl apply -f example/example_one_namespace_config.yaml`

## Usage
Follow the [AWS docs](https://docs.aws.amazon.com/secretsmanager/latest/userguide//tutorials_basic.html) on how to add a key-value secret into AWS secrets manager.
With the default installation above, the name of the AWS secret store needs to follow: `<namespace>/<name-of-secret>`. This will apply the secret named `<name-of-secret>`  into the corresponding kubernetes namespace, `<namespace>`.


## Custom Config
Modify config.yaml file in [example_k8s_config.yaml](https://github.com/limebike/secrets-manager/blob/master/example/example_k8s_config.yaml) in order to do custom secret installations.

### Simple namespace config
```
config:
  secret_manager_envs:
    - name: production
```

### Multiple namespaces config
```
config:
  secret_manager_envs:
    - name: production
      namespaces:
        - production
        - default
```

### Custom secret config
```
config:
  secret_manager_envs:
    - name: production
      namespaces:
        - production
        - default
  custom_secrets:
    - aws_secret_manager_name: kube-system/datadog-secret
      secret_name: datadog-secret
      namespace: kube-system
    - aws_secret_manager_name: kube-system/logdna-agent
      secret_name: logdna-agent
      namespace: kube-system
```

## Contributing
Pull requests are welcome! Please see our [contributing guidelines](https://github.com/limebike/secrets-manager/blob/master/.github/CONTRIBUTING.md) for more details.