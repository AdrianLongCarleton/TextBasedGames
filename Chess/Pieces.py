from enum import Enum
from typing import Tuple, List
import Board

class PieceType(Enum):
    PAWN = 0
    ROOK = 1
    KNIGHT = 2
    BISHOP = 3
    QUEEN = 4
    KING = 5

class Piece:
    def __init__(self, pieceType: PieceType, color: bool, data: bool):
        self.pieceType = pieceType
        self.color = color
        self.data = data

    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        return []
    def move(self, pos: Tuple[int,int], tar: Tuple[int,int,int], board: "Board.Pieces"):
        board.setPiece(tar,board.getPiece(pos))
        board.setPiece(pos,None)
    def update(self, pos: Tuple[int, int]):
        pass

    def __str__(self):
        color = "Black"
        if self.color:
            color = "White"
        return f"{color} {self.pieceType.name} {str(self.data)}"

    @staticmethod
    def walk(pos: Tuple[int, int], stp: Tuple[int, int], color: bool, board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        moves = []
        cur_x, cur_y = pos[0] + stp[0], pos[1] + stp[1]
        while board.inBounds((cur_x, cur_y)):
            piece = board.getPiece((cur_x, cur_y))
            if piece is None:
                moves.append((cur_x, cur_y, Board.MoveType.REGULAR))
            else:
                if board.isKing((cur_x,cur_y)):
                    break
                if piece.color != color:
                    moves.append((cur_x, cur_y, Board.MoveType.CAPTURE))
                break
            cur_x += stp[0]
            cur_y += stp[1]
        return moves

class Pawn(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.PAWN, color, True)
    
    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int,int]]:
        moves = []
        x, y = pos
        frwdDir = -1 if self.color else 1
        start_rank = 6 if self.color else 1

        # Move forward one
        tar = (x, y + frwdDir)
        if board.inBounds(tar) and board.getPiece(tar) is None:
            moves.append(tar)
            # Move forward two from starting position
            tar2 = (x, y + frwdDir * 2,Board.MoveType.REGULAR)
            if self.data and board.inBounds(tar2) and board.getPiece(tar2) is None:
                moves.append(tar2)

        # Captures & en passant
        for dx in [-1, 1]:
            cap = (x + dx, y + frwdDir)
            if board.inBounds(cap):
                target_piece = board.getPiece(cap)
                if target_piece is not None and target_piece.color != self.color and not board.isKing(cap):
                    moves.append((cap[0],cap[1],Board.MoveType.CAPTURE))
                    continue
                # En passant (simplified, assumes .data encodes eligibility)
                side = (x + dx, y)
                side_piece = board.getPiece(side)
                if (side_piece is not None and
                    side_piece.color != self.color and
                    side_piece.pieceType == PieceType.PAWN and
                    side_piece.data):
                    moves.append((cap[0],cap[1],Board.MoveType.SPECIAL)) #Negative one encodes enpasant capture
    
    def move(self, pos: Tuple[int,int], tar: Tuple[int,int,int], board: "Board.Pieces"):
        super().move(pos,tar,board)
        if tar[2] == Board.MoveType.SPECIAL:
            board.pieces[tar[0]][pos[1]] = None

    def update(self, pos: Tuple[int, int]):
        start_rank = 6 if self.color else 1
        if self.data and pos[1] != start_rank:
            self.data = False

class Rook(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.ROOK, color, False) #hasMoved = False

    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        moves = []
        moves += Piece.walk(pos, (-1, 0), self.color, board)
        moves += Piece.walk(pos, (1, 0),  self.color, board)
        moves += Piece.walk(pos, (0, -1), self.color, board)
        moves += Piece.walk(pos, (0, 1),  self.color, board)
        return moves

    def move(self, pos: Tuple[int,int], tar: Tuple[int,int,int], board: "Board.Pieces"):
        self.data = True #hasMoved = True
        super().move(pos,tar,board)

class Knight(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.KNIGHT, color, False)

    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        moves = []
        for dr in [-1,1]:
            for dc in [-1,1]:
                for mv in [(2,1),(1,2)]:
                    tar = (pos[0] + mv[0] * dr,pos[1] + mv[1] * dc,Board.MoveType.REGULAR)
                    if not board.inBounds(tar):
                        continue
                    piece = board.getPiece(tar)
                    if piece != None and piece.color == self.color or board.isKing(tar):
                        continue
                    moves.append(tar)
        return moves
class Bishop(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.BISHOP, color, False)
                    
    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int]]:
        moves = []

        for dr in [-1,1]:
            for dc in [-1,1]:
                moves += Piece.walk(pos, (dr, dc), self.color, board)
        return moves
class Queen(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.QUEEN, color, False)
    
    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        moves = []

        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == dc == 0:
                    continue
                moves += Piece.walk(pos, (dr, dc), self.color, board)
        return moves
class King(Piece):
    def __init__(self, color: bool):
        super().__init__(PieceType.KING, color, False) #hasMoved = False
        self.rookPos = {-1:0,1:7}
    def moves(self, pos: Tuple[int, int], board: "Board.Pieces") -> List[Tuple[int, int, int]]:
        moves = []
        
        #Regular moves
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == dc == 0:
                    continue
                tar = (pos[0] + dr,pos[1] + dc, Board.MoveType.REGULAR)
                if not board.inBounds((tar[0],tar[1])):
                    continue
                tarPiece = board.getPiece((tar[0],tar[1]))
                if tarPiece is not None:
                    if tarPiece.color != self.color:
                        tar = (tar[0],tar[1], Board.MoveType.CAPTURE)
                    else:
                        continue
                if board.distKing(not self.color,tar) < 2:
                    continue
                moves.append(tar)
        
        #Castling
        kingHasMoved = self.data
        if kingHasMoved:
            return moves
        for i in [-1,1]:
            kingAdjacentPiece = board.getPiece((pos[0],pos[1] + i))
            if not kingAdjacentPiece is None:
                continue
            piece         = board.getPiece((pos[0],self.rookPos[i]))
            pieceExists   = piece is not None
            pieceIsRook   = piece.pieceType == PieceType.ROOK 
            pieceHasMoved = piece.data
            if pieceExists and pieceIsRook and not pieceHasMoved:
                move = (pos[0],pos[1] + 2*i,Board.MoveType.SPECIAL)
                moves.append(move)
        return moves
    
    def move(self, pos: Tuple[int,int], tar: Tuple[int,int,int], board: "Board.Pieces"):
        if tar[2] == Board.MoveType.SPECIAL:
            vec = tar[1] - pos[1]
            if vec == 0:
                raise Exception("DIV 0")
            vec = vec // abs(vec)
            rookBgn = (pos[0],self.rookPos[vec])
            rookEnd = (tar[0],tar[1] - vec,NORMAL)
            rook = board.getPiece(rookBgn)
            if rookEnd in rook.moves(rookBgn,board):
                rook.move(rookBgn,rookEnd,board)
        self.data = True #hasMoved = True
        super().move(pos,tar,board)
        if self.color:
            board.whiteKine = tar
        else:
            board.blackKing = tar
    
def new(color:bool,pieceType:int):
    match pieceType:
        case 0:
            return Pawn(color)
        case 1:
            return Rook(color)
        case 2:
            return Knight(color)
        case 3:
            return Bishop(color)
        case 4:
            return Queen(color)
        case 5:
            return King(color)
        case _:
            raise Exception("Chess only has 6 pieces")

