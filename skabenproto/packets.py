class BasePacket:
    """
        Base packet class
    """

    def __init__(self, dev_type, uid=None):
        self.payload = dict()  # data payload
        self.command = str()  # command, assign in child classes
        self.dev_type = dev_type  # group channel address

        # WARNING: uid here will be used for addressing.
        self.uid = uid  # personal channel address, optional
        self.ts = None  # timestamp will be assigned by encoder

    def __repr__(self):
        if self.uid:
            ident = '{}/{}'.format(self.dev_type, self.uid)
        else:
            ident = self.dev_type

        return '<{}> {}'.format(self.command, ident)

# ping packets


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type, uid=None):
        super().__init__(dev_type=dev_type,
                         uid=uid)
        self.command = 'PING'


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, dev_type, uid):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         )
        self.command = 'PONG'


class PINGLegacy(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type):
        super().__init__(dev_type=dev_type,
                         )
        self.command = '*/PING'

# service packets


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, dev_type, timeout, uid):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         )

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError('bad timeout value: %s' % timeout)
        self.command = 'WAIT'
        self.payload.update({'timeout': timeout})


class ACK(BasePacket):
    """
        Confirm operations on previous packet as successful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         )
        self.command = 'ACK'
        self.payload.update({'task_id': task_id})


class NACK(BasePacket):
    """
        Confirm operations on previous packet as unsuccessful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         )
        self.command = 'NACK'
        self.payload.update({'task_id': task_id})


# packets with payload


class PayloadPacket(BasePacket):
    """
        Loaded packet basic class.
    """

    payload = {}  # packet inner payload

    def __init__(self, dev_type, payload,  uid=None, task_id=None):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         )

        if task_id:
            self.payload.update({'task_id': task_id})
        if not isinstance(payload, dict):
            raise Exception(f'payload should be a dictionary, not a {type(payload)}')
        if not dev_type == 'dumb':
            self.payload.update(**payload)
        else:
            self.payload = payload


class INFO(PayloadPacket):
    """
        Multipurpose payload packet
    """
    def __init__(self, dev_type, payload, uid, task_id=None):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         )

        self.command = 'INFO'


class CUP(PayloadPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, dev_type, payload, task_id,  uid=None):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         )

        self.command = 'CUP'


class SUP(PayloadPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, dev_type, payload, uid, task_id=None):
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         )

        self.command = 'SUP'
