import hashlib

from scheduler.constants import RANDOM_SEED_MOD


def deterministic_k(date_str: str, track: str) -> int:
    """
    Generate deterministic pseudo-random number using Bitcoin's RFC 6979 approach.
    Uses HMAC-SHA256 for deterministic randomness based on date and track.
    """
    # Create message from date and track
    message = f"{date_str}:{track}".encode("utf-8")

    # Use a fixed key for deterministic behavior across runs
    key = b"learning_scheduler_v1"

    # Use a fixed nonce for simplicity, can be adjusted
    nonce = 0
    combined = message + key + nonce.to_bytes(8, "big")

    # Generate deterministic k using HMAC-SHA256 chain
    k = b"\x01" * 32  # Initial k
    v = b"\x00" * 32  # Initial v

    # HMAC-SHA256 based deterministic generation (simplified RFC 6979)
    for n in range(5):  # Multiple rounds for better distribution
        # Update k
        h = hashlib.new("sha256")
        h.update(k + v + combined + n.to_bytes(1, "big"))
        k = h.digest()

        # Update v
        h = hashlib.new("sha256")
        h.update(k + v)
        v = h.digest()

    # Convert to integer and apply modulo
    return int.from_bytes(v, byteorder="big") % RANDOM_SEED_MOD
