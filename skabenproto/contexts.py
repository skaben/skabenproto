from skabenproto.packets import *

CMD = {
        'PING': PING,  # heartbeat, broadcast
        'PONG': PONG,  # response to PING with PING timestamp
        'ACK': ACK,   # confirm success (to CUP/SUP)
        'NACK': NACK,  # confirm fail (to CUP/SUP)
        'WAIT': WAIT,  # device stop sending PONGs for a time
        'CUP': CUP,  # Client UPdate config from server
        'SUP': SUP,  # Server UPdate config from client
        'INFO': INFO  # other operations
}


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

    def __init__(self):
        super().__init__()

    def load(self, packet_type, **kwargs):
        p = CMD.get(packet_type)
        if not p:
            raise Exception('cannot encode packet for {}'.format(packet_type))
        packet = p(**kwargs)
        return packet

    def encode(self, packet):
        if not packet:
            raise Exception('cannot encode empty packet - packet should be '
                            'created first')
        data = {}
        # encoding packet
        if packet.uid:
            # unicast, send by name
            topic = sjoin((packet.dev_type, str(packet.uid)))
        else:
            # broadcast, send by device type
            topic = packet.dev_type
        data.update({'ts': packet.ts})
        # update additional fields
        if hasattr(packet, 'payload'):
            data.update(**packet.payload)
        data = json.dumps(data).replace("'", '"')
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
            msg_topic = safelist(message.topic.split('/'))
            msg_payload = safelist(message.payload.decode("utf-8").split('/'))
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
        # checking for martians
        if data['command'] not in CMD:
            raise Exception('unknown command <{}> in data <{}>'\
                                .format(data['command'], data))
        # this field is missing in broadcast packets
        data['uid'] = msg_topic.get(1, None)
        # payload managing
        _decoded_pl = json.loads(data['payload'])
        self.dec = _decoded_pl
        data['ts'] = _decoded_pl.get('ts', None)
        data['task_id'] = _decoded_pl.get('task_id', None)
        data['payload'] = _decoded_pl
        # timestamp is necessary, task_id is not
        #if not data.get('ts'):
        #    raise Exception('missing timestamp in packet: {}'.format(data))
        # assigning for possible future use in context
        self.data = data
        return data


