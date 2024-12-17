from tkinter import *
from tkinter import messagebox

class Game:
    def __init__(self, size):
        self.__size = size
        self.__board = [['0' for _ in range(size)] for _ in range(size)]
        self.__initialize_board()

    def get_board(self):
        return self.__board

    def __initialize_board(self):
        self.__board[0][self.__size - 1] = '1'  #Reine 1
        self.__board[self.__size - 1][0] = '3'  #Reine 2

        total_pieces = (self.__size ** 2) // 4 - 1
        self.__fill_area_with_pieces((0, self.__size - 1), total_pieces, '2')  #Pions 1
        self.__fill_area_with_pieces((self.__size - 1, 0), total_pieces, '4')  #Pions 2

    def __fill_area_with_pieces(self, start_position, total_pieces, piece_type):
        x, y = start_position
        layer = 1
        placed_pieces = 0
        #placement des pions
        while placed_pieces < total_pieces:
            for i in range(x - layer, x + layer + 1):
                for j in range(y - layer, y + layer + 1):
                    if 0 <= i < self.__size and 0 <= j < self.__size and self.__board[i][j] == '0':
                        self.__board[i][j] = piece_type
                        placed_pieces += 1
                        if placed_pieces == total_pieces:
                            return 
            layer += 1 

class Player:
    def __init__(self, queen_coords):
        self.__player = 1
        self.queen_coords = queen_coords
        self.pieces_remaining = 0

    def get_player(self):
        return self.__player

    def set_player(self):
        self.__player = 1

    def change_player(self):
        self.__player = 2 if self.__player == 1 else 1

    def count_pieces(self, board):
        if self.__player == 1:
            self.pieces_remaining = sum(row.count('1') + row.count('2') for row in board)
        elif self.__player == 2:
            self.pieces_remaining = sum(row.count('3') + row.count('4') for row in board)
        return self.pieces_remaining

