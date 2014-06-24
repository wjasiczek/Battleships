from __future__ import print_function
import threading
import time
import random


#Program polega na grze dwoch watkow miedzy soba w statki

#listy 12 x 12 aby obudowac je do okola 9
boardOne = [ ['-' for i in range(12)] for j in range(12) ]
boardTwo = [ ['-' for i in range(12)] for j in range(12) ]
#lastShot = 100 #brak strzalu, pierwsze sprawdzenie
count = 0 #zliczanie ilosci strzalow


class Play(threading.Thread):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    digits = [ i for i in range(10) ]
    lastShot = 100
    def __init__(self, board, player, lock, event):
        threading.Thread.__init__(self)
        self.board = board
        self.player = player
        self.lock = lock
        self.event = event
        self.previousMoves = []
        for i in range(12):         
            for j in range(12):
                if self.board[i][j] == 9:
                    self.board[i][j] = '-'
    
    """Pracuje na numeracji 0-99, zeby latwiej bylo przechowywac poprzednie ruchy
       pobieram ostatni strzal przeciwnika, sprawdzam, czy na tym polu stoi moj statek i jesli tak to zamieniam to pole na - (niszcze pole)
       nastepnie losuje swoj ruch i jesli nie znajduje sie na liscie poprzednich ruchow to wpisuje go na liste i zapisuje go w statycznej zmiennej lastShot"""
    def run(self):
        while not self.event.is_set():
            self.lock.acquire()
            global count 
            count = count + 1
            print(count)
            if not Play.lastShot == 100:
                row = int((Play.lastShot - Play.lastShot % 10) / 10)
                column = Play.lastShot % 10
                if not self.board[row+1][column+1] == '-':
                    print("Pole " + Play.letters[row] + ", " + str(column) + " gracza " + str(self.player) + " zostalo zniszczone!") 
                    self.board[row+1][column+1] = 'X'
            self.WhoWon()
            if self.event.is_set():
                self.PrintBoard()
                self.lock.release()
                time.sleep(2)
                continue  
            print("Gracz " + str(self.player) + " wykonuje ruch")
            isCorrect = False
            while not isCorrect:
                row = random.randint(0,9)
                column = random.randint(0,9)
                moveBufor = column + row * 10
                if not self.previousMoves.__contains__(moveBufor):
                    Play.lastShot = moveBufor
                    self.previousMoves.append(moveBufor)
                    isCorrect = True
            print("Gracz " + str(self.player) + " strzelil w pole " + self.letters[row] + ", " + str(column))
            self.PrintBoard()
            print()
            self.lock.release()
            time.sleep(2) 
             
    def PrintBoard(self):   
        print ("Wyswietlam plansze gracza " + str(self.player))
        print(end="  ")
        for column in range(10):
            print(Play.digits[column], end="  ")
        print()
        for row in range(10):
            print(Play.letters[row], end=" ")
            for column in range(10):
                if self.board[row+1][column+1] == 9:
                    if column == 9:
                        print("-")
                    else:
                        print("-", end="  ")
                else:
                    if column == 9:
                        print(str(self.board[row+1][column+1]))
                    else:
                        print(str(self.board[row+1][column+1]), end="  ")        
          
    def WhoWon(self):
        for row in range(10):
            for column in range(10):
                if self.board[row+1][column+1] == 'O':
                    return
                
        if self.player == 1:
            print("Zwyciezyl gracz 2!")
        else:
            print("Zwyciezyl gracz 1!")
        self.event.set()
                
      
def PrepareBoard(board, player, size):
    for i in range(0,12):  #Obudowujemy do okola 9 zeby nie wstawialo statkow obok siebie
        board[0][i] = 9
        board[11][i] = 9
        board[i][0] = 9
        board[i][11] = 9
    
    """Tutaj losuje pozycje i kierunek, w ktorym ma byc budowany statek i sprawdzam czy istnieje dla niego miejsce. 
       Jesli nie to losuje inna pozycje i kierunek"""           
    for ships in range(5-size):
        isCorrect = False
        while not isCorrect:
            row = random.randint(1,10)
            column = random.randint(1,10)
            if board[row][column] == '-':
                direction = random.randint(0,3)
                isCorrect = True    
                if direction == 0:
                    for sizeOfShip in range(size-1):
                        if not board[row][column+1+sizeOfShip] == '-':
                            isCorrect = False
                            break
                elif direction == 1:
                    for sizeOfShip in range(size-1):
                        if not board[row+1+sizeOfShip][column] == '-':
                            isCorrect = False
                            break
                elif direction == 2:
                    for sizeOfShip in range(size-1):    
                        if not board[row][column-1-sizeOfShip] == '-':
                            isCorrect = False
                            break
                elif direction == 3:
                    for sizeOfShip in range(size-1):
                        if not board[row-1-sizeOfShip][column] == '-':
                            isCorrect = False
                            break
        
        """Jezeli jest miejsce na statek to umieszczam go w wyzej sprawdzonym miejscu i obudowuje go 9 aby inne statki nie mogly obok niego stanac"""               
        if isCorrect:
            for update in range(size):
                board[row][column] = player
                if direction == 0:
                    for sizeOfShip in range(size-1):
                        board[row][column+1+sizeOfShip] = player
                    for i in range(size+2):
                        board[row-1][column-1+i] = 9
                        board[row+1][column-1+i] = 9
                    board[row][column-1] = 9
                    board[row][column+size] = 9
                elif direction == 1:
                    for sizeOfShip in range(size-1):
                        board[row+1+sizeOfShip][column] = player
                    for i in range(size+2):
                        board[row-1+i][column-1] = 9
                        board[row-1+i][column+1] = 9
                    board[row-1][column] = 9
                    board[row+size][column] = 9
                elif direction == 2:
                    for sizeOfShip in range(size-1):
                        board[row][column-1-sizeOfShip] = player
                    for i in range(size+2):
                        board[row-1][column-size+i] = 9
                        board[row+1][column-size+i] = 9
                    board[row][column-size] = 9
                    board[row][column+1] = 9    
                elif direction == 3:
                    for sizeOfShip in range(size-1):
                        board[row-1-sizeOfShip][column] = player
                    for i in range(size+2):
                        board[row-size+i][column-1] = 9
                        board[row-size+i][column+1] = 9
                    board[row-size][column] = 9
                    board[row+1][column] = 9
                                        
    
for sizeOfShip in range(1,5):
    PrepareBoard(boardOne, 'O', sizeOfShip)
    PrepareBoard(boardTwo, 'O', sizeOfShip)             

lock = threading.Lock()
event = threading.Event()

Play(boardOne, 1, lock, event).start()
time.sleep(1)
Play(boardTwo, 2, lock, event).start() 
