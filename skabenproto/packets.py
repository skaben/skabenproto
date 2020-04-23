import json


class BasePacket:
    """
        Base packet class
    """

    command = str()

    def __init__(self, topic, uid=None, timestamp=None):
        self.topic = "/".join([_ for _ in (topic, uid, self.command) if _ not in (None, "")])
        self.payload = {
            "timestamp": timestamp if timestamp else 0  # assign timestamp if provided
        }

    def encode(self):
        try:
            payload = json.dumps(self.payload).encode('utf-8')
            return tuple((self.topic, payload))
        except Exception:
            raise

    def __repr__(self):
        return f"{self.topic} {self.payload}"

# ping packets


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, topic, uid=None, timestamp=None):
        self.command = "PING"
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, topic, uid, timestamp):
        self.command = "PONG"
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)


class PINGLegacy(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, topic):
        self.command = "*/PING"
        super().__init__(topic=topic)

# service packets


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, topic, timeout, uid, timestamp):
        self.command = "WAIT"
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError(f"bad timeout value: {timeout}")
        self.payload.update({"timeout": timeout})


class ACK(BasePacket):
    """
        Confirm operations on previous packet as successful
        Should send ts of previous packet
    """
    def __init__(self, topic, task_id, uid, timestamp):
        self.command = "ACK"
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)
        self.payload.update({"task_id": task_id})


class NACK(BasePacket):
    """
        Confirm operations on previous packet as unsuccessful
        Should send ts of previous packet
    """
    def __init__(self, topic, task_id, uid, timestamp):
        self.command = "NACK"
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)
        self.payload.update({"task_id": task_id})


# packets with payload


class DataholdPacket(BasePacket):
    """
        Loaded packet basic class.
    """

    datahold = {}  # packet data load

    def __init__(self, topic, datahold, timestamp, uid=None, task_id=None):
        super().__init__(topic=topic,
                         uid=uid,
                         timestamp=timestamp)
        self.payload.update({"datahold": datahold})  # separated namespace
        if task_id:
            self.payload.update({"task_id": task_id})


class INFO(DataholdPacket):
    """
        Multipurpose payload packet
    """
    def __init__(self, topic, datahold, uid, timestamp, task_id=None):
        self.command = "INFO"
        super().__init__(topic=topic,
                         datahold=datahold,
                         timestamp=timestamp,
                         task_id=task_id,
                         uid=uid)


class SUP(DataholdPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, topic, datahold, uid, timestamp, task_id=None):
        self.command = "SUP"
        super().__init__(topic=topic,
                         datahold=datahold,
                         task_id=task_id,
                         uid=uid,
                         timestamp=timestamp)


class CUP(DataholdPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, topic, datahold, task_id, timestamp, uid=None):
        self.command = "CUP"
        super().__init__(topic=topic,
                         datahold=datahold,
                         task_id=task_id,
                         uid=uid,
                         timestamp=timestamp)
