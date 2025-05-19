from signalrcore.hub_connection_builder import HubConnectionBuilder


class AccelpixApi:
    def __init__(self):
        self.connection = HubConnectionBuilder() \
            .with_url("https://datafeed.accelpix.in/accelpixhub") \
            .build()

    async def connect(self):
        self.connection.on_open(lambda: print("Connection opened"))
        self.connection.start()

    async def subscribeAll(self, symbols):
        if not symbols:
            return
        self.connection.send("SubscribeAll", [symbols])
