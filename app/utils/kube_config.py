from kubernetes import config as k8s_config
from app.config import Config


def load_k8s_config():
    try:
        if Config.KUBE_CONFIG_PATH is not None:
            k8s_config.load_kube_config(Config.KUBE_CONFIG_PATH)
        else:
            k8s_config.load_kube_config()
    except Exception:
        k8s_config.load_incluster_config()
