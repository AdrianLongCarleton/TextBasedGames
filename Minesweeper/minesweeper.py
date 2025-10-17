import os
import sys
import random
import numpy as np
from typing import Tuple
import colorama
from math import floor
import time
from collections import deque

colorama.init()
size = 0 
percentMines = 0.0 
try:
    if len(sys.argv) != 3:
        raise Exception()
    size = int(sys.argv[1])
    percentMines = int(sys.argv[2]) / 100.0
    if not 0.01 <= percentMines <= 1:
        raise Exception()
except (ValueError, TypeError, Exception):
    print("input must be in the format minesweeper.py <size:int> <percentMines:int; 1 to 100 inclusive>")
    sys.exit()
titleScreen = ""
revealed = 0
safe = 0
board = np.full((size, size), 0)
vsble = np.full((size, size), 0) #[-1:"revealed",0:"unknown",1:"flagged",2:"cursor"]
offsets = [[-1, -1], [-1, 0], [-1, 1],
           [ 0, -1],          [ 0, 1],
           [ 1, -1], [ 1, 0], [ 1, 1]]

symbols = ["_|",f"{colorama.Back.YELLOW} F{colorama.Style.RESET_ALL}","XX",f"{colorama.Back.GREEN}  {colorama.Style.RESET_ALL}",f"{colorama.Back.GREEN}  {colorama.Style.RESET_ALL}",f"{colorama.Back.GREEN} F{colorama.Style.RESET_ALL}"]
revDir = {"w":"s","a":"d","s":"w","d":"a"}

def to_base26_letters(n: int) -> str:
    if n < 0:
        raise ValueError("Negative numbers not supported.")
    result = []
    while n >= 26:
        result.append(chr(ord('a') + (n % 26) - 1))
        n //= 26
    result.append(chr(ord('a') + n - 1))
    result[0] = chr(ord(result[0]) + 1)
    return ''.join(result).upper()[::-1]

def to_base10_number(s: str) -> int:
    n:int = 0
    s = s.lower()
    chrs = list(s)
    sLen = len(s)
    a = ord('a') - 1
    for i in range(len(chrs)):
        j = sLen - i - 1
        v = ord(chrs[i]) - a
        n += v * 26**j
    return n - 1


def onBoard(pos:Tuple[int, int]) -> bool:
    return 0 <= pos[0] < size and 0 <= pos[1] < size

def initBoard(mines:int,move:Tuple[int,int,int]):
    forbiden = {(move[0],move[1])}
    for offset in offsets:
        forbiden.add((move[0] + offset[0],move[1] + offset[1]))

    adjWalls = 0
    if move[0] == 0 or move[0] == (size - 1):
        adjWalls += 1
    if move[1] == 0 or move[1] == (size - 1):
        adjWalls += 1

    result = 0
    match adjWalls:
        case 0:
            result = 9
        case 1:
            result = 6
        case 2:
            result = 4
    
    cells = size**2 - result
    for row in range(size):
        for col in range(size):
            if (row,col) in forbiden:
                continue
            if random.randint(1,cells) <= mines:
                mines -= 1
                board[row][col] = -1
                
                for offset in offsets:
                    offsetPosition = (row + offset[0], col + offset[1])
                    if not onBoard(offsetPosition):
                        continue
                    if board[offsetPosition[0]][offsetPosition[1]] != -1:
                        board[offsetPosition[0]][offsetPosition[1]] += 1
            cells -= 1

def printBoard():
    rightPad = len(str(size + 1))

    horizLable = [] 
    horizPad = len(to_base26_letters(size))
    for i in range(size):
        horizLable.append(list(f"{to_base26_letters(i):>{horizPad}}"))
    for i in range(horizPad):
        outputLine = colorama.Back.LIGHTBLACK_EX + " " * rightPad + colorama.Style.RESET_ALL
        for j in range(len(horizLable)):
            outputLine += f"{colorama.Back.LIGHTBLACK_EX} {horizLable[j][i]}{colorama.Style.RESET_ALL}"
        print(outputLine)
        
    for i in range(size):
        outputLine = ""
        for j in range(size): 
            if j == 0:
                outputLine += f"{colorama.Back.LIGHTBLACK_EX}{i + 1:>{rightPad}}{colorama.Style.RESET_ALL}"
            override = ""
            decoded = vsble[i][j]
            if decoded >= 2:
                override = colorama.Back.GREEN
                decoded -= 3
            if decoded != -1:
                #Print a cell that a user has not revealed.
                #Can be an unknown tile, or a flag
                try:
                    outputLine += symbols[vsble[i][j]] 
                except IndexError:
                    outputLine += f"INDEX ERROR: {vsble[i][j]}"
                    print(f"INDEX ERRPR: {vsble[i][j]}")
                continue
            cell = board[i][j]
            if cell < 0:
                #Print a bomb
                outputLine += f"{colorama.Back.RED} B{colorama.Style.RESET_ALL}"
                continue
            if cell == 0:
                #Print an empty cell
                outputLine += f"{colorama.Back.WHITE}{override}  {colorama.Style.RESET_ALL}"
                continue
            #Print a cell with a number in it
            outputLine += f"{colorama.Back.BLUE}{override} {cell}{colorama.Style.RESET_ALL}"
        
        print(outputLine)

def parseInput(visualMode:bool) -> Tuple[int, int, int]:
    inputText = ""
    moveType = 0 #Selection
    while True:
        inputText = input("What is your move? ")

        try:
            array = inputText.split(" ")
            if not 1 <= len(array) <= 3:
                raise Exception()
            for part in array:
                if len(part) == 0:
                    raise Exception()
            if len(array) == 1:
                symbol = array[0][0].lower()
                if symbol == "q":
                    return -1, -1, 2 #Quit
                elif symbol == "v":
                    return size // 2, size // 2, 3 #Start visual mode at the center
                elif symbol == "c":
                    if os.name == 'nt':
                        os.system('cls')
                    else:
                        os.system('clear')
                    printBoard()
                    continue
                elif symbol == "h":
                    print(titleScreen)
                    printBoard()
                    continue
                elif symbol == "r":
                    return -1, -1, 5
                    
            if visualMode:
                symbol = array[0][0]
                numActions = 1
                if len(array) > 1:
                    numActions = int(array[1])
                if numActions == 0:
                    continue
                if numActions < 0:
                    numActions = abs(numActions)
                    symbol = revDir[symbol]
                match symbol:
                    case "e":
                        return 1, 0, 4 #Cursor action -> Enter
                    case "f":
                        return 1, 1, 4 #Cursor action -> Flag
                    case "w":
                        return numActions, 2, 4 #Cursor action -> Up
                    case "a":
                        return numActions, 3, 4 #Cursor action -> Left
                    case "s":
                        return numActions, 4, 4 #Cursor action -> Down
                    case "d":
                        return numActions, 5, 4 #Cursor action -> Right
                    case "m": 
                        return 1, 6, 4           #Cursor action -> Multi Select
                raise Exception()

            posCol = to_base10_number(array[0])
            posRow = int(array[1]) - 1
            if posRow < 0:
                raise Exception()
            if len(array) == 3:
                keyword = array[2].lower()
                if keyword[0] == "f":
                    moveType = 1 #Flag
                elif keyword[0] == "v":
                    moveType = 3 #Cursor select
            if not onBoard((posRow,posCol)):
                raise Exception()
            break
        except:
            if not visualMode:
                print("Input must be in the form \"<letterCordinate:str> <numberCordinate:int> [{f[lag], v[isual]}]\"\nor \"{q[uit], v[isual], c[lear | ls]}}\"")
            else:
                print("Input must be in the form \"{e[nter], f[lag], m[ark], w #up#, a #left#, s #down#, d #right#} [<repetitions:int>] \"")
    return posRow, posCol, moveType
    
