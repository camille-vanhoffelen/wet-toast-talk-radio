from datetime import datetime

import pytest

from media_store.virtual.bucket import ShowType, VirtualBucket
from media_store.virtual.media_store import VirtualObject


@pytest.fixture()
def virtual_bucket() -> VirtualBucket:
    return VirtualBucket()


@pytest.fixture(autouse=True)
def _reset():
    virtual_bucket = VirtualBucket()
    virtual_bucket.reset()


class TestVirtulBucket:
    def test_singleton(self):
        vb1 = VirtualBucket()
        vb2 = VirtualBucket()
        assert vb1 is vb2

        vb1["foo"] = VirtualObject("bar", b"baz", datetime.now(), ShowType.RAW)
        assert vb2 == vb1

    def test_singleton_fixture(self, virtual_bucket: VirtualBucket):
        vb2 = VirtualBucket()
        assert virtual_bucket is vb2

        vb2["foo2"] = VirtualObject("bar2", b"baz", datetime.now(), ShowType.RAW)
        assert vb2 == virtual_bucket
        assert "foo" not in virtual_bucket.keys()
