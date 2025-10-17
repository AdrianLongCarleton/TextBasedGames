import os
import importlib.util
from DataHandler import DataHandler
from Pieces import PieceType
from Pieces import new
from bitstring import BitArray
from typing import Tuple, List

def decodeMetaData(bits:BitArray):
    turn = bits[1] == 1
    enpasant = -1
    index = 3
    if bits[2] == 1: #Enpasant is possible
        enpasant = bits[3:7].uint
        index += 4
    castlingPossible = []
    for bit in bits[index:index + 4]:
        castlingPossible.append(bit == 1)
    index += 4
    return turn, enpasant, castlingPossible, bits[:index], bits[index:]

def registerSpecialMoves(enpassant:int,castlingPossible:List[bool],board:"Board"):
    if enpassant >= 0:
        row = 3
        col = enpassant
        if col > 7:
            col -= 8
            row = 4
        piece = board.getPiece((row,col))
        if piece != None and piece.pieceType == PieceType.PAWN:
            piece.data = True
    
    index = 0
    for i in [0,7]:
        for j in [0, 7]:
            canBePerformed = castlingPossible[index]
            index += 1
            tarMaybeRook = (i,j)
            tarMaybeKing = (i,4)
            maybeRook = board.getPiece(tarMaybeRook)
            maybeKing = board.getPiece(tarMaybeKing)
            if maybeRook == None or maybeKing == None:
                continue
            if canBePerformed and maybeRook.pieceType == PieceType.ROOK and maybeKing.pieceType == PieceType.KING:
                maybeRook.data = True
                maybeKing.data = True
                board.setPiece(tarMaybeRook,maybeRook)
                board.setPiece(tarMaybeKing,maybeKing)

def decodeFallBack(bits:BitArray,board:"Board"):
    if len(bits) != 256:
        raise Exception("Invalid piece data")
    chunks = [bits[i:i+4] for i in range(0,len(bits), 4)]
    for i in range(len(chunks)):
        tar = (i // 8, i % 8)
        color = chunks[i][0] == 1
        piece = new(color,chunks[i+1:].uint)
        piece.data = False
        if piece.pieceType.value == 0 and ((tar[0] == 1 and not color) or (tar[0] == 6 and color)):
            piece.data = True
        if piece.pieceType == PieceType.KING or piece.pieceType == PieceType.ROOK:
            piece.data = True #Must assume they have moved
        board.setPiece(tar,piece)

def toHex(binary):
    return hex(int(binary,2))[2:].upper()
def trimBinary(value,length):
    binary = bin(value)[2:].zfill(length)
    binary += "0" * length
    return binary[:length]

def getHandlerId(bits):
    flag = bits[0]
    handlerId = bits[1:3]
    if flag != 1:
        bits = bits[4:]
        return int(handlerId,2), bits
    handlerId = ""
    while flag == 1:
        flag = bits[0]
        handlerId += bits[1:7]
        bits = bits[8:]
    return int(handlerId,2), bits


class Save:
    def __init__(self, handler_dir="dataHandlers"):
        self.handlers = {}
        self.load_handlers(handler_dir)

    def load_handlers(self, handler_dir):
        for filename in os.listdir(handler_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                path = os.path.join(handler_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Find class inheriting from DataHandler
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, DataHandler) and obj is not DataHandler:
                        handler = obj()
                        hid = handler.handlerId
                        if hid in self.handlers:
                            raise RuntimeError(f"Handler id collision: {hid}")
                        self.handlers[hid] = handler

    def create(self, board) -> str:
        piecesOfType = [[], [], [], [], [], [],
                        [], [], [], [], [], []
                        ]
        enpassant = None
        for i in range(8):
            for j in range(8):
                piece = board.getPiece((i, j))
                if piece is None:
                    continue
                pieceId = piece.pieceType.value
                if piece.color:
                    pieceId += 6
                piecesOfType[pieceId].append(i * 8 + j)
                if pieceId == 0 and (i == 3 or i == 4) and piece.data:
                    if enpassant is not None:
                        raise Exception("Only one pawn can be capturable by enpassant at a time")
                    enpassant = j
                    if i == 3:
                        enpassant += 8
        board.piecesOfType = piecesOfType

        castlingPossible = [False for _ in range(4)]
        index = -1
        for i in [0, 7]:
            for j in [0, 7]:
                index += 1
                tarMaybeRook = (i, j)
                tarMaybeKing = (i, 4)
                maybeRook = board.getPiece(tarMaybeRook)
                maybeKing = board.getPiece(tarMaybeKing)
                if maybeRook is None or maybeKing is None:
                    continue
                if maybeRook.pieceType == PieceType.ROOK and maybeKing.pieceType == PieceType.KING and maybeRook.data and maybeKing.data:
                    castlingPossible[index] = True
        metaData = "1"
        metaData += "1" if board.turn else "0"
        if enpassant is None:
            metaData += "0"
        else:
            metaData += "1" + trimBinary(enpassant, 4)
        for validMove in castlingPossible:
            metaData += "1" if validMove else "0"

        data = ""

        detected = False
        for handler in self.handlers.values():
            if handler.handlerId == 0:
                continue
            if not handler.detect(board):
                continue
            detected = True
            data = handler.encode(board)
            break
        if not detected:
            raise RuntimeError("No handlers encoded the data.")
        if len(data) > 256:
            data = self.handlers[1].encode(board)

        return toHex(metaData + data)

    def load(self,position, board):
        position = "0b" + bin(int(position, 16))[2:]

        bits = BitArray(position)
        strategy = bits[0] == 0

        board.turn, enpassant, castlingPossible, metaData, bits = decodeMetaData(bits)

        if strategy:
            decodeFallBack(bits, board)
        else:
            if bits[0:1].bin == "01":
                bits = bits[2:]
                handlerId, bits = getHandlerId(bits)
            else:
                handlerId = 0
            print(handlerId)
            print(bits.bin)
            if handlerId not in self.handlers:
                raise RuntimeError(f"No handler with the id {handlerId}")
            self.handlers[handlerId].decode(bits,board)

        registerSpecialMoves(enpassant, castlingPossible, board)
        return toHex(position[2:])

