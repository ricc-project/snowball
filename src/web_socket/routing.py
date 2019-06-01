# from django.urls import path
from django.conf.urls import url

from . import consumers

websocket_url = [
    url(r'^ws/$', consumers.ActuatorConsumer),
]