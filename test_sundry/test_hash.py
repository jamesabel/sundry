import os

from sundry import get_string_md5, get_string_sha256, get_string_sha512, get_file_md5, get_file_sha256, get_file_sha512


def test_hash():
    file_path = os.path.join('test_sundry', 'a.txt')
    s = 'a'
    a_md5 = '0cc175b9c0f1b6a831c399e269772661'
    a_sha256 = 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
    a_sha512 = '1f40fc92da241694750979ee6cf582f2d5d7d28e18335de05abc54d0560e0f5302860c652bf08d560252aa5e74210546f369fbbbce8c12cfc7957b2652fe9a75'
    assert(get_string_md5(s) == a_md5)
    assert(get_string_sha256(s) == a_sha256)
    assert(get_string_sha512(s) == a_sha512)
    assert(get_file_md5(file_path) == a_md5)
    assert(get_file_sha256(file_path) == a_sha256)
    assert(get_file_sha512(file_path) == a_sha512)
