from teleimager import image_client


CONFIG = {
    "head_camera": {"enable_zmq": True, "enable_webrtc": True, "zmq_port": 55555},
    "left_wrist_camera": {"enable_zmq": True, "enable_webrtc": False, "zmq_port": 55556},
    "right_wrist_camera": {"enable_zmq": True, "enable_webrtc": False, "zmq_port": 55557},
}


class FakeManager:
    def __init__(self):
        self.calls = []

    def subscribe(self, host, port, request_bgr=False):
        self.calls.append((host, port, request_bgr))


class FakeRequester:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def request(self):
        return CONFIG


def _make(monkeypatch, camera_names=None):
    manager = FakeManager()
    monkeypatch.setattr(
        image_client.ZMQ_SubscriberManager, "get_instance", lambda: manager
    )
    monkeypatch.setattr(image_client, "ZMQ_Requester", FakeRequester)
    client = image_client.ImageClient(
        host="camera-host", request_bgr=True, camera_names=camera_names
    )
    return client, manager


def test_selected_head_camera_does_not_subscribe_to_wrist_streams(monkeypatch):
    client, manager = _make(monkeypatch, camera_names=("head_camera",))
    assert manager.calls == [("camera-host", 55555, True)]
    try:
        client.get_left_wrist_frame()
    except RuntimeError as exc:
        assert "left_wrist_camera" in str(exc)
    else:
        raise AssertionError("an unselected wrist stream must not be requested")
    assert manager.calls == [("camera-host", 55555, True)]


def test_default_still_subscribes_to_every_enabled_camera(monkeypatch):
    _client, manager = _make(monkeypatch)
    assert manager.calls == [
        ("camera-host", 55555, True),
        ("camera-host", 55556, True),
        ("camera-host", 55557, True),
    ]


def test_unknown_selected_camera_fails_closed(monkeypatch):
    try:
        _make(monkeypatch, camera_names=("not_a_camera",))
    except ValueError as exc:
        assert "not_a_camera" in str(exc)
    else:
        raise AssertionError("unknown camera selection must fail")
