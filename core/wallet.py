import hashlib, hmac, os, secrets

class AGIOWallet:
    def __init__(self, sk_hex=None):
        self._sk = bytes.fromhex(sk_hex.strip()) if sk_hex else secrets.token_bytes(32)
        h = hashlib.sha256(self._sk).digest()
        self.address = "AG1" + h.hex()[:37]
    def sk_hex(self): return self._sk.hex()
    def sign(self, msg): return hmac.new(self._sk, msg.encode(), hashlib.sha256).hexdigest()
    def verify(self, msg, sig): return hmac.compare_digest(self.sign(msg), sig)
    def to_dict(self): return {"address": self.address, "sk_hex": self.sk_hex()}
    @classmethod
    def generate(cls): return cls()
