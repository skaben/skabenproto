import pytest

@pytest.fixture(autouse=True)
def fake_mqtt():
    """

    :param message: (tpoic, payload)
    :return: mqtt-like object
    """
    class FakeMsg:

        def __init__(self, msg_tuple):
            self.topic = msg_tuple[0]
            self.payload = bytes(msg_tuple[1], 'utf-8')

        def __enter__(self):
            return self

        def __exit__(self, *err):
            return

        def __repr__(self):
            return f'<FakeMsg> {self.topic} {self.payload}'

    def fake(message):
        return FakeMsg(message)

    return fake
