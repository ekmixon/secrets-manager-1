from flask import Flask
from healthcheck import HealthCheck
from datadog import initialize
from app.secretsmanager.controller import secretsmanager
from app.secretsmanager.secretsmanager import healthcheck as sm_healthcheck
from app.config import Config
import logging
from app.utils.kube_config import load_k8s_config

app = Flask(__name__)


def setup_datadog():
    options = None
    if Config.DOGSTATSD_HOST_IP is not None \
            and Config.DOGSTATSD_HOST_PORT is not None:
        options = {
            'statsd_host': Config.DOGSTATSD_HOST_IP,
            'statsd_port': Config.DOGSTATSD_HOST_PORT
        }
    elif Config.DD_API_KEY is not None and Config.DD_APP_KEY is not None:
        options = {
            'api_key': Config.DD_API_KEY,
            'app_key': Config.DD_APP_KEY
        }
    if options is not None:
        initialize(**options)


def log_config(app):
    if Config.BACKUP_S3_BUCKET is None:
        app.logger.info("Ignoring backup. BACKUP_S3_BUCKET not set")
    if Config.SLACK_API_TOKEN is None:
        app.logger.info("Ignoring slack notification. SLACK_API_TOKEN not set")


def setup(app):
    app.logger.setLevel(logging.INFO)
    setup_datadog()
    load_k8s_config()
    log_config(app)


setup(app)

health = HealthCheck(app, "/health")
health.add_check(sm_healthcheck)

app.register_blueprint(secretsmanager, url_prefix='/')
