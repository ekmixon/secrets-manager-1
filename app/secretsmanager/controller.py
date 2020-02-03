from flask import Blueprint, json, Response
from app.secretsmanager.secretsmanager import run

secretsmanager = Blueprint('secretsmanager', __name__)


@secretsmanager.route('/ready')
def ready():
    response = Response(
        response=json.dumps({"status": "ok"}),
        status=200,
        mimetype='application/json'
    )
    return response


@secretsmanager.route('/run')
def index():
    run()
    response = Response(
        response=json.dumps({"status": "ok"}),
        status=200,
        mimetype='application/json'
    )
    return response
