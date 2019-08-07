import pytest

import skabenproto.contexts as contexts

from skabenproto.tests.mocks import dev_types, TS, UID, TASK_ID
from skabenproto.tests.mocks import get_random_from

# sanity tests

@pytest.mark.parametrize('cmd', ('PING', ))
def test_sanity_ping(cmd):
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           uid=UID)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res


@pytest.mark.parametrize('cmd', ('ACK', ))
def test_sanity_ack(cmd):
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           task_id=TASK_ID,
                           dev_type=dev_type,
                           uid=UID)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res


@pytest.mark.parametrize('cmd', ('CUP', 'SUP', 'INFO'))
def test_sanity_payload(cmd):
    sanity_payload = {'data': 'data'}
    dev_type = get_random_from(dev_types)
    with contexts.PacketEncoder() as encoder:
        res = encoder.load(packet_type=cmd,
                           dev_type=dev_type,
                           task_id=TASK_ID,
                           payload=sanity_payload,
                           uid=UID)
        assert isinstance(res, contexts.CMD.get(cmd)), res
        assert isinstance(encoder.encode(res), tuple), res
        # and here goes task_id
        sanity_payload.update({'task_id': TASK_ID})
        assert res.payload == sanity_payload, res
