from bitstring import BitArray
from DataHandler import DataHandler
from Save import trimBinary
from Pieces import new

class Default(DataHandler):
    def __init__(self):
        super().__init__(0)
    def detect(self, board) -> bool:
        return True
    def encode(self, board) -> str:
        pieces = board.piecesOfType
        presenceMap = ""
        data = ""
        for key in range(12):
            if key % 6 == 5:
                if len(pieces[key]) != 1:
                    raise Exception("Must save only 1 king of each color on a board")
                data += trimBinary(pieces[key][0], 6)
                continue
            pieceCount = len(pieces[key])
            if pieceCount > 0:
                presenceMap += "1"
                if pieceCount > 15:
                    raise Exception("Cannot save more then 16 locations for one piece type")
                data += trimBinary(pieceCount, 4)
                for tileId in pieces[key]:
                    data += trimBinary(tileId, 6);
            else:
                presenceMap += "0"
        firstLetter = presenceMap[0]
        allTheSame = True
        for letter in presenceMap:
            allTheSame = allTheSame and (letter == firstLetter)

        if allTheSame:
            data = "1" + firstLetter + data
        else:
            data += "00" + data
        return data
    def decode(self, bits:BitArray, board):
        here = bits[0]
        fill = bits[1]
        bits = bits[2:]
        presenceMap = []
        if here:
            for i in range(12):
                presenceMap.append(fill == 1)
        elif fill:
            #00 case
            for i in range(10):
                if i == 5:
                    presenceMap.append(True)
                bit = bits[i]
                presenceMap.append(bit == 1)
            presenceMap.append(True)
            bits = bits[10:]
        else:
            raise RuntimeError("Default handler encountered non default handler flag")
        pieceId = 0

        while pieceId < 12:
            color = pieceId >= 6
            if pieceId % 6 != 5:
                #Non Kings
                if not presenceMap[pieceId]:
                    pieceId += 1
                    continue
                pieceCount = bits[0:4].uint
                bits = bits[4:]
                for i in range(pieceCount):
                    tileId = bits[0:6].uint
                    bits = bits[6:]
                    tar = (tileId // 8, tileId % 8)
                    piece = new(color,pieceId % 6)
                    piece.data = False
                    if pieceId % 6 == 0 and ((tar[0] == 1 and not color) or (tar[0] == 6 and color)):
                        piece.data = True

                    if pieceId % 6 == 1: #Piece is rook
                        piece.data = True #Must assume they have moved
                    board.setPiece(tar,piece)
            else:
                #Kings
                tileId = bits[0:6].uint
                bits = bits[6:]
                tar = (tileId // 8, tileId % 8)
                piece = new(color,pieceId % 6)
                piece.data = True #Must assume they have moved
                board.setPiece(tar,piece)
            pieceId += 1