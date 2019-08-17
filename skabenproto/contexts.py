import json
import time

from skabenproto.packets import PING, PONG, ACK, NACK, WAIT, CUP, SUP, INFO
from skabenproto.packets import PINGLegacy

CMD = {
        'PING': PING,  # heartbeat, broadcast
        'LEGPING': PINGLegacy,  # legacy ping for non-smart
        'PONG': PONG,  # response to PING with PING timestamp
        'ACK': ACK,   # confirm success (to CUP/SUP)
        'NACK': NACK,  # confirm fail (to CUP/SUP)
        'WAIT': WAIT,  # device stop sending PONGs for a time
        'CUP': CUP,  # Client UPdate config from server
        'SUP': SUP,  # Server UPdate config from client
        'INFO': INFO  # other operations
}

# helpers

class SafeList(list):
    def get(self, index, default=None):
        try:
            return self.__getitem__(index)
        except IndexError:
            return default


def sjoin(strings):
    # join list with possible empty values
    return '/'.join(x.strip() for x in strings if x.strip())


class BaseContext:

    """
        basic context manager methods
    """

    def __init__(self):
        self.data = dict()

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

    def __repr__(self):
        return json.dumps(self.data)


class PacketEncoder(BaseContext):

    # packet encoder methods namespace

    timestamp = int()  # packet encoding time
    data = dict()  # for testing purposes

    def __init__(self):
        super().__init__()

    def load(self, packet_type, **kwargs):
        p = CMD.get(packet_type)
        if not p:
            raise Exception('cannot encode packet for {}'.format(packet_type))
        packet = p(**kwargs)
        return packet

    def encode(self, packet, timestamp=None):
        self.data = {}
        if not timestamp:
            timestamp = int(time.time())
        self.timestamp = timestamp  # save "encoded at" for tests
        if not packet:
            raise Exception('cannot encode empty packet - packet should be '
                            'loaded first')
        # encoding packet
        if packet.uid:
            # unicast, send by name
            topic = sjoin((packet.dev_type, str(packet.uid)))
        else:
            # broadcast, send by device type
            topic = packet.dev_type
        # assign timestamp
        self.data.update({'ts': timestamp})
        # filtering data
        _filtered_data = {k:v for k,v in packet.payload.items()
                              if v is not None}
        # update additional fields
        if hasattr(packet, 'payload'):
            self.data.update(**_filtered_data)
        data = json.dumps(self.data).replace("'", '"')
        payload = sjoin((packet.command, data))
        return tuple((topic, payload))


class PacketDecoder(BaseContext):

    # packet decoder methods namespace

    def __init__(self):
        super().__init__()

    def decode(self, message):
        # decoding packet from mqtt message
        data = {}
        # checking for invalid message format
        for attr in ('topic', 'payload'):
            if not hasattr(message, attr):
                raise Exception('attr <{}> missing from data {}' \
                                .format(attr, message))
        # from paho.mqtt topic received as string, but payload as b''
        try:
            msg_topic = SafeList(message.topic.split('/'))
            msg_payload = SafeList(message.payload.decode("utf-8").split('/'))
        except:
            #logging.exception('cannot decode {}'.format(message))
            raise
        # necessary field management
        data['dev_type'] = msg_topic.get(0, None)
        data['command'] = msg_payload.get(0, None)
        data['payload'] = msg_payload.get(1, None)

        # check for missing parts
        for field in ('dev_type', 'command', 'payload'):
            if not data.get(field):
                raise Exception('field <{}> missing from data {}' \
                                .format(field, data))

        # cut unneeded response marker
        if data['dev_type'].endswith('ask'):
            data['dev_type'] = data['dev_type'][:-3]

        # checking for martians
        if data['command'] not in CMD:
            raise Exception('unknown command <{}> in data <{}>'\
                                .format(data['command'], data))
        # this field is missing in broadcast packets
        data['uid'] = msg_topic.get(1, None)
        # payload managing
        _decoded_pl = json.loads(data['payload'])
        data['ts'] = _decoded_pl.get('ts', None)
        data['task_id'] = _decoded_pl.get('task_id', None)
        data['payload'] = _decoded_pl

        return data


