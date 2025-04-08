"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""


from io import BytesIO
import struct

class gameover_t(object):
    """ Sent when the game finishes.  Asks the nodes to deallocate themselves. """

    __slots__ = []

    __typenames__ = []

    __dimensions__ = []

    def __init__(self):
        pass

    def encode(self):
        buf = BytesIO()
        buf.write(gameover_t._get_packed_fingerprint())
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
        if buf.read(8) != gameover_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return gameover_t._decode_one(buf)

    @staticmethod
    def _decode_one(buf):
        self = gameover_t()
        return self

    @staticmethod
    def _get_hash_recursive(parents):
        if gameover_t in parents: return 0
        tmphash = (0x12345678) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff) + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _packed_fingerprint = None

    @staticmethod
    def _get_packed_fingerprint():
        if gameover_t._packed_fingerprint is None:
            gameover_t._packed_fingerprint = struct.pack(">Q", gameover_t._get_hash_recursive([]))
        return gameover_t._packed_fingerprint

    def get_hash(self):
        """Get the LCM hash of the struct"""
        return struct.unpack(">Q", gameover_t._get_packed_fingerprint())[0]

