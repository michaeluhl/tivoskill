import logging
import os
from queue import Queue
from threading import Event

import lambdaskill
import libtivomind.api as api


from pubnub.enums import PNOperationType, PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


logger = logging.getLogger('lambdaskill')


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
        return lambdaskill.Response.respond('Welcome to TiVo Control')

    def do_pauseintent(self, request):
        logger.info('PauseIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.pause.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="Paused")

    def do_resumeintent(self, request):
        logger.info('ResumeIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.play.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="Resuming")

    def do_advanceintent(self, request):
        logger.info('AdvanceIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.advance.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_selectintent(self, request):
        logger.info('SelectIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.select.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_liveintent(self, request):
        logger.info('LiveIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.liveTv.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_lastchannelintent(self, request):
        logger.info('LastChannelIntent')
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': api.RemoteKey.enter.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_directionintent(self, request):
        slots = request.get_slots()
        direction = slots['direction']
        logger.info('DirectionIntent, direction={}'.format(direction))
        key = api.RemoteKey[direction]
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': key.name}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_typedintent(self, request):
        slots = request.get_slots()
        typed_text = slots['words_to_type']
        logger.info('TypedIntent, words_to_type="{}"'.format(typed_text))
        self.__comm.publish({'type': 'request', 'cmd': 'remote_key', 'params': {'key': 'string', 'value': typed_text}})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish(output="")

    def do_channelchangeintent(self, request):
        slots = request.get_slots()
        params = {k: v for k, v in slots.items() if k in ['channel_number', 'channel_name']}
        logger.info('ChannelChangeIntent, params={}'.format(str(params)))
        self.__comm.publish({'type': 'request', 'cmd': 'change_channel', 'params': params})
        result = self.__comm.get_message()
        return lambdaskill.Response.finish('Changed.')


handler = Tivo.get_handler()

