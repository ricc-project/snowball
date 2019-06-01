

class MacAuthMiddleware:
    """
    Custom middleware that authenticates through MAC address.
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        mac = 'aasdad'
        
        try:
            raw_mac = scope['query_string'].decode('utf-8')
            mac = raw_mac.strip('mac=').replace(':', '-')
        except:
            pass

        user = mac

        return self.inner(dict(scope, user=user))