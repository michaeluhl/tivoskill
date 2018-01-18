import os
from queue import Queue
from threading import Event

import lambdaskill
import libtivomind.api as api


from pubnub.enums import PNOperationType, PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


class Communicator(SubscribeCallback):

    def __init__(self, config, channel_pub, channel_sub):
        self.__config = config
        self.__channel_pub = channel_pub
        self.__channel_sub = channel_sub
        self.__pubnub = None
        self.__queue = Queue()
        self.__connected = Event()

    def run(self):
        self.__pubnub = PubNub(self.__config)
        self.__pubnub.add_listener(self)
        self.__pubnub.subscribe().channels(self.__channel_sub).execute()

    @property
    def connected(self):
        return self.__connected.is_set()

    def message(self, pubnub, message):
        self.__queue.put(message.message)

    def get_message(self):
        m = self.__queue.get()
        self.__queue.task_done()
        return m

    def status(self, pubnub, status):
        if status.operation in (PNOperationType.PNSubscribeOperation, PNOperationType.PNUnsubscribeOperation):
            if status.category == PNStatusCategory.PNConnectedCategory:
                self.__connected.set()
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                self.__connected.clear()

    def presence(self, pubnub, presence):
        pass

    def publish(self, message):
        self.__pubnub.publish().channel(self.__channel_pub).message(message).sync()


class Tivo(lambdaskill.Skill):

    def __init__(self):
        super().__init__()
        self._app_id = os.environ['APP_ID']

        pnconfig = PNConfiguration()
        pnconfig.publish_key = os.environ['PUBKEY']
        pnconfig.subscribe_key = os.environ['SUBKEY']
        pnconfig.uuid = os.environ['CLIENT_ID']
        pnconfig.ssl = True

        self.__comm = Communicator(pnconfig,
                                   os.environ['PUBLISH_CHANNEL'],
                                   os.environ['SUBSCRIBE_CHANNEL'])
        self.__comm.run()


    def on_launch_request(self, request):
        return lambdaskill.Response.respond('Welcome to TiVo Talk')

    def do_pauseintent(self, request):
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.pause.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="Paused")

    def do_resumeintent(self, request):
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.play.name}})
        return lambdaskill.Response.finish(output="Resuming")

    def do_advanceintent(self, request):
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.advance.name}})
        return lambdaskill.Response.finish(output="Advancing")

    def do_testintent(self, request):
        return lambdaskill.Response.finish(output="Test Response")


handler = Tivo.get_handler()

