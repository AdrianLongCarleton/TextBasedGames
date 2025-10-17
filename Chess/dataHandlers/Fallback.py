from bitstring import BitArray
from DataHandler import DataHandler
from Save import trimBinary
from Pieces import new

class Fallback(DataHandler):
    def __init__(self):
        super().__init__(1)
    def detect(self, board) -> bool:
        return False
    def encode(self, board) -> str:
        data = ""
        for i in range(8):
            for j in range(8):
                piece = board.pieceAt((i,j))
                if piece is None:
                    data += "0111"
                data += "1" if piece.color else "0"
                data += trimBinary(piece.pieceType.value + 1, 3)
    def decode(self, bits:BitArray, board):
        if len(bits) != 256:
            raise Exception("Invalid piece data")
        chunks = [bits[i:i + 4] for i in range(0, len(bits), 4)]
        for i in range(len(chunks)):
            tar = (i // 8, i % 8)
            pieceId = chunks[i + 1:].uint
            if pieceId > 5:
                continue
            color = chunks[i][0] == 1
            piece = new(color, pieceId)
            piece.data = False

            if pieceId  == 0 and ((tar[0] == 1 and not color) or (tar[0] == 6 and color)):
                piece.data = True

            if pieceId == 1 or pieceId == 5:  # Piece is rook
                piece.data = True  # Must assume they have moved
            board.setPiece(tar,piece)

