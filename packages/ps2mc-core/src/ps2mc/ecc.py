class EccCalculator:
    """
    ECC checksum generator using Hamming code for 128-byte data blocks.
    """

    _PARITY_TABLE, _COLUMN_PARITY_MASKS = None, None

    @staticmethod
    def _parity(byte: int) -> int:
        """
        Calculate the parity (even or odd) of a byte.
        Returns 0 for even parity, 1 for odd.
        """
        byte ^= byte >> 1
        byte ^= byte >> 2
        byte ^= byte >> 4
        return byte & 1

    @classmethod
    def _init_tables(cls):
        """
        Initialize lookup tables for parity and column parity masks.
        This is done only once and reused across instances.
        """
        if cls._PARITY_TABLE is not None:
            return  # Already initialized

        parity_table = [cls._parity(b) for b in range(256)]
        cpmasks = [0x55, 0x33, 0x0F, 0x00, 0xAA, 0xCC, 0xF0]

        column_parity_masks = [0] * 256
        for b in range(256):
            mask = 0
            for i, cpm in enumerate(cpmasks):
                mask |= parity_table[b & cpm] << i
            column_parity_masks[b] = mask

        cls._PARITY_TABLE = parity_table
        cls._COLUMN_PARITY_MASKS = column_parity_masks

    def calc(self, data: bytes) -> bytes:
        """
        Compute the ECC for a 128-byte data block.

        Args:
            data (bytes): Input data, must be exactly 128 bytes long.

        Returns:
            bytes: 3 ECC bytes: column_parity, line_parity_0, line_parity_1
        """
        if len(data) != 128:
            raise ValueError("Data must be exactly 128 bytes")

        self._init_tables()

        cp = 0x77  # Column parity initial value
        lp0 = 0x7F  # Line parity 0 initial value
        lp1 = 0x7F  # Line parity 1 initial value

        for i, b in enumerate(data):
            cp ^= self._COLUMN_PARITY_MASKS[b]
            if self._PARITY_TABLE[b]:
                lp0 ^= ~i
                lp1 ^= i

        return bytes([cp, lp0 & 0x7F, lp1])
