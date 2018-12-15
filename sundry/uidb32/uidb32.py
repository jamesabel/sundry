
import sys
import uuid
import base64


def gen_uuid_b32():
    """
    Generate a new uuid b32 string
    :return: uuid b32 string
    """
    return uuid_to_b32(uuid.uuid4())


def uuid_hex_to_b32(hex_str):
    """
    Convert a UUID hex string to a b32 string
    :param hex_str:
    :return: b32 string
    """
    return uuid_to_b32(uuid.UUID(hex_str))


def uuid_to_b32(uuid_obj):
    """
    Convert UUID object to a b32 string
    :param uuid_obj: UUID object
    :return: b32 string
    """
    return base64.b32encode(uuid_obj.bytes).decode().replace('=', '').lower()


def b32_to_uuid(uuid_str_b32):
    """
    Convert a UUID b32 format string to a UUID object
    :param uuid_str_b32:
    :return: UUID object based on the passed b32 string
    """
    # pad (b32decode requires this)
    while len(uuid_str_b32) % 8 != 0:
        uuid_str_b32 += '='
    return uuid.UUID(base64.b32decode(uuid_str_b32, casefold=True).hex())


def uidb32():
    # CLI
    if len(sys.argv) < 2:
        # generate a new UUID b32
        print(gen_uuid_b32())
    else:
        arg_str = sys.argv[1]
        if ("-" in arg_str and len(arg_str) == 36) or len(arg_str) == 32:
            # passed in a UUID in hex format (with dashes)
            print(uuid_hex_to_b32(arg_str))
        elif len(arg_str) == 26:
            # Passed a uuid in b32 format.  Convert it to a UUID string.
            print(b32_to_uuid(sys.argv[1]))
        else:
            print(f"Error : {arg_str} is not a UUID or uuid_b32")


if __name__ == "__main__":
    uidb32()
