from bitstring import BitArray
from DataHandler import DataHandler
from Save import trimBinary
from Pieces import new

class Symetry(DataHandler):
    def __init__(self):
        super().__init__(2)
        self.horzReflect = True
        self.vertReflect = True
        self.detected = False
    def detect(self, board) -> bool:
        return False
        self.detected = True
        self.horzReflect = True
        self.vertReflect = True
        for pieceId in board.piecesOfType:
            positions = board.piecesOfType[pieceId]
            for pos in positions:
                oppositeRow = (7 - pos[0], pos[1])
                oppositeCol = (pos[0], 7 - pos[1])
                color = pieceId // 6 == 1
                pieceType = pieceId % 6
                piece = board.getPiece(oppositeRow)
                if piece.color != color or piece.pieceType != pieceType:
                    self.vertReflect = False
                piece = board.getPiece(oppositeCol)
                if piece.color != color or piece.pieceType != pieceType:
                    horzReflect = False
                if not self.horzReflect and not self.vertReflect:
                    break
            if not self.horzReflect and not self.vertReflect:
                break
        return self.horzReflect or self.vertReflect

    def encode(self, board) -> str:
        if not self.detected:
            raise Exception("Cannot encode if detection wasn't attempted")
        horzReflectRange = 4
        vertReflectRange = 4
        if self.vertReflect and not self.horzReflect:
            horzReflectRange = 8
        elif self.horzReflect and not self.vertReflect:
            vertReflectRange = 8
        #elif not self.vertReflect
        pass

    def decode(self, bits: BitArray, board):
        pass