def reveal(pos:Tuple[int,int,int]) -> bool:
    if not onBoard(pos):
        #return if out of bounds or allready revealed
        return False
    if vsble[pos[0]][pos[1]] == -1: #The cell is revealed
        if pos[2] == 2:
            return False #Don't recursivly reveal the board
        #Clicking a visible cell, if the count of neighboring flags equals this cells value
        #Reveal all the non flag cells around the current cells.
        flags = 0
        targets = set()
        for offset in offsets:
            offsetPosition = (pos[0] + offset[0],pos[1] + offset[1], 2)
            if not onBoard(offsetPosition):
                continue
            if vsble[offsetPosition[0]][offsetPosition[1]] == 1:
                flags += 1
                continue
            targets.add(offsetPosition)
        result = False
        if flags == board[pos[0]][pos[1]]:
            for target in targets:
                result |= reveal(target) 
        return result
    if pos[2] == 1:
        #the user want's to place a flag
        vsble[pos[0]][pos[1]] = 1
        return False
    if vsble[pos[0]][pos[1]] == 1:
        #the user want's to remove a flag
        vsble[pos[0]][pos[1]] = 0
        return False
    global revealed
    revealed += 1
    #vsble[pos[0]][pos[1]] += 3
    #printBoard()
    #time.sleep(0.0125)
    vsble[pos[0]][pos[1]] = -1
    cell = board[pos[0]][pos[1]]
    if cell == -1:
        return True
    if cell == 0:
        if pos[2] == 2:
            return False
        skipChart = [7,6,5,
                     4,  3,
                     2,1,0]
        startTime = time.time()
        queue = set()
        for offset in offsets:
            temp = (pos[0] + offset[0],pos[1] + offset[1],2)
            if not onBoard(temp) or vsble[temp[0]][temp[1]] == -1:
                continue
            queue.add(temp)
        while len(queue) > 0:
            tar = queue.pop()
            reveal(tar)
            if board[tar[0]][tar[1]] == 0:
                for offset in offsets:
                    temp = (tar[0] + offset[0],tar[1] + offset[1],2)
                    if not onBoard(temp) or vsble[temp[0]][temp[1]] == -1:
                        continue
                    queue.add(temp)
    return False 
    
def startGame(mines):
    first = True    
    cursorMode = False
    curRow = 0
    curCol = 0
    vsbleState = 0
    multiSelect = {}
    while revealed < safe:
        lost = False
        printBoard()
        move = parseInput(cursorMode)
        if move[2] == 2:
            break
        if move[2] == 5:
            rndRow = 0
            rndCol = 0
            while True:
                rndRow = random.randint(0,size - 1)
                rndCol = random.randint(0,size - 1)
                if vsble[rndRow][rndCol] == 0:
                    break
            move = (rndRow,rndCol,0)
        if first and move[2] != 1:
            first = False
            initBoard(mines,move)
        if not cursorMode and move[2] == 3:
            cursorMode = True
            vsbleState = vsble[move[0]][move[1]]
            #-1 -> revealed
            #0 -> unknown
            #1 -> flag
            #+3
            #-1 -> 2
            # 0 -> 2
            # 1 -> 4
            vsble[move[0]][move[1]] += 3
            curRow = move[0]
            curCol = move[1]
        if move[2] == 4:
            if not cursorMode:
                continue
            vsble[curRow][curCol] = vsbleState
            match move[1]:
                case 0: #Exit and select
                    cursorMode = False
                    move = (curRow,curCol,0)
                    curRow = 0
                    curCol = 0
                case 1: #Exit and flag
                    cursorMode = False
                    move = (curRow,curCol,1)
                    curRow = 0
                    curCol = 0
                case 2: #Move cursor up
                    for i in range(move[0]):
                        curRow -= 1
                    curRow = max(0,curRow)
                    vsbleState = vsble[curRow][curCol]
                case 3: #Move cursor left
                    for i in range(move[0]):
                        curCol -= 1
                    curCol = max(0,curCol)
                    vsbleState = vsble[curRow][curCol]
                case 4: #Move cursor down
                    for i in range(move[0]):
                        curRow += 1
                    curRow = min(size - 1,curRow)
                    vsbleState = vsble[curRow][curCol]
                case 5: #Move cursor right
                    for i in range(move[0]):
                        curCol += 1
                    curY = min(size - 1,curCol)
                    vsbleState = vsble[curRow][curCol]
                case 6: #Add a new cursor
                    temp = None
                    key = (curRow,curCol)
                    if key in multiSelect:
                        temp = multiSelect[key]
                    if temp != None:
                        vsble[curRow][curCol] = temp
                        multiSelect.pop(key)
                        vsbleState = temp
                    else:
                        multiSelect[key] = vsbleState
                        if vsble[curRow][curCol] >= 2:
                            vsble[curRow][curCol] -= 3
                        vsbleState = vsble[curRow][curCol] + 3 
            if cursorMode:
                if vsble[curRow][curCol] >= 2:
                    vsble[curRow][curCol] -= 3
                vsble[curRow][curCol] += 3
            else:
                for key in multiSelect:
                    vsble[key[0]][key[1]] = multiSelect[key]
                    lost |= reveal((key[0],key[1],move[2]))
                multiSelect = {}
        
        if cursorMode:
            continue
        if reveal(move) or lost:
            break
    if revealed == safe:
        printBoard()
        print("Congratulation you won!")
    else:
        for i in range(size):
            for j in range(size):
                if board[i][j] == -1:
                    vsble[i][j] = -1
        printBoard()
        print("Aww, try again next time.")

