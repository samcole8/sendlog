from plugin import Channel

class Stdout(Channel):
    __slots__ = []
    def __call__(self, payload):
        print(payload)
