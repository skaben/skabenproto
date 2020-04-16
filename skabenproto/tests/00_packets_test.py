import pytest
import random
import time

from skabenproto.packets import *

dev_types = [
    "lock",
    "term",
    "dumb",
]

TS = int(time.time())
UID = "00ff00ff00ff"
TASK_ID = "51048"

PAYLOAD = {"test": "value",
           "list": ['1', 0, True],
           "bool": False,
           "dict": {'test': 'value'}}


def get_random_from(_list):
    i = random.randint(0, len(_list)-1)
    return _list[i]


def test_base_packet():
    dev_type = get_random_from(dev_types)
    pkg = BasePacket(dev_type=dev_type,
                     uid=UID,
                     timestamp=TS)

    assert pkg.topic == f"{dev_type}/{UID}", "bad topic assigned"
    assert pkg.content.get("timestamp") == TS, "bad timestamp"


def test_base_packet_no_timestamp():
    dev_type = get_random_from(dev_types)
    pkg = BasePacket(dev_type=dev_type,
                     uid=UID)

    assert pkg.content.get("timestamp") == 0, "bad timestamp assigned, should be 0 if not provided"


def test_base_packet_no_uid():
    dev_type = get_random_from(dev_types)
    pkg = BasePacket(dev_type=dev_type)

    assert pkg.topic == f'{dev_type}'


@pytest.mark.parametrize(("packet", "cmd"), ((PING, "PING"), (PINGLegacy, "*/PING")))
def test_pings_normal(packet, cmd):
    dev_type = 'test'
    pkg = packet(dev_type=dev_type)

    assert pkg.command == cmd, f"bad command assigned: {cmd}"


def test_pong_normal():
    dev_type = 'test'
    pong = PONG(dev_type=dev_type, uid=UID, timestamp=TS)

    assert pong.command == 'PONG', f'bad command: {pong.command}'


@pytest.mark.parametrize(("packet", "cmd"), ((ACK, "ACK"), (NACK, "NACK")))
def test_ack_nack(packet, cmd):
    dev_type = get_random_from(dev_types)
    pkg = packet(dev_type=dev_type, uid=UID, timestamp=TS, task_id=TASK_ID)

    assert pkg.content.get('task_id') == TASK_ID, 'not assigned task id'


def test_base_payload_packet():
    dev_type = get_random_from(dev_types)
    pkg = PayloadPacket(dev_type=dev_type,
                        payload=PAYLOAD,
                        timestamp=TS)

    assert pkg.content.get('timestamp') == TS, 'timestamp not assigned'
    assert pkg.content.get('payload') == PAYLOAD, 'payload not assigned'


@pytest.mark.parametrize(("packet", "cmd"), ((INFO, "INFO"), (SUP, "SUP")))
def test_payload_no_task_id(packet, cmd):
    dev_type = get_random_from(dev_types)
    pkg = packet(dev_type=dev_type,
                 payload=PAYLOAD,
                 timestamp=TS,
                 uid=UID)

    assert pkg.command == cmd, 'bad command assigned'


@pytest.mark.parametrize(("packet", "cmd"), ((INFO, "INFO"), (SUP, "SUP"), (CUP, "CUP")))
def test_payload_with_task_id(packet, cmd):
    dev_type = get_random_from(dev_types)
    pkg = packet(dev_type=dev_type,
                 payload=PAYLOAD,
                 timestamp=TS,
                 uid=UID,
                 task_id=TASK_ID)

    assert pkg.command == cmd, 'bad command assigned'
    assert pkg.content.get('task_id') == TASK_ID, 'bad task_id'


def test_fail():
    assert 1 == 0, "no deploy pls"