def main():
    cellCount = size ** 2
    mines = floor(max(cellCount - 9,0) * percentMines)
    global safe
    safe = cellCount - mines
    global titleScreen
    titleScreen  = "-----------------------------------------------------------------------------------------\n"
    titleScreen += "Minesweeper:\n    by: Adrian Long\n    date:2025-09-18\n\n    How to play:\n"
    titleScreen += "        Syntax:\n"
    titleScreen += "            \"#comment here#\"      -> some helpful information\n"
    titleScreen += "            \"<variableName:type>\" -> you must enter a value of the corresponding type\n"
    titleScreen += "            \"[optionalStuff]\"     -> you don't have to type what is inside these\n"
    titleScreen += "            \"{part1,part2,...}\"   -> you may type one of the comma seperated parts\n"
    titleScreen += "            \"mustBeTyped\"         -> you must type all unenclosed parts\n\n"
    titleScreen += "        Modes:\n"
    titleScreen += "            any:\n"
    titleScreen += "                q[uit] #exit the program#\n"
    titleScreen += "                v[isual] #enters visual mode at the center of the minefield#\n"
    titleScreen += "                c[{ls,lear}] #clears the console#\n"
    titleScreen += "                h[elp] #brings up this text window\n"
    titleScreen += "                r[andom] #triggers a non-flagged, non-revealed cell\n" 
    titleScreen += "            selectMode:\n"
    titleScreen += "                <letters:str> <number:int> [{f[lag] ,v[isual]}]\n"
    titleScreen += "                    ex: a 1   -> triggers the a1 cell\n"
    titleScreen += "                    ex: a 1 f -> flags    the a1 cell\n"
    titleScreen += "                    ex: a 1 v -> enters into visual mode at the a1 cell\n"
    titleScreen += "            visualMode: selected cells are highlighted green.\n"
    titleScreen += "                e[nter] #triggers all selected cells#\n"
    titleScreen += "                f[lag]  #flags all selected cells#\n"
    titleScreen += "                m[ark]  #the cell underneath the cursor is selected or unselected\n"
    titleScreen += "                w [<rep:int>] #move up once,    or rep times#\n" 
    titleScreen += "                a [<rep:int>] #move left once,  or rep times#\n" 
    titleScreen += "                s [<rep:int>] #move down once,  or rep times#\n" 
    titleScreen += "                d [<rep:int>] #move right once, or rep times#\n" 
    titleScreen += "                note: rep can be -ve to move in the opposite direction\n\n"
    rightAlign = len(str(cellCount))
    titleScreen += f"        Mines: {mines:>{rightAlign}}\n        Safe:  {safe:>{rightAlign}}\n        Total: {cellCount}\n"
    titleScreen += "-----------------------------------------------------------------------------------------\n"
    print(titleScreen)
    startGame(mines)
main()
