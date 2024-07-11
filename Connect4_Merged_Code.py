# Four-In-A-Row (a Connect Four clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, copy, sys, pygame
import timeit #CB
from pygame.locals import *

Number_in_a_row = input("Number of tokens in a row to win (from 4 up to 8, the more the harder!):")

if Number_in_a_row == "4":
        BOARDWIDTH = 7  # how many spaces wide the board is
        BOARDHEIGHT = 6 # how many spaces tall the board is
        assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'
        SPACESIZE = 50 # size of the tokens and individual board spaces in pixels
elif Number_in_a_row == "5":
        BOARDWIDTH = 9  # how many spaces wide the board is
        BOARDHEIGHT = 8 # how many spaces tall the board is
        assert BOARDWIDTH >= 5 and BOARDHEIGHT >= 5, 'Board must be at least 5x5.'
        SPACESIZE = 45 # size of the tokens and individual board spaces in pixels
elif Number_in_a_row == "6":
        BOARDWIDTH = 11  # how many spaces wide the board is
        BOARDHEIGHT = 10 # how many spaces tall the board is
        assert BOARDWIDTH >= 6 and BOARDHEIGHT >= 6, 'Board must be at least 6x6.'
        SPACESIZE = 40 # size of the tokens and individual board spaces in pixels
elif Number_in_a_row == "7":
    BOARDWIDTH = 13  # how many spaces wide the board is
    BOARDHEIGHT = 12 # how many spaces tall the board is
    assert BOARDWIDTH >= 7 and BOARDHEIGHT >= 7, 'Board must be at least 7x7.'
    SPACESIZE = 35 # size of the tokens and individual board spaces in pixels
elif Number_in_a_row == "8":
    BOARDWIDTH = 15  # how many spaces wide the board is
    BOARDHEIGHT = 14 # how many spaces tall the board is
    assert BOARDWIDTH >= 8 and BOARDHEIGHT >= 8, 'Board must be at least 8x8.'
    SPACESIZE = 30 # size of the tokens and individual board spaces in pixels

DIFFICULTY = 2 # how many moves to look ahead. (>2 is usually too much)

FPS = 30 # frames per second to update the screen
WINDOWWIDTH = 840 # width of the program's window, in pixels
WINDOWHEIGHT = 680 # height in pixels

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)

elapsed_time = 0; #CB

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'


def main():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
    global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
    global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG, GREENARROWIMG

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Four in a Row')

    REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    REDTOKENIMG = pygame.image.load('4row_red.png')
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load('4row_black.png')
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load('4row_board.png')
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load('4row_humanwinner.png')
    COMPUTERWINNERIMG = pygame.image.load('4row_computerwinner.png')
    TIEWINNERIMG = pygame.image.load('4row_tie.png')
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    ARROWIMG = pygame.image.load('4row_arrow.png')
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery
    
    isFirstGame = True

    while True:
        runGame(isFirstGame)
        isFirstGame = False


def runGame(isFirstGame):
    if isFirstGame:
        # Let the computer go first on the first game, so the player
        # can see how the tokens are dragged from the token piles.
        turn = COMPUTER
        showHelp = True
    else:
        # Randomly choose who goes first.
        if random.randint(0, 1) == 0:
            turn = COMPUTER
        else:
            turn = HUMAN
        showHelp = False

    # Set up a blank board data structure.
    mainBoard = getNewBoard()

    while True: # main loop cp
        if turn == HUMAN:
            # Human player's turn to make a move cp
            getHumanMove(mainBoard, showHelp)
            if showHelp:
                # turn off help arrow after the first move cp
                showHelp = False
            if isWinner(mainBoard, RED):
                winnerImg = HUMANWINNERIMG # if the human player wins show human winner image cp
                break
            turn = COMPUTER # switch to other player cp
        else:
            # Computer player's turn cp
            column = getComputerMove(mainBoard)
            animateComputerMoving(mainBoard, column)
            makeMove(mainBoard, BLACK, column) # computers move cp
            if isWinner(mainBoard, BLACK): 
                winnerImg = COMPUTERWINNERIMG #if computer player wins display image corresponding to a computer win cp
                break
            turn = HUMAN # switch to other player cp

        if isBoardFull(mainBoard): 
            # A fulll board results in a tie game cp
            winnerImg = TIEWINNERIMG # when the game ends in a tie display tie image
            break

    while True:
        # Keep looping until player clicks the mouse or quits the game cp
        drawBoard(mainBoard)
        DISPLAYSURF.blit(winnerImg, WINNERRECT) 
        pygame.display.update() 
        FPSCLOCK.tick() 
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE): 
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return


