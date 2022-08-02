from flask import Blueprint, json, Response
from app.secretsmanager.secretsmanager import run

secretsmanager = Blueprint('secretsmanager', __name__)


@secretsmanager.route('/ready')
def ready():
    return Response(
        response=json.dumps({"status": "ok"}),
        status=200,
        mimetype='application/json',
    )


@secretsmanager.route('/run')
def index():
    run()
    return Response(
        response=json.dumps({"status": "ok"}),
        status=200,
        mimetype='application/json',
    )
