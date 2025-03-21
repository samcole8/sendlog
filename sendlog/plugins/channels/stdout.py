from plugin import Channel

class Stdout(Channel):
    required_vars = []
    def __call__(self, payload):
        print(payload)