def makeMove(board, player, column):
    lowest = getLowestEmptySpace(board, column)
    if lowest != -1: 
        board[column][lowest] = player
# if the bottom of the board already has a token, token falls to next highest spot cp

def drawBoard(board, extraToken=None):
    DISPLAYSURF.fill(BGCOLOR)
    font = pygame.font.Font('freesansbold.ttf' , 20) #CB
    green = (0,255,0) #CB
    black = (0,0,0) #CB

        #time display in User interface, CB
    elapsed_time = int(pygame.time.get_ticks() / 1000) % 10


   #when game is over, won or ties set elapsed time to 0, CB
    if isWinner(board, RED) or isWinner(board, BLACK) or isBoardFull(board): #if these boolean give true any of them then set time to 0 #CB
       elapsed_time = 0 #CB

    #convert elapsed_time in mm:ss format of output_string CB
    minutes = elapsed_time // 60 #CB
    seconds = elapsed_time % 60 #CB
    output_string = "Time Remaining: {0:02}:{1:02}".format(minutes, seconds) #CB

    
    text = font.render(output_string, True, green, black) #CB
    # textRect = text.get_rect()
    # textRect.center = (300, 200)

    DISPLAYSURF.blit(text, (170,30)) #CB

    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    # draw the extra token cp
    if extraToken != None:
        if extraToken['color'] == RED:
            DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
        elif extraToken['color'] == BLACK:
            DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    # draw board over tokens cp
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    # draw the red and black tokens beside the board cp
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT) # red on the left cp
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT) # black on the right cp
    
def getNewBoard():
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY] * BOARDHEIGHT)
    return board

#LH, Function describing the Human player's move 
def getHumanMove(board, isFirstMove): #LH, 2 arguments, current state of the board and if it is the player's first move of the game
    elapsed_time = 0 
    t_0 = timeit.default_timer() #check time first CB
    timerlimit = 9
    draggingToken = False #LH, assign variable to determine if player is dragging the token 
    tokenx, tokeny = None, None #LH, Assigns token position 
    while True: #LH, loop determining how to proceed after a given event in the pygame module 
        t_1 = timeit.default_timer() #check time second CB
        elapsed_time = round((t_1 - t_0) , 3) #take difference of time CB
        drawBoard(board)
        if(elapsed_time > timerlimit): #if time is greater than 10 seconds then exit CB
            return

        for event in pygame.event.get(): 
            if event.type == QUIT: #LH, if player quits the game (event type == QUIT) 
                pygame.quit() #LH, Exit pygame module
                sys.exit() #LH, Exit System module
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos): #LH, If player clicks down on the red pile
                draggingToken = True #LH, Player is dragging a token 
                tokenx, tokeny = event.pos #LH, Position of token is at the red pile
            elif event.type == MOUSEMOTION and draggingToken: #LH, If player moves the mouse 
                tokenx, tokeny = event.pos #LH, Tracks position of the token 
            elif event.type == MOUSEBUTTONUP and draggingToken: #LH, If player lets go of the mouse 
                if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN: #LH, If the token is let go above the board 
                    column = int((tokenx - XMARGIN) / SPACESIZE) #LH, Assigns position of the token above the board/which column it is above 
                    if isValidMove(board, column): #LH, Checks if this is a valid move based on current state of the board and which column was assigned
                        animateDroppingToken(board, column, RED) #LH, Animates token dropping down
                        board[column][getLowestEmptySpace(board, column)] = RED #LH, Positions dropped token at the lowest empty space in that column
                        drawBoard(board) #LH, Draws the board 
                        pygame.display.update() #LH, displays updated state of the game 
                        return
                tokenx, tokeny = None, None #LH, returns token to the pile 
                draggingToken = False #LH, Player is no longer dragging the token
        if tokenx != None and tokeny != None: #LH, If token is not at the pile
            drawBoard(board, {'x':tokenx - int(SPACESIZE / 2), 'y':tokeny - int(SPACESIZE / 2), 'color':RED}) #LH, Draws the board and token at the current position 
        else:
            drawBoard(board) #LH, Draws the board only

        if isFirstMove: #LH, If it is the player's first move 
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT) #LH, Displays help arrow

        pygame.display.update() #LH, Display updated state of the game 
        FPSCLOCK.tick() #LH, Assures run time is 30 FPS for the loop 

