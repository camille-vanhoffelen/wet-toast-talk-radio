import multiprocessing


class MockShout:
    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue
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
