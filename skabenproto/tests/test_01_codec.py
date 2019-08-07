import time
import json
import pytest

from skabenproto.packets import BasePacket
import skabenproto.contexts as contexts

from skabenproto.tests.mocks import dev_types, TS, UID, TASK_ID
from skabenproto.tests.mocks import get_random_from

# encoder test
# strange behavior with task_id
@pytest.mark.parametrize('cmd', ('WAIT',))
def test_encoder(cmd, fake_mqtt):
    dev_type = get_random_from(dev_types)
    _topic = dev_type
    #_topic = '/'.join((dev_type, UID))
    _payload = '{}/{{\"ts\": {}}}'.format(cmd, TS)
    with contexts.PacketEncoder() as encoder:
        pkg = BasePacket(dev_type=dev_type)
        pkg.command = cmd # for example
        assert not pkg.payload.get('task_id'), \
            f'bad task_id assigned by package {pkg}'
        message = encoder.encode(pkg, TS)
        assert not encoder.data.get('task_id'), \
            f'bad task_id from encoder: {message}'
        assert encoder.timestamp == TS, 'bad encoder timestamp'
        assert message[0] == _topic, message
        assert message[1] == _payload, message
        with fake_mqtt(message) as fm:
            assert fm.topic == _topic, fm
            assert fm.payload == bytes(_payload, 'utf-8'), fm


def test_timestamp_basic(fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        timestamp = int(time.time())
        pkg = encoder.load(packet_type='PING',
                           dev_type=dev_type,
                           uid=UID)
        assert not pkg.ts, 'wrongfully assigned timestamp to pkg'
        message = encoder.encode(pkg)
        ts = json.loads(message[1].split('/')[1]).get('ts')
        assert encoder.timestamp == ts, 'bad timestamp'


def test_timestamp_loaded(fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        timestamp = int(time.time())
        payload = {'data': 'data'}
        pkg = encoder.load(packet_type='SUP',
                           dev_type=dev_type,
                           payload=payload,
                           uid=UID)
        assert not pkg.ts, 'wrongfully assigned timestamp to pkg'
        message = encoder.encode(pkg)
        ts = json.loads(message[1].split('/')[1]).get('ts')
        assert encoder.timestamp == ts, 'bad timestamp'

# encoding/decoding tests

# strange behavior with task_id
@pytest.mark.parametrize('cmd', ('PING',))
def test_encdec_ping(cmd, fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           uid=UID)
        message = encoder.encode(res)
        test_payload = bytes('%s/{\"ts\": %s}' % \
                             (cmd, encoder.timestamp), 'utf-8')

        with fake_mqtt(message) as fm:
            assert fm.payload == test_payload, fm

            with contexts.PacketDecoder() as decoder:
                decoded = decoder.decode(fm)

                assert decoded.get('command') == cmd
                assert decoded.get('dev_type') == dev_type
                assert decoded.get('uid') == UID

# skipped due to strange task_id
@pytest.mark.parametrize('cmd', ('ACK',))
def test_encdec_ack(cmd, fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           task_id=TASK_ID,
                           uid=UID)
        message = encoder.encode(res)
        with fake_mqtt(message) as fm:
            with contexts.PacketDecoder() as decoder:
                decoded = decoder.decode(fm)

                assert decoded.get('command') == cmd
                assert decoded.get('dev_type') == dev_type
                assert decoded.get('uid') == UID


@pytest.mark.parametrize('cmd', ('CUP', 'SUP', 'INFO'))
def test_encdec_payload(cmd, fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           payload={'data': 'data'},
                           task_id=TASK_ID,
                           uid=UID)
        message = encoder.encode(res)
        with fake_mqtt(message) as fm:
            with contexts.PacketDecoder() as decoder:
                decoded = decoder.decode(fm)

                assert decoded.get('command') == cmd
                assert decoded.get('dev_type') == dev_type
                assert decoded.get('uid') == UID
                assert decoded.get('payload')
                assert decoded.get('payload').get('data') == 'data'