import channels.layers
from asgiref.sync import async_to_sync


def switch(mac_addr, user=None):
    """
    Switch the state of the user actuator.
    """
    channel_layer = channels.layers.get_channel_layer()
    addr = mac_addr.replace(':', '-')

    async_to_sync(channel_layer.group_send)(
        addr,
        {
            'type': 'switch',
            'message': True
        }
    )
