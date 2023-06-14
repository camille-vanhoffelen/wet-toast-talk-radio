import multiprocessing


class MockShout:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        pass

    def open(self):  # noqa: A003
        pass

    def get_connected(self):
        pass

    def set_metadata(self, metadata: dict):
        pass

    def send(self, chunk: bytes):
        self.queue.put(chunk)

    def sync(self):
        pass

    def close(self):
        pass
