import pytest
import random
import time

import skabenproto.packets as sp

topics = [
    "lock",
    "term",
    "dumb",
]

TS = int(time.time())
UID = "00ff00ff00ff"
TASK_ID = "51048"

DATA = {"test": "value",
        "list": ['1', 0, True],
        "bool": False,
        "dict": {'test': 'value'}}


def get_random_from(_list):
    i = random.randint(0, len(_list) - 1)
    return _list[i]


def test_base_packet():
    topic = get_random_from(topics)
    pkg = sp.BasePacket(topic=topic,
                        uid=UID,
                        timestamp=TS)

    assert pkg.topic == f"{topic}/{UID}", "bad topic assigned"
    assert pkg.payload.get("timestamp") == TS, "bad timestamp"


def test_base_packet_no_timestamp():
    topic = get_random_from(topics)
    pkg = sp.BasePacket(topic=topic,
                        uid=UID)

    assert pkg.payload.get("timestamp") == 0, "bad timestamp assigned, should be 0 if not provided"


def test_base_packet_no_uid():
    topic = get_random_from(topics)
    pkg = sp.BasePacket(topic=topic)

    assert pkg.topic == f'{topic}'


@pytest.mark.parametrize(("packet", "cmd"), [(sp.PING, "ping")])
def test_pings_normal(packet, cmd):
    topic = 'test'
    pkg = packet(topic=topic)

    assert pkg.command == cmd, f"bad command assigned: {cmd}"


def test_pong_normal():
    topic = 'test'
    pong = sp.PONG(topic=topic, uid=UID, timestamp=TS)

    assert pong.command == 'pong', f'bad command: {pong.command}'


@pytest.mark.skip(reason="not used")
@pytest.mark.parametrize(("packet", "cmd"), ((sp.ACK, "ack"), (sp.NACK, "nack")))
def test_ack_nack(packet, cmd):
    topic = get_random_from(topics)
    pkg = packet(topic=topic, uid=UID, timestamp=TS, task_id=TASK_ID, config_hash='')

    assert pkg.payload.get('task_id') == TASK_ID, 'not assigned task id'


def test_base_datahold_packet():
    topic = get_random_from(topics)
    pkg = sp.DataholdPacket(topic=topic,
                            datahold=DATA,
                            timestamp=TS)

    assert pkg.payload.get('timestamp') == TS, 'timestamp not assigned'
    assert pkg.payload.get('datahold') == DATA, 'datahold not assigned'


@pytest.mark.parametrize(("packet", "cmd"), ((sp.INFO, "info"), (sp.SUP, "sup")))
def test_datahold_no_task_id(packet, cmd):
    topic = get_random_from(topics)
    pkg = packet(topic=topic,
                 datahold=DATA,
                 timestamp=TS,
                 uid=UID)

    assert pkg.command == cmd, 'bad command assigned'


@pytest.mark.parametrize(("packet", "cmd"), ((sp.INFO, "info"), (sp.SUP, "sup"), (sp.CUP, "cup")))
def test_datahold_with_task_id(packet, cmd):
    topic = get_random_from(topics)
    pkg = packet(topic=topic,
                 datahold=DATA,
                 timestamp=TS,
                 uid=UID,
                 task_id=TASK_ID)

    assert pkg.command == cmd, 'bad command assigned'
    assert pkg.payload.get('task_id') == TASK_ID, 'bad command assigned'