#LH, Function describing animation of dropping a token 
def animateDroppingToken(board, column, color): #LH, 3 arguments, current state of board, column it is being dropped in, and colour of the token 
    x = XMARGIN + column * SPACESIZE #LH, Horizontal position of the token 
    y = YMARGIN - SPACESIZE #LH, vertical position of the token
    dropSpeed = 1.0 #LH, Assigns speed at which token drops

    lowestEmptySpace = getLowestEmptySpace(board, column) #LH, Assigns lowest empty space for that column, based on current state of the board
#LH, Loop determing how long to drop the token for 
    while True: 
        y += int(dropSpeed) #LH, increases vertical position of the token at the drop speed 
        dropSpeed += 0.5 #LH, increases drop speed 
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace: #LH, Ends loop at lowest empty space 
            return
        drawBoard(board, {'x':x, 'y':y, 'color':color}) #LH, Draws the board with new token in the position at which it ended 
        pygame.display.update() #LH, Displays updated state of the game 
        FPSCLOCK.tick() #LH, Assures loop runs at 30 FPS 

#LH, Function describing animation of the computers turn 
def animateComputerMoving(board, column): #LH, 2 arguments, current state of the board and column in which computer wants to drop token
    x = BLACKPILERECT.left #LH, Horizontal movement of the black token from the balck pile 
    y = BLACKPILERECT.top #LH, vertical movement of the black token from the black pile 
    speed = 1.0 #LH, speed at which token moves 
 #LH, loop determing vertical position of token 
    while y > (YMARGIN - SPACESIZE): #LH, when y has not reached desired coordinates 
        y -= int(speed) #LH, moves token up at movement speed 
        speed += 0.5 #LH, increases movement speed 
        drawBoard(board, {'x':x, 'y':y, 'color':BLACK}) #LH, Draws the board and token at current position
        pygame.display.update() #LH, Displays updated state of the game 
        FPSCLOCK.tick() #LH, Assures loop runs at 30 FPS 
    
    y = YMARGIN - SPACESIZE #LH, vertical position of token 
    speed = 1.0 #LH, movement speed 
    while x > (XMARGIN + column * SPACESIZE): #LH, loop determining horizontal position, when desired coordinates have not been reached 
        x -= int(speed) #LH, moves token horizontally at movement speed 
        speed += 0.5 #LH, increases movement speed 
        drawBoard(board, {'x':x, 'y':y, 'color':BLACK}) #LH, Draws the board and token at current position 
        pygame.display.update() #LH, displays updated state of the game 
        FPSCLOCK.tick() #LH, Assures loop runs at 30 FPS 
    
    animateDroppingToken(board, column, BLACK) #LH, animates a Black token dropping in desired column based on the current state of the board (using previous function)

#LH, Function describing which move the computer will make
def getComputerMove(board): #LH, 1 argument, current state of the board
    potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY) #LH, Assigns potential moves based on function 
    bestMoveFitness = -1 #LH, assigns best move fitness as -1
    for i in range(BOARDWIDTH): #LH, for all potential moves 
        if potentialMoves[i] > bestMoveFitness and isValidMove(board, i): #LH, if a potential move value is greater than the best move fitness and it is a valid move 
            bestMoveFitness = potentialMoves[i] #LH, Assign potential move value as best move fitness 
    #LH, find all potential moves that have this best fitness
    bestMoves = [] #LH, list best moves 
    for i in range(len(potentialMoves)): #LH, for all potential move values in the range of the list of potential moves
        if potentialMoves[i] == bestMoveFitness and isValidMove(board, i): #LH, if the potential move value is equal to the best move fitness and is a valid move
            bestMoves.append(i) #LH, add it to the end of the list of best moves 
    return random.choice(bestMoves) #LH, chooses a random move from the list of best moves 

