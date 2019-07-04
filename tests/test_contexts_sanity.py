import pytest

import time
import contexts
import packets
import random

# valid data

dev_types = [
    'lock',
    'term',
    'dumb',
]

TS = int(time.time())
UID = '00ff00ff00ff'
TASK_ID = '12345'

class FakeMsg:

    def __init__(self, msg_tuple):
        self.topic = msg_tuple[0]
        self.payload = bytes(msg_tuple[1], 'utf-8')


def fake_mqtt(msg_tuple):
    return FakeMsg(msg_tuple)


def get_random_from(_list):
    i = random.randint(0, len(_list)-1)
    return _list[i]

# sanity tests

@pytest.mark.parametrize('cmd', ('PING', 'PONG'))
def test_sanity_ping(cmd):
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           ts=TS,
                           uid=UID)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res
        assert res.dev_type == dev_type, res
        assert res.ts == TS, res
        assert res.uid == UID, res


@pytest.mark.parametrize('cmd', ('ACK', 'NACK'))
def test_sanity_ack(cmd):
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           task_id=TASK_ID,
                           dev_type=dev_type,
                           ts=TS,
                           uid=UID)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res
        assert res.dev_type == dev_type, res
        assert res.ts == TS, res
        assert res.uid == UID, res


@pytest.mark.parametrize('cmd', ('CUP', 'SUP', 'INFO'))
def test_sanity_payload(cmd):
    sanity_payload = {'data': 'data'}
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           task_id=TASK_ID,
                           payload=sanity_payload,
                           uid=UID,
                           ts=TS)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res
        assert res.dev_type == dev_type, res
        assert res.ts == TS, res
        assert res.uid == UID, res
        # and here goes task_id
        sanity_payload.update({'task_id': TASK_ID,
                               'ts': TS})
        assert res.payload == sanity_payload, res

# encoding/decoding tests

@pytest.mark.parametrize('cmd', ('PING', 'PONG'))
def test_encdec_ping(cmd):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           ts=TS,
                           uid=UID)
        message = encoder.encode(res)
        fake_msg = fake_mqtt(message)
        with contexts.PacketDecoder() as decoder:
            decoded = decoder.decode(fake_msg)

            assert decoded.get('command') == cmd
            assert decoded.get('dev_type') == dev_type
            assert decoded.get('uid') == UID
            assert decoded.get('ts') == TS


@pytest.mark.parametrize('cmd', ('ACK', 'NACK'))
def test_encdec_ack(cmd):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           task_id=TASK_ID,
                           ts=TS,
                           uid=UID)
        message = encoder.encode(res)
        fake_msg = fake_mqtt(message)
        with contexts.PacketDecoder() as decoder:
            decoded = decoder.decode(fake_msg)

            assert decoded.get('command') == cmd
            assert decoded.get('dev_type') == dev_type
            assert decoded.get('uid') == UID
            assert decoded.get('ts') == TS


@pytest.mark.parametrize('cmd', ('CUP', 'SUP', 'INFO'))
def test_encdec_payload(cmd):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           payload={'data': 'data'},
                           task_id=TASK_ID,
                           ts=TS,
                           uid=UID)
        message = encoder.encode(res)
        fake_msg = fake_mqtt(message)
        with contexts.PacketDecoder() as decoder:
            decoded = decoder.decode(fake_msg)

            assert decoded.get('command') == cmd
            assert decoded.get('dev_type') == dev_type
            assert decoded.get('uid') == UID
            assert decoded.get('ts') == TS
            assert decoded.get('payload')
            assert decoded.get('payload').get('data') == 'data'