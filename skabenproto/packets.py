class BasePacket:
    """
        Base packet class
    """

    command = str()

    def __init__(self, dev_type, uid=None, timestamp=None):
        self.topic = self.dev_type if not uid else f"{dev_type}/{uid}"  # assign mqtt topic
        self.timestamp = timestamp if timestamp else 0  # assign timestamp if provided
        self.content = {
            'command': self.command,
            'timestamp': self.timestamp,
        }

    def __repr__(self):
        return f"{self.topic} {self.data}"

# ping packets


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type, uid=None, timestamp=None):
        self.command = 'PING'
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, dev_type, uid, timestamp):
        self.command = 'PONG'
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)


class PINGLegacy(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type):
        self.command = '*/PING'
        super().__init__(dev_type=dev_type)

# service packets


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, dev_type, timeout, uid, timestamp):
        self.command = 'WAIT'
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError('bad timeout value: %s' % timeout)
        self.content.update({'timeout': timeout})


class ACK(BasePacket):
    """
        Confirm operations on previous packet as successful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid, timestamp):
        self.command = 'ACK'
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)
        self.content.update({'task_id': task_id})


class NACK(BasePacket):
    """
        Confirm operations on previous packet as unsuccessful
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid, timestamp):
        self.command = 'NACK'
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)
        self.content.update({'task_id': task_id})


# packets with payload


class PayloadPacket(BasePacket):
    """
        Loaded packet basic class.
    """

    payload = {}  # packet inner payload

    def __init__(self, dev_type, payload, timestamp, uid=None, task_id=None):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         timestamp=timestamp)
        self.content.update({'payload': payload})  # separated namespace


class INFO(PayloadPacket):
    """
        Multipurpose payload packet
    """
    def __init__(self, dev_type, payload, uid, timestamp, task_id=None):
        self.command = 'INFO'
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         timestamp=timestamp,
                         task_id=task_id,
                         uid=uid)


class CUP(PayloadPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, dev_type, payload, task_id, timestamp, uid=None):
        self.command = 'CUP'
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         timestamp=timestamp)


class SUP(PayloadPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, dev_type, payload, uid, timestamp, task_id=None):
        self.command = 'SUP'
        super().__init__(dev_type=dev_type,
                         payload=payload,
                         task_id=task_id,
                         uid=uid,
                         timestamp=timestamp)
