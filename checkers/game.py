from tkinter import Canvas, Event, messagebox
from PIL import Image, ImageTk
from random import choice
from pathlib import Path
from time import sleep
from math import inf

from checkers.field import Field
from checkers.move import Move
from checkers.constants import *
from checkers.enums import CheckerType, SideType, GameType

import checkers.leaderboard as lb


class Game:
    def __init__(self, canvas: Canvas, x_field_size: int, y_field_size: int, player_names: dict, game_type: GameType):

        self.__player_names = player_names
        self.__game_type = game_type

        self.__canvas = canvas
        self.__field = Field(x_field_size, y_field_size)

        self.__player_turn = True

        self.__current_turn = SideType.WHITE

        self.__hovered_cell = Point()
        self.__selected_cell = Point()
        self.__animated_cell = Point()

        self.__init_images()

        self.__draw()

        lb.create_table()

        # If the player plays for the blacks, then make the opponent's move
        if (PLAYER_SIDE == SideType.BLACK):
            self.__handle_enemy_turn()

    def __init_images(self):
        self.__images = {
            CheckerType.WHITE_REGULAR: ImageTk.PhotoImage(
                Image.open(Path('images', 'red-regular.png')).resize((CELL_SIZE, CELL_SIZE), Image.ANTIALIAS)),
            CheckerType.BLACK_REGULAR: ImageTk.PhotoImage(
                Image.open(Path('images', 'black-regular.png')).resize((CELL_SIZE, CELL_SIZE), Image.ANTIALIAS)),
            CheckerType.WHITE_QUEEN: ImageTk.PhotoImage(
                Image.open(Path('images', 'red-queen.png')).resize((CELL_SIZE, CELL_SIZE), Image.ANTIALIAS)),
            CheckerType.BLACK_QUEEN: ImageTk.PhotoImage(
                Image.open(Path('images', 'black-queen.png')).resize((CELL_SIZE, CELL_SIZE), Image.ANTIALIAS)),
        }

    def __animate_move(self, move: Move):
        self.__animated_cell = Point(move.from_x, move.from_y)
        self.__draw()

        # Creating checkers for animation
        animated_checker = self.__canvas.create_image(move.from_x * CELL_SIZE, move.from_y * CELL_SIZE,
                                                      image=self.__images.get(
                                                          self.__field.type_at(move.from_x, move.from_y)), anchor='nw',
                                                      tag='animated_checker')

        # Motion vectors
        dx = 1 if move.from_x < move.to_x else -1
        dy = 1 if move.from_y < move.to_y else -1

        # Animation
        for distance in range(abs(move.from_x - move.to_x)):
            for _ in range(100 // ANIMATION_SPEED):
                self.__canvas.move(animated_checker, ANIMATION_SPEED / 100 * CELL_SIZE * dx,
                                   ANIMATION_SPEED / 100 * CELL_SIZE * dy)
                self.__canvas.update()
                sleep(0.01)

        self.__animated_cell = Point()

    def __draw(self):
        """Displaying the grid of fields and checkers"""
        self.__canvas.delete('all')
        self.__draw_field_grid()
        self.__draw_checkers()

    def __draw_field_grid(self):
        """Drawing a field grid"""
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                self.__canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, x * CELL_SIZE + CELL_SIZE,
                                               y * CELL_SIZE + CELL_SIZE, fill=FIELD_COLORS[(y + x) % 2], width=0,
                                               tag='boards')

                # Drawing frames for the required cells
                if (x == self.__selected_cell.x and y == self.__selected_cell.y):
                    self.__canvas.create_rectangle(x * CELL_SIZE + BORDER_WIDTH // 2, y * CELL_SIZE + BORDER_WIDTH // 2,
                                                   x * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2,
                                                   y * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2,
                                                   outline=SELECT_BORDER_COLOR, width=BORDER_WIDTH, tag='border')
                elif (x == self.__hovered_cell.x and y == self.__hovered_cell.y):
                    self.__canvas.create_rectangle(x * CELL_SIZE + BORDER_WIDTH // 2, y * CELL_SIZE + BORDER_WIDTH // 2,
                                                   x * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2,
                                                   y * CELL_SIZE + CELL_SIZE - BORDER_WIDTH // 2,
                                                   outline=HOVER_BORDER_COLOR, width=BORDER_WIDTH, tag='border')

                # Displaying possible move points if there is a selected cell
                if (self.__selected_cell):
                    #player_moves_list = self.__get_moves_list(PLAYER_SIDE)
                    player_moves_list = self.__get_moves_list(self.__current_turn)
                    for move in player_moves_list:
                        if (self.__selected_cell.x == move.from_x and self.__selected_cell.y == move.from_y):
                            self.__canvas.create_oval(move.to_x * CELL_SIZE + CELL_SIZE / 3,
                                                      move.to_y * CELL_SIZE + CELL_SIZE / 3,
                                                      move.to_x * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3),
                                                      move.to_y * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3),
                                                      fill=POSIBLE_MOVE_CIRCLE_COLOR, width=0,
                                                      tag='posible_move_circle')

    def __draw_checkers(self):
        '''Drawing checkers'''
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # Don't draw empty cells or animated checkers
                if (self.__field.type_at(x, y) != CheckerType.NONE and not (
                        x == self.__animated_cell.x and y == self.__animated_cell.y)):
                    self.__canvas.create_image(x * CELL_SIZE, y * CELL_SIZE,
                                               image=self.__images.get(self.__field.type_at(x, y)), anchor='nw',
                                               tag='checkers')

    def mouse_move(self, event: Event):
        """Mouse movement event"""
        x, y = (event.x) // CELL_SIZE, (event.y) // CELL_SIZE
        if (x != self.__hovered_cell.x or y != self.__hovered_cell.y):
            self.__hovered_cell = Point(x, y)

            # If the player's turn, then redraw
            if (self.__player_turn):
                self.__draw()

    def mouse_down(self, event: Event):
        """Mouse click event"""
        if self.__game_type == GameType.PVE:
            if not (self.__player_turn): return

            x, y = (event.x) // CELL_SIZE, (event.y) // CELL_SIZE

            # If the point is not inside the field
            if not (self.__field.is_within(x, y)): return

            if (PLAYER_SIDE == SideType.WHITE):
                player_checkers = WHITE_CHECKERS
            elif (PLAYER_SIDE == SideType.BLACK):
                player_checkers = BLACK_CHECKERS
            else:
                return

            # If you click on the player's checker, then select it
            if (self.__field.type_at(x, y) in player_checkers):
                self.__selected_cell = Point(x, y)
                self.__draw()
            elif (self.__player_turn):
                move = Move(self.__selected_cell.x, self.__selected_cell.y, x, y)

                # If you click on a cell that you can look like
                if (move in self.__get_moves_list(PLAYER_SIDE)):
                    self.__handle_player_turn(move)

                    if not (self.__player_turn):
                        self.__handle_enemy_turn()
        else:
            x, y = (event.x) // CELL_SIZE, (event.y) // CELL_SIZE
            if not (self.__field.is_within(x, y)): return
            if (self.__current_turn == SideType.WHITE):
                player_checkers = WHITE_CHECKERS
            elif (self.__current_turn == SideType.BLACK):
                player_checkers = BLACK_CHECKERS
            else:
                return
            if (self.__field.type_at(x, y) in player_checkers):
                self.__selected_cell = Point(x, y)
                self.__draw()
            elif (self.__player_turn):
                move = Move(self.__selected_cell.x, self.__selected_cell.y, x, y)

                if (move in self.__get_moves_list(self.__current_turn)):
                    self.__handle_player_turn(move)



    def __handle_move(self, move: Move, draw: bool = True) -> bool:
        '''Making a move'''
        if (draw): self.__animate_move(move)

        # Changing the type of checker if it has reached the edge
        if (move.to_y == 0 and self.__field.type_at(move.from_x, move.from_y) == CheckerType.WHITE_REGULAR):
            self.__field.at(move.from_x, move.from_y).change_type(CheckerType.WHITE_QUEEN)
        elif (move.to_y == self.__field.y_size - 1 and self.__field.type_at(move.from_x,
                                                                            move.from_y) == CheckerType.BLACK_REGULAR):
            self.__field.at(move.from_x, move.from_y).change_type(CheckerType.BLACK_QUEEN)

        # Changing the position of the checker
        self.__field.at(move.to_x, move.to_y).change_type(self.__field.type_at(move.from_x, move.from_y))
        self.__field.at(move.from_x, move.from_y).change_type(CheckerType.NONE)

        # Motion vectors
        dx = -1 if move.from_x < move.to_x else 1
        dy = -1 if move.from_y < move.to_y else 1

        # Removing eaten checkers
        has_killed_checker = False
        x, y = move.to_x, move.to_y
        while (x != move.from_x or y != move.from_y):
            x += dx
            y += dy
            if (self.__field.type_at(x, y) != CheckerType.NONE):
                self.__field.at(x, y).change_type(CheckerType.NONE)
                has_killed_checker = True

        if (draw): self.__draw()

        return has_killed_checker

    def __handle_player_turn(self, move: Move):
        """Processing a player's turn"""
        if self.__game_type == GameType.PVE:
            self.__player_turn = False


            # Was the checker killed
            has_killed_checker = self.__handle_move(move)

            required_moves_list = list(
                filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y,
                       self.__get_required_moves_list(PLAYER_SIDE)))

            # If there is another move with the same checker
            if (has_killed_checker and required_moves_list):
                self.__player_turn = True

            self.__selected_cell = Point()
        else:
            self.__current_turn = self.__current_turn.opposite()
            has_killed_checker = self.__handle_move(move)

            required_moves_list = list(
                filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y,
                       self.__get_required_moves_list(self.__current_turn.opposite())))

            # If there is another move with the same checker
            if (has_killed_checker and required_moves_list):
                self.__current_turn = self.__current_turn.opposite()

            self.__selected_cell = Point()
        self.__check_for_game_over()




    def __handle_enemy_turn(self):
        """Working out the opponent's move"""
        self.__player_turn = False

        optimal_moves_list = self.__predict_optimal_moves(SideType.opposite(PLAYER_SIDE))

        for move in optimal_moves_list:
            self.__handle_move(move)

        self.__player_turn = True

        self.__check_for_game_over()

    def __check_for_game_over(self):
        """Checking at the end of the game"""
        game_over = False

        white_moves_list = self.__get_moves_list(SideType.WHITE)
        if not (white_moves_list):
            # White lost
            answer = messagebox.showinfo('The end of the game', 'Black wins')
            if self.__game_type == GameType.PVE:
                lb.add_player(self.__player_names["white"], self.__field.white_score - self.__field.black_score)
            else:
                lb.add_player(self.__player_names["black"], self.__field.black_score)
            game_over = True

        black_moves_list = self.__get_moves_list(SideType.BLACK)
        if not (black_moves_list):
            # Black lost
            answer = messagebox.showinfo('The end of the game', 'White wins')
            lb.add_player(self.__player_names["white"], self.__field.white_score)
            game_over = True

        if (game_over):
            # Start new game
            self.__init__(self.__canvas, self.__field.x_size, self.__field.y_size, self.__player_names, GameType.PVP)

    def __predict_optimal_moves(self, side: SideType) -> list[Move]:
        """Predict the optimal move"""
        best_result = 0
        optimal_moves = []
        predicted_moves_list = self.__get_predicted_moves_list(side)

        if (predicted_moves_list):
            field_copy = Field.copy(self.__field)
            for moves in predicted_moves_list:
                for move in moves:
                    self.__handle_move(move, draw=False)

                try:
                    if (side == SideType.WHITE):
                        result = self.__field.white_score / self.__field.black_score
                    elif (side == SideType.BLACK):
                        result = self.__field.black_score / self.__field.white_score
                except ZeroDivisionError:
                    result = inf

                if (result > best_result):
                    best_result = result
                    optimal_moves.clear()
                    optimal_moves.append(moves)
                elif (result == best_result):
                    optimal_moves.append(moves)

                self.__field = Field.copy(field_copy)

        optimal_move = []
        if (optimal_moves):
            # Filtering moves
            for move in choice(optimal_moves):
                if (side == SideType.WHITE and self.__field.type_at(move.from_x, move.from_y) in BLACK_CHECKERS):
                    break
                elif (side == SideType.BLACK and self.__field.type_at(move.from_x, move.from_y) in WHITE_CHECKERS):
                    break

                optimal_move.append(move)

        return optimal_move

    def __get_predicted_moves_list(self, side: SideType, current_prediction_depth: int = 0,
                                   all_moves_list: list[Move] = [], current_moves_list: list[Move] = [],
                                   required_moves_list: list[Move] = []) -> list[Move]:
        """Sort all possible moves"""

        if (current_moves_list):
            all_moves_list.append(current_moves_list)
        else:
            all_moves_list.clear()

        if (required_moves_list):
            moves_list = required_moves_list
        else:
            moves_list = self.__get_moves_list(side)

        if (moves_list and current_prediction_depth < MAX_PREDICTION_DEPTH):
            field_copy = Field.copy(self.__field)
            for move in moves_list:
                has_killed_checker = self.__handle_move(move, draw=False)

                required_moves_list = list(filter(
                    lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y,
                    self.__get_required_moves_list(side)))

                # If there is another move with the same checker
                if (has_killed_checker and required_moves_list):
                    self.__get_predicted_moves_list(side, current_prediction_depth, all_moves_list,
                                                    current_moves_list + [move], required_moves_list)
                else:
                    self.__get_predicted_moves_list(SideType.opposite(side), current_prediction_depth + 1,
                                                    all_moves_list, current_moves_list + [move])

                self.__field = Field.copy(field_copy)

        return all_moves_list

    def __get_moves_list(self, side: SideType) -> list[Move]:
        """Getting a list of moves"""
        moves_list = self.__get_required_moves_list(side)
        if not (moves_list):
            moves_list = self.__get_optional_moves_list(side)
        return moves_list

    def __get_required_moves_list(self, side: SideType) -> list[Move]:
        """Getting a list of required moves"""
        moves_list = []

        # Defining checker types
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
            enemy_checkers = BLACK_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
            enemy_checkers = WHITE_CHECKERS
        else:
            return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):

                # For a regular checker
                if (self.__field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        if self.__field.type_at(x + offset.x, y + offset.y) in enemy_checkers and self.__field.type_at(
                                x + offset.x * 2, y + offset.y * 2) == CheckerType.NONE:
                            moves_list.append(Move(x, y, x + offset.x * 2, y + offset.y * 2))

                # For the Queen
                elif (self.__field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        has_enemy_checker_on_way = False

                        for shift in range(1, self.__field.size):
                            if not (self.__field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            # If there was no enemy checker on the way
                            if (not has_enemy_checker_on_way):
                                if (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) in enemy_checkers):
                                    has_enemy_checker_on_way = True
                                    continue
                                # If there is an allied checker on the way, then finish the cycle
                                elif (self.__field.type_at(x + offset.x * shift,
                                                           y + offset.y * shift) in friendly_checkers):
                                    break

                            # If there was an enemy checker on the way
                            if (has_enemy_checker_on_way):
                                if (self.__field.type_at(x + offset.x * shift,
                                                         y + offset.y * shift) == CheckerType.NONE):
                                    moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                                else:
                                    break

        return moves_list

    def __get_optional_moves_list(self, side: SideType) -> list[Move]:
        """Getting a list of optional moves"""
        moves_list = []

        # Defining checker types
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
        else:
            return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # For a regular checker
                if (self.__field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS[:2] if side == SideType.WHITE else MOVE_OFFSETS[2:]:
                        if not (self.__field.is_within(x + offset.x, y + offset.y)): continue

                        if (self.__field.type_at(x + offset.x, y + offset.y) == CheckerType.NONE):
                            moves_list.append(Move(x, y, x + offset.x, y + offset.y))

                # For the Queen
                elif (self.__field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x, y + offset.y)): continue

                        for shift in range(1, self.__field.size):
                            if not (self.__field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            if (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE):
                                moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                            else:
                                break
        return moves_list
