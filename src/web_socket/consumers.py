import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ActuatorConsumer(WebsocketConsumer):

    def connect(self):
        self.actuator = self.scope['user']
        print('Connected: ', self.actuator)

        async_to_sync(self.channel_layer.group_add)(
            self.actuator,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response = text_data_json['message']
        
        if response == 200:
            print('Actuator successfuly switched')
        else:
            print('Failed to switch actuator')

    def switch(self, event):
        """
        Send a switch actuator message to the client socket.
        """
        self.send(text_data=json.dumps({
            'switch': True
        }))

        print('Sended switch message')

