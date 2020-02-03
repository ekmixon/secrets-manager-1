from slackclient import SlackClient
from app.config import Config


def slack_message(message):
    token = Config.SLACK_API_TOKEN
    if token is not None:
        sc = SlackClient(token)
        sc.api_call('chat.postMessage', channel=Config.SLACK_CHANNEL,
                    text=message, username=Config.SLACK_USERNAME)
