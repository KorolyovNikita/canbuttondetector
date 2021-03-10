class BitMask:
    def __init__(self, mask=0xFF, width=8):
        self.mask = mask
        self.width = width

    def split(self):
        if self.width < 2:
            return
        shift = self.width // 2
        left = BitMask((self.mask << shift) & self.mask, shift)
        right = BitMask((self.mask >> shift) & self.mask, shift)

        return left, right

    def get(self):
        return self.mask
