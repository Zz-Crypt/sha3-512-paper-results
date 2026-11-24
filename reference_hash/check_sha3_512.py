"""Compare the paper's full-round SHA3-512 implementation with hashlib (Section VII-C)."""

import hashlib


LANE_MASK = (1 << 64) - 1
RATE_BYTES = 72
ROTATION = (
    (0, 1, 62, 28, 27),
    (36, 44, 6, 55, 20),
    (3, 10, 43, 25, 39),
    (41, 45, 15, 21, 8),
    (18, 2, 61, 56, 14),
)
ROUND_CONSTANTS = (
    0x1, 0x8082, 0x800000000000808A, 0x8000000080008000,
    0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
    0x8A, 0x88, 0x80008009, 0x8000000A,
    0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x80000001, 0x8000000080008008,
)
REFERENCE_LENGTHS = (0, 1, 3, 7, 31, 64, 70, 71, 72, 73, 143, 144, 145, 200)


def _rotate_left(value, shift):
    return ((value << shift) | (value >> (64 - shift))) & LANE_MASK


def _permute(state):
    for constant in ROUND_CONSTANTS:
        parity = [0] * 5
        for y in range(5):
            for x in range(5):
                parity[x] ^= state[x + 5 * y]
        correction = [
            parity[(x - 1) % 5] ^ _rotate_left(parity[(x + 1) % 5], 1)
            for x in range(5)
        ]
        rotated = [0] * 25
        for y in range(5):
            for x in range(5):
                lane = state[x + 5 * y] ^ correction[x]
                rotated[y + 5 * ((2 * x + 3 * y) % 5)] = _rotate_left(lane, ROTATION[y][x])
        for y in range(5):
            row = rotated[5 * y : 5 * y + 5]
            for x in range(5):
                state[x + 5 * y] = row[x] ^ (~row[(x + 1) % 5] & row[(x + 2) % 5])
        state[0] ^= constant


def sha3_512_digest(message):
    """Return the standard 64-byte SHA3-512 digest of a byte string."""
    padding_length = RATE_BYTES - len(message) % RATE_BYTES
    if padding_length == 1:
        padding = b"\x86"
    else:
        padding = b"\x06" + bytes(padding_length - 2) + b"\x80"
    padded = message + padding
    state = [0] * 25
    for start in range(0, len(padded), RATE_BYTES):
        for lane in range(RATE_BYTES // 8):
            offset = start + 8 * lane
            state[lane] ^= int.from_bytes(padded[offset : offset + 8], "little")
        _permute(state)
    return b"".join(lane.to_bytes(8, "little") for lane in state[:8])


def main():
    for size in REFERENCE_LENGTHS:
        message = bytes((29 * i + size) % 256 for i in range(size))
        if sha3_512_digest(message) != hashlib.sha3_512(message).digest():
            raise SystemExit(f"SHA3-512 mismatch for the {size}-byte reference message")
    print(f"SHA3-512: {len(REFERENCE_LENGTHS)}/{len(REFERENCE_LENGTHS)} reference digests match hashlib.")


if __name__ == "__main__":
    main()
