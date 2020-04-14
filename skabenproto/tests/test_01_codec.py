import time
import json
import pytest

import skabenproto.packets as packets
import skabenproto.contexts as contexts

from skabenproto.tests.mocks import dev_types, TS, UID, TASK_ID
from skabenproto.tests.mocks import get_random_from


def test_encoder_load(fake_mqtt):
    """ Smoke test encoder load method"""
    cmd = 'PING'  # most basic packet
    dev_type = get_random_from(dev_types)
    _topic = dev_type
    _payload = '{}/{{\"ts\": {}}}'.format(cmd, TS)
    with contexts.PacketEncoder() as encoder:
        pkg = encoder.load(cmd, dev_type=dev_type)
        assert isinstance(pkg, packets.PING), f'wrong instance: {type(pkg)}'


def test_encoder_encode(fake_mqtt):
    """ Smoke test encoder encode method"""
    cmd = 'PING'
    dev_type = get_random_from(dev_types)
    _timestamp = 123456789
    _topic = dev_type
    _payload = '{}/{{\"ts\": {}}}'.format(cmd, TS)
    with contexts.PacketEncoder() as encoder:
        pkg = encoder.load(cmd, dev_type=dev_type)
        message = encoder.encode(pkg, timestamp=_timestamp)
        assert encoder.timestamp == _timestamp
        assert message[0] == _topic, f"bad topic in {message}"
        assert message[1] == _payload, f"bad payload in {message}"
        with fake_mqtt(message) as fm:
            assert fm.topic == _topic, fm
            assert fm.payload == bytes(_payload, 'utf-8'), fm


def test_timestamp_not_provided(fake_mqtt):
    """Test encoder with timestamp not provided"""
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        pkg = encoder.load(packet_type='PING',
                           dev_type=dev_type,
                           uid=UID)
        message = encoder.encode(pkg)
        ts = json.loads(message[1].split('/')[1])['ts']
        assert not pkg.ts, 'pkg should not have timestamp'
        assert encoder.timestamp == ts, 'bad timestamp'


def test_timestamp_provided(fake_mqtt):
    """Test encoder with timestamp provided"""
    timestamp = int(time.time())
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        pkg = encoder.load(packet_type='PING',
                           dev_type=dev_type,
                           uid=UID)
        message = encoder.encode(pkg, timestamp=timestamp)
        ts = json.loads(message[1].split('/')[1])['ts']
        assert not pkg.ts, 'pkg should not have timestamp'
        assert encoder.timestamp == ts, 'bad timestamp'


def test_encdec_ping_broadcast(fake_mqtt):
    """ Test ping without device UID """
    cmd = 'PING'
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type)
        message = encoder.encode(res)
        test_payload = bytes('%s/{\"ts\": %s}' % \
                             (cmd, encoder.timestamp), 'utf-8')

        with fake_mqtt(message) as fm:
            assert fm.payload == test_payload, f"bad payload for {fm}"
            assert fm.topic == dev_type, f"bad topic for {fm}"

            with contexts.PacketDecoder() as decoder:
                decoded = decoder.decode(fm)

                assert decoded.get('command') == cmd
                assert decoded.get('dev_type') == dev_type


@pytest.mark.parametrize('cmd', ('PING', 'PONG',))
def test_encdec_ping_unicast(cmd, fake_mqtt):
    with contexts.PacketEncoder() as encoder:
        dev_type = get_random_from(dev_types)
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           uid=UID)
        message = encoder.encode(res)
        test_payload = bytes('%s/{\"ts\": %s}' % \
                             (cmd, encoder.timestamp), 'utf-8')

        with fake_mqtt(message) as fm:
            assert fm.topic == '/'.join((dev_type, UID))
            assert fm.payload == test_payload, fm

            with contexts.PacketDecoder() as decoder:
                decoded = decoder.decode(fm)

                assert decoded.get('command') == cmd
                assert decoded.get('dev_type') == dev_type
                assert decoded.get('uid') == UID


@pytest.mark.parametrize('cmd', ('ACK', 'NACK'))
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