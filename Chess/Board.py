import sys
from enum import Enum
from typing import Tuple, List
import colorama
from Pieces import *


colorama.init()

class MoveType(Enum):
    SPECIAL = 0
    REGULAR = 1
    CAPTURE = 2

class Pieces:
    #Which way is forward is currently unsuported

        
    def __init__(self):
        # 8x8 grid, initialized to None
        
        self.sprites = [["    ▄▄    ","   ▄██▄   ","  ▀▀██▀▀  ","    ██    ","  ▄████▄  "], #Pawn
                        ["  ▄ ▄▄ ▄  ","  ██████  ","   ████   ","   ████   ","  ▄████▄  "], #Rook
                        ["    ▄▄    ","  ▀██▀█▄  ","  ████▄▀  ","   ▀██    ","  ▄████▄  "], #Knight
                        ["    ▄▄    ","   ▀██▀   ","  ▀▀██▀▀  ","   ▄██▄   ","  ▄████▄  "], #Bishop
                        ["  ▄ ▄▄ ▄  ","   ████   ","   ▄██▄   ","  █ ██ █  ","  ▄████▄  "], #Queen
                        ["    ▄▄    ","   ▀██▀   ","   ▄██▄   ","  █ ██ █  ","  ▄████▄  "]  #King
                        ]
        self.turn = True
        self.enpasant:Tuple[int,int] = None
        self.pieces = [[None for _ in range(8)] for _ in range(8)]
        self.piecesOfType = []
        self.whiteKing = (7,4)
        self.blackKing = (0,4)
        self.pieceOfInterest = (0,6)
        
            
        
    def isKing(self, pos: Tuple[int,int]) -> bool:
        return pos == self.whiteKing or pos == self.blackKing
        
    def getPiece(self, pos: Tuple[int, int]):
        return self.pieces[pos[0]][pos[1]]

    def setPiece(self, pos: Tuple[int,int], piece : "Piece"):
        self.pieces[pos[0]][pos[1]] = piece

    def distKing(self,color:bool,pos: Tuple[int,int]) -> float:
        king = self.blackKing
        if color:
            king = self.whiteKing
        #return the magnitude of the vector pos to king
        return ((king[0] - pos[0]) ** 2 + (king[1] - pos[1]) ** 2)**(1/2)


    def inBounds(self, pos: Tuple[int, int]):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def __str__(self):
        #return str(self.pieces)
        outputLines = ""
        validMoves = []
        if self.pieceOfInterest != None:
            piece = self.getPiece(self.pieceOfInterest)
            if piece!= None:
                for move in piece.moves(self.pieceOfInterest,self):
                    validMoves.append((move[0],move[1]))

        print(validMoves)
        for i in range(8):
            outputRow = ["","","","",""]
            for j in range(8):
                piece = self.pieces[i][j]
                #Set the color
                color = (i + j) % 2 == 0
                if (i,j) in validMoves:
                    for line in range(5):
                        outputRow[line] += colorama.Back.BLUE
                elif color:
                    for line in range(5):
                        outputRow[line] += colorama.Back.YELLOW
                else:
                    for line in range(5):
                        outputRow[line] += colorama.Back.GREEN
                #Draw the piece
                if piece == None:
                    for line in range(5):
                        outputRow[line] += " "*10
                else:
                    spriteId = piece.pieceType.value
                    if not piece.color:
                        for line in range(5):
                            outputRow[line] += colorama.Fore.BLACK
                    #if piece.data:
                        #for line in range(5):
                        #    outputRow[line] += colorama.Fore.RED
                    for line in range(5):
                        outputRow[line] += self.sprites[spriteId][line]

                #Reset the color
                for line in range(5):
                    outputRow[line] += colorama.Style.RESET_ALL

            for line in outputRow:
                outputLines += line + "\n"
        return outputLines

                