class Gui:
    def __init__(self, size, queen_coords):
        self.__size = size
        self.__game = Game(size)
        self.__board = self.__game.get_board()
        self.__player = Player(queen_coords)
        
        self.__root = Tk()
        self.__root.title("Plateau de Jeu")
        self.__frame1 = Frame(self.__root)
        self.__frame2 = Frame(self.__root)

        self.__frame1.grid(row=0, column=0)
        self.__frame2.grid(row=1, column=0)

        self.__canvas = Canvas(self.__frame1, width=600, height=600, bg="white")
        self.__canvas.pack()
        self.selected = None
        self.valid_moves = []

        self.display()

        self.player_label = Label(self.__frame2, text="Joueur " + str(self.__player.get_player()))
        self.player_label.pack()

        self.__canvas.bind('<Button-1>', self.click_select)
        self.__canvas.focus_set()

        reset_button = Button(self.__frame2, text="Réinitialiser", command=self.reset_board)
        reset_button.pack()

        self.__root.mainloop()

    def get_valid_moves(self, piece_type, start_pos):
        directions = []
        if piece_type in ['1', '3']:  #Reine
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]
        elif piece_type in ['2', '4']:  #Tour
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        valid_moves = []
        y, x = start_pos

        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            while 0 <= ny < self.__size and 0 <= nx < self.__size and self.__board[ny][nx] == '0':
                valid_moves.append((ny, nx))
                ny += dy
                nx += dx

        return valid_moves

    def highlight_moves(self):
        cell_size = 600 // self.__size
        for y, x in self.valid_moves:
            x1, y1 = x * cell_size, y * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            self.__canvas.create_rectangle(x1, y1, x2, y2, fill="lightgrey", outline="black", tags="highlight")

    def clear_highlights(self):
        self.__canvas.delete("highlight")

    def click_select(self, event):
        cell_size = 600 // self.__size
        x = event.x // cell_size
        y = event.y // cell_size

        if 0 <= y < self.__size and 0 <= x < self.__size:
            current_player = self.__player.get_player()
            piece = self.__board[y][x]

            if self.selected is None and piece != '0' and \
                ((current_player == 1 and piece in ['1', '2']) or
                (current_player == 2 and piece in ['3', '4'])):
                self.selected = (y, x)
                self.valid_moves = self.get_valid_moves(piece, (y, x))
                self.highlight_moves()
            elif self.selected:
                sy, sx = self.selected
                self.move(sy, sx, y, x)

    def move(self, sy, sx, y, x):
        selected_piece = self.__board[sy][sx]
        if (y, x) in self.valid_moves:
            self.__board[sy][sx], self.__board[y][x] = '0', selected_piece

            current_player = self.__player.get_player()
            self.check_and_capture(current_player)

            self.selected = None
            self.valid_moves = []

            self.clear_highlights()
            self.display()
            self.__player.change_player()
            self.update_player_label()

            self.check_victory()
        else:
            self.selected = None
            self.valid_moves = []
            self.clear_highlights()

    def check_and_capture(self, player):
        queen_type = '1' if player == 1 else '3'
        opponent_pawn = '4' if player == 1 else '2'
        #cherche la reine du oueur
        queen_pos = None
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__board[i][j] == queen_type:
                    queen_pos = (i, j)
                    break
            if queen_pos:
                break

        qy, qx = queen_pos
        #Vérif du rectangle
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__board[i][j] == '2' and player == 1 or self.__board[i][j] == '4' and player == 2:
                    ty, tx = i, j
                    if ty != qy and tx != qx: 
                        corners = [(qy, tx), (ty, qx)]
                        for cy, cx in corners:
                            if 0 <= cy < self.__size and 0 <= cx < self.__size:
                                if self.__board[cy][cx] == opponent_pawn:
                                    self.__board[cy][cx] = '0' 

    def display(self):
        cell_size = 600 // self.__size  
        self.__canvas.delete("all")  
        for i in range(self.__size):
            for j in range(self.__size):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                self.__canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

                if self.__board[i][j] == '1':  #Reine 1
                    self.__canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="blue")
                elif self.__board[i][j] == '2':  #Pions 1
                    self.__canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="lightblue")
                elif self.__board[i][j] == '3':  #Reine 2
                    self.__canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="red")
                elif self.__board[i][j] == '4':  #Pions 2
                    self.__canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="pink")

    def reset_board(self):
        self.__board = Game(self.__size).get_board()
        self.__player.set_player()
        self.update_player_label()
        self.display()

    def update_player_label(self):
        self.player_label.config(text="Joueur " + str(self.__player.get_player()))

    def check_victory(self):
        self.__player.count_pieces(self.__board)
        if self.__player.pieces_remaining <= 2:
            if self.__player.get_player() == 1 :
                winner = 2
            else :
                winner = 1
            self.end_game(winner)

    def end_game(self, winner):
        response = messagebox.askyesno("Partie terminée", f"Le Joueur {winner} a gagné !\nVoulez-vous rejouer ?")
        if response:
            self.reset_board()
        else:
            self.__root.destroy()

class StartGui:
    def __init__(self):
        self.__root = Tk()
        self.__root.title("Choix de la taille")
        self.ask_size()

    def ask_size(self):
        
        Label(self.__root, text="Règles du jeu :", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=(10, 5))
        Label(self.__root, text="Le but du jeu est de capturer toutes les pièces adverses.").pack()
        Label(self.__root, text="Les reines peuvent se déplacer en diagonale et en ligne droite.").pack()
        Label(self.__root, text="Les pions peuvent se déplacer en ligne droite.").pack()
        Label(self.__root, text="Si la tour du joueur est sur une case qui n'est ni sur la même ligne ni sur la même colonne que sa reine, \n et que des tours adverses se trouvent aux coins du rectangle formé, elles sont capturées.").pack()
        Label(self.__root, text="Le joueur 1 a les pions bleus, le joueur 2 a les pions roses.").pack()
        Label(self.__root, text="").pack()
        Label(self.__root, text="Entrez la taille du plateau (entier pair, 4 à 16) :", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=(10, 5))
        size_entry = Entry(self.__root)
        size_entry.insert(0, "8")
        size_entry.pack()

        def confirm_size():
            try:
                size = int(size_entry.get())
                if size < 4 or size > 16 or size % 2 != 0:
                    raise ValueError("La taille doit être un entier pair entre 4 et 16.")
                queen_coords = (0, size - 1)  #Reine 1
                self.__root.destroy()
                Gui(size, queen_coords)
            except ValueError as e:
                error_label.config(text=str(e))

        Button(self.__root, text="OK", command=confirm_size).pack()
        error_label = Label(self.__root, text="", fg="red")
        error_label.pack()
        self.__root.mainloop()

StartGui()