#LH, Function describing potential moves for the computer 
def getPotentialMoves(board, tile, lookAhead): #LH, 3 arguments, current state of the board, colour of token, and moves to look ahead 
    if lookAhead == 0 or isBoardFull(board): #LH, if there are no more moves left
        return [0] * BOARDWIDTH #LH, returns no potential moves 

    if tile == RED: #LH, if the colour of the token is red
        enemyTile = BLACK #LH, assigns enemy player tokens as black 
    else:
        enemyTile = RED #LH, otherwise assigns the enemy player tokens as red 

    # Figure out the best move to make.
    potentialMoves = [0] * BOARDWIDTH
    for firstMove in range(BOARDWIDTH):
        dupeBoard = copy.deepcopy(board)
        if not isValidMove(dupeBoard, firstMove):
            continue
        makeMove(dupeBoard, tile, firstMove)
        if isWinner(dupeBoard, tile):
            # a winning move automatically gets a perfect fitness
            potentialMoves[firstMove] = 1
            break # don't bother calculating other moves
        else:
            # do other player's counter moves and determine best one
            if isBoardFull(dupeBoard):
                potentialMoves[firstMove] = 0
            else:
                for counterMove in range(BOARDWIDTH):
                    dupeBoard2 = copy.deepcopy(dupeBoard)
                    if not isValidMove(dupeBoard2, counterMove):
                        continue
                    makeMove(dupeBoard2, enemyTile, counterMove)
                    if isWinner(dupeBoard2, enemyTile):
                        # a losing move automatically gets the worst fitness
                        potentialMoves[firstMove] = -1
                        break
                    else:
                        # do the recursive call to getPotentialMoves()
                        results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
                        potentialMoves[firstMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
    return potentialMoves


def getLowestEmptySpace(board, column):
    # Return the row number of the lowest empty row in the given column.
    for y in range(BOARDHEIGHT-1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1


def isValidMove(board, column):
    # Returns True if there is an empty space in the given column.
    # Otherwise returns False.
    if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
        return False
    return True


def isBoardFull(board):
    # Returns True if there are no empty spaces anywhere on the board.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == EMPTY:
                return False
    return True


def isWinner(board, tile):
    # check horizontal spaces
    if Number_in_a_row == "4":
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                    return True
        return False
    elif Number_in_a_row == "5":
        for x in range(BOARDWIDTH - 4):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile and board[x+4][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 4):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile and board[x][y+4] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 4):
            for y in range(4, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile and board[x+4][y-4]:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 4):
            for y in range(BOARDHEIGHT - 4):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile and board[x+4][y+4] == tile:
                    return True
        return False
    elif Number_in_a_row == "6":
        for x in range(BOARDWIDTH - 5):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile and board[x+4][y] == tile and board[x+5][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 5):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile and board[x][y+4] == tile and board[x][y+5] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 5):
            for y in range(5, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile and board[x+4][y-4] == tile and board[x+5][y-5] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 5):
            for y in range(BOARDHEIGHT - 5):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile and board[x+4][y+4] == tile and board[x+5][y+5] == tile:
                    return True
        return False
    elif Number_in_a_row == "7":
        for x in range(BOARDWIDTH - 6):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile and board[x+4][y] == tile and board[x+5][y] == tile and board[x+6][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 6):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile and board[x][y+4] == tile and board[x][y+5] == tile and board[x][y+6] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 6):
            for y in range(6, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile and board[x+4][y-4] == tile and board[x+5][y-5] == tile and board[x+6][y-6] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 6):
            for y in range(BOARDHEIGHT - 6):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile and board[x+4][y+4] == tile and board[x+5][y+5] == tile and board[x+6][y+6] == tile:
                    return True
        return False
    elif Number_in_a_row == "8":
        for x in range(BOARDWIDTH - 7):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile and board[x+4][y] == tile and board[x+5][y] == tile and board[x+6][y] == tile and board[x+7][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 7):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile and board[x][y+4] == tile and board[x][y+5] == tile and board[x][y+6] == tile and board[x][y+7] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 7):
            for y in range(7, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile and board[x+4][y-4] == tile and board[x+5][y-5] == tile and board[x+6][y-6] == tile and board[x+7][y-7] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 7):
            for y in range(BOARDHEIGHT - 7):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile and board[x+4][y+4] == tile and board[x+5][y+5] == tile and board[x+6][y+6] == tile and board[x+7][y+7] == tile:
                    return True
        return False

if __name__ == '__main__':
    main()
