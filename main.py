from tkinter import Tk, Canvas, PhotoImage, Button, Entry, ttk
from tkinter.constants import NO, CENTER

from checkers.enums import GameType
from checkers.game import Game
from checkers.constants import X_SIZE, Y_SIZE, CELL_SIZE
import checkers.leaderboard as lb


def main():
    # Creating a window
    main_window = Tk()
    lb.create_table()
    main_window.title('Checkers')
    main_window.resizable(0, 0)
    main_window.iconphoto(False, PhotoImage(file='images/icon.png'))

    # Creating leaderboard
    my_leaderboard = ttk.Treeview(main_window)

    my_leaderboard['columns'] = ('id', 'name', 'score')

    my_leaderboard.column("#0", width=0, stretch=NO)
    my_leaderboard.column("id", anchor=CENTER, width=80)
    my_leaderboard.column("name", anchor=CENTER, width=80)
    my_leaderboard.column("score", anchor=CENTER, width=80)

    my_leaderboard.heading("#0", text="", anchor=CENTER)
    my_leaderboard.heading("id", text="Id", anchor=CENTER)
    my_leaderboard.heading("name", text="Name", anchor=CENTER)
    my_leaderboard.heading("score", text="Score", anchor=CENTER)

    for row in lb.show_table():
        pl_id = row[0]
        pl_name = row[1]
        pl_score = row[2]
        my_leaderboard.insert(parent="", index='end', iid=row[0], text="", values=(f'{pl_id}', f'{pl_name}', f'{pl_score}'))

    my_leaderboard.pack()

    def input_name(type: GameType):
        startVsBotButton.destroy()
        startVsPlayerButton.destroy()
        e.pack()
        if type == GameType.PVP:
            e1.pack()
        gameButton.pack()

    def start_game():
        gameButton.destroy()
        playerNames = dict()
        playerNames["white"] = e.get()
        opponentsName = e1.get()
        e.destroy()
        my_leaderboard.destroy()

        # Creating a canvas
        main_canvas = Canvas(main_window, width=CELL_SIZE * X_SIZE, height=CELL_SIZE * Y_SIZE)
        main_canvas.pack()

        if opponentsName != "Enter opponents name":
            playerNames["black"] = e1.get()
            e1.destroy()
            game = Game(main_canvas, X_SIZE, Y_SIZE, playerNames, GameType.PVP)
        else:
            game = Game(main_canvas, X_SIZE, Y_SIZE, playerNames, GameType.PVE)
        main_canvas.bind("<Motion>", game.mouse_move)
        main_canvas.bind("<Button-1>", game.mouse_down)

    e = Entry(main_window, width=40)
    e.insert(0, "Enter your name")
    e1 = Entry(main_window, width=40)
    e1.insert(0, "Enter opponents name")
    gameButton = Button(main_window, text="Start", command=start_game)

    startVsBotButton = Button(main_window, text="Start vs Bot", command=lambda: input_name(GameType.PVE))
    startVsPlayerButton = Button(main_window, text="Start vs Player", command=lambda: input_name(GameType.PVP))
    startVsBotButton.pack()
    startVsPlayerButton.pack()

    main_window.mainloop()


if __name__ == '__main__':
    main()
