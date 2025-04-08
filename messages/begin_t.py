"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""


from io import BytesIO
import struct

class begin_t(object):
    """ Sent to nodes when the game begins. """

    __slots__ = []

    __typenames__ = []

    __dimensions__ = []

    def __init__(self):
        pass

    def encode(self):
        buf = BytesIO()
        buf.write(begin_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        pass

    @staticmethod
    def decode(data: bytes):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = BytesIO(data)
        if buf.read(8) != begin_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return begin_t._decode_one(buf)

    @staticmethod
    def _decode_one(buf):
        self = begin_t()
        return self

    @staticmethod
    def _get_hash_recursive(parents):
        if begin_t in parents: return 0
        tmphash = (0x12345678) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff) + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _packed_fingerprint = None

    @staticmethod
    def _get_packed_fingerprint():
        if begin_t._packed_fingerprint is None:
            begin_t._packed_fingerprint = struct.pack(">Q", begin_t._get_hash_recursive([]))
        return begin_t._packed_fingerprint

    def get_hash(self):
        """Get the LCM hash of the struct"""
        return struct.unpack(">Q", begin_t._get_packed_fingerprint())[0]

