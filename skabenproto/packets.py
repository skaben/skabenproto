import time
from skabenproto.helpers import *

CURRENT = int(time.time())

class BasePacket:
    """
        Base packet class
    """

    payload = dict()  # packet payload
    dev_type = str()  # device type
    command = str()  # command

    def __init__(self, dev_type, ts=CURRENT, uid=None):
        self.command = str()  # command, assign in child classes
        self.ts = ts # timestamp on start, should be external if client
        self.dev_type = dev_type  # group channel address
        self.payload.update({'ts': ts})  # set basic payload

        # WARNING: uid here will be used for addressing.
        # for any other purposes, you should pass device name with 'data'
        self.uid = uid  # personal channel address, optional

    def __repr__(self):
        if self.uid:
            ident = '{}/{}'.format(self.dev_type, self.uid)
        else:
            ident = self.dev_type

        return '<{}>\t{}\t{}'.format(self.command, ident, self.ts)

# Packets!

class ACK(BasePacket):
    """
        Confirm operations on previous packet as successful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'ACK'
        self.payload.update({'task_id': task_id})


class NACK(BasePacket):
    """
        Confirm operations on previous packet as unsuccessful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'NACK'
        self.payload.update({'task_id': task_id})


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, dev_type, timeout, uid, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)

        if isinstance(timeout, float):
            timeout = int(timeout)

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError('bad timeout value: %s' % timeout)
        self.command = 'WAIT'
        self.payload.update({'timeout': timeout})


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type, uid=None, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         ts=ts,
                         uid=uid)
        self.command = 'PING'


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, dev_type, uid, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'PONG'
        self.ts = ts

# packets with payload

class PayloadPacket(BasePacket):
    """
        Loaded packet basic class.
    """

    payload = {} # packet inner payload

    def __init__(self, dev_type, payload, uid=None, ts=CURRENT, task_id=None):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)

        # wtf >
        if isinstance(payload, str):
            try:
                payload = pl_decode(payload)
            except:
                raise Exception('cannot decode %s' % payload)
        # / wtf

        if task_id:
            self.payload.update({'task_id': task_id})
        self.payload.update(**payload)


class INFO(PayloadPacket):
    """
        Multipurpose payload packet
    """
    def __init__(self, dev_type, payload, uid, ts, task_id=None):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         ts=ts)

        self.command = 'INFO'


class CUP(PayloadPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, dev_type, payload, task_id, uid=None, ts=CURRENT):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         ts=ts)

        self.command = 'CUP'


class SUP(PayloadPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, dev_type, payload, uid, ts=CURRENT, task_id=None):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         ts=ts)

        self.command = 'SUP'

