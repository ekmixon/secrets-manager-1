#!/bin/sh
set -e

if [[ -z "$KUBE_CONFIG_PATH" ]]; then
    export KUBE_CONFIG_PATH="."
fi
if [[ -z "$KUBE_CONFIG_S3" ]]; then
    echo "KUBE_CONFIG_S3 not set"
else
    pipenv run aws s3 cp --region us-west-2 "$KUBE_CONFIG_S3" "$KUBE_CONFIG_PATH"
fi

exec pipenv run python run.py