import uuid

from sundry import gen_uuid_b32, uuid_hex_to_b32, uuid_to_b32, b32_to_uuid


def test_uid_b23():

    assert(len(gen_uuid_b32()) > 0)
    tst_uuid = uuid.uuid4()
    tst_uuid_str = str(tst_uuid)
    value_b32 = uuid_hex_to_b32(tst_uuid_str)
    value_b32_str = uuid_to_b32(tst_uuid)
    assert(value_b32 == value_b32_str)
    value_uuid = str(b32_to_uuid(value_b32))
    assert(value_uuid == tst_uuid_str)
    assert(len(value_b32) == 26)
    assert(len(value_uuid) == 36)
