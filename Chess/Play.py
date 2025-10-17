import sys
from typing import Tuple, List
from enum import Enum
from Board import Pieces as Board
import Pieces
from Save import Save
def main():
    save = Save()
    position = ""
    if len(sys.argv) != 2:
        position = "1BF820928B30D38F20072046208510C48C31CB3D35DB72E3F2E7E2EBD1EFC"
    else:
        position = sys.argv[1]
    board = Board()
    #Set up the chess position manually
    #board.setPiece((0, 0), Pieces.Rook(False))
    #board.setPiece((0, 1), Pieces.Knight(False))
    #board.setPiece((0, 2), Pieces.Bishop(False))
    #board.setPiece((0, 3), Pieces.Queen(False))
    #board.setPiece((0, 4), Pieces.King(False))
    #board.setPiece((0, 5), Pieces.Bishop(False))
    #board.setPiece((0, 6), Pieces.Knight(False))
    #board.setPiece((0, 7), Pieces.Rook(False))
    #board.setPiece((1, 0), Pieces.Pawn(False))
    #board.setPiece((1, 1), Pieces.Pawn(False))
    #board.setPiece((1, 2), Pieces.Pawn(False))
    #board.setPiece((1, 3), Pieces.Pawn(False))
    #board.setPiece((1, 4), Pieces.Pawn(False))
    #board.setPiece((1, 5), Pieces.Pawn(False))
    #board.setPiece((1, 6), Pieces.Pawn(False))
    #board.setPiece((1, 7), Pieces.Pawn(False))
    #board.setPiece((6, 0), Pieces.Pawn(True))
    #board.setPiece((6, 1), Pieces.Pawn(True))
    #board.setPiece((6, 2), Pieces.Pawn(True))
    #board.setPiece((6, 3), Pieces.Pawn(True))
    #board.setPiece((6, 4), Pieces.Pawn(True))
    #board.setPiece((6, 5), Pieces.Pawn(True))
    #board.setPiece((6, 6), Pieces.Pawn(True))
    #board.setPiece((6, 7), Pieces.Pawn(True))
    #board.setPiece((7, 0), Pieces.Rook(True))
    #board.setPiece((7, 1), Pieces.Knight(True))
    #board.setPiece((7, 2), Pieces.Bishop(True))
    #board.setPiece((7, 3), Pieces.Queen(True))
    #board.setPiece((7, 4), Pieces.King(True))
    #board.setPiece((7, 5), Pieces.Bishop(True))
    #board.setPiece((7, 6), Pieces.Knight(True))
    #board.setPiece((7, 7), Pieces.Rook(True))
    #01010000 00000001 00001000 00010001
    #00000000 00000000 00000000 00000000
    data = save.load(position,board)
    print(board)
    print(f"Loaded: {data}")
    data = save.create(board)
    print(f"Saved:  {data}")

if __name__ == "__main__":
    main()
