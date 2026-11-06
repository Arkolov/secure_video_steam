"""Student exercises for nonlinear stream-generator variants."""

from stream_cipher import LFSR_PERIOD_BITS, MAX_SEED, _next_bit

DEFAULT_GEFFE_SEEDS = (0xACE1, 0xBEEF, 0x1234)


def _validate(length: int, seeds: tuple[int, ...], offset: int) -> None:
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if any(not isinstance(seed, int) or not 1 <= seed <= MAX_SEED for seed in seeds):
        raise ValueError("every seed must be an integer from 1 to 65535")


def nlfsr_keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Generate bytes from an NLFSR with one nonlinear AND feedback term."""
    _validate(length, (seed,), offset)

    state = seed

    def next_bit():
        nonlocal state

        output_bit = state & 1
        feedback_bit = (
            ((state >> 0) & 1)
            ^ ((state >> 2) & 1)
            ^ ((state >> 3) & 1)
            ^ ((state >> 5) & 1)
            ^ (((state >> 1) & 1) & ((state >> 7) & 1))
        )

        state = (state >> 1) | (feedback_bit << 15)
        return output_bit

    for _ in range(offset * 8):
        next_bit()

    result = bytearray()

    for _ in range(length):
        byte = 0
        for _ in range(8):
            byte = (byte << 1) | next_bit()
        result.append(byte)

    return bytes(result)

def geffe_keystream(
    length: int,
    seeds: tuple[int, int, int] = DEFAULT_GEFFE_SEEDS,
    offset: int = 0,
) -> bytes:
    """Combine three LFSR output bits with the nonlinear Geffe function.

    If the three output bits are x, y, and z, emit
    (x AND y) XOR ((1 XOR x) AND z). Each component uses the base LFSR.
    """
    if len(seeds) != 3:
        raise ValueError("the Geffe generator needs exactly three seeds")
    _validate(length, seeds, offset)

    states = list(seeds)

    for _ in range(offset * 8):
        for i in range(3):
            _, states[i] = _next_bit(states[i])

    result = bytearray()

    for _ in range(length):
        byte = 0

        for _ in range(8):
            bits = []

            for i in range(3):
                output_bit, states[i] = _next_bit(states[i])
                bits.append(output_bit)

            x, y, z = bits
            output_bit = (x & y) ^ ((1 ^ x) & z)
            byte = (byte << 1) | output_bit

        result.append(byte)

    return bytes(result)
