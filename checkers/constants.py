from checkers.point import Point
from checkers.enums import CheckerType, SideType

# The side for which the player plays
PLAYER_SIDE = SideType.WHITE

# Field size
X_SIZE = Y_SIZE = 8
# Cell size (in pixels)
CELL_SIZE = 75

# Animation speed (more = faster)
ANIMATION_SPEED = 4

# Number of moves to predict
MAX_PREDICTION_DEPTH = 3

BORDER_WIDTH = 2 * 2

# Game board colors
FIELD_COLORS = ['#ebf2ed', '#756666']
# Border color when hovering the mouse over a cell
HOVER_BORDER_COLOR = '#54b346'
# Border color when selecting a cell
SELECT_BORDER_COLOR = '#944444'
# Color of circles of possible moves
POSIBLE_MOVE_CIRCLE_COLOR = '#19d44e'

# Possible shifts of checkers moves
MOVE_OFFSETS = [
    Point(-1, -1),
    Point( 1, -1),
    Point(-1,  1),
    Point( 1,  1)
]

# Arrays of white and black checkers types [regular, Queen]
WHITE_CHECKERS = [CheckerType.WHITE_REGULAR, CheckerType.WHITE_QUEEN]
BLACK_CHECKERS = [CheckerType.BLACK_REGULAR, CheckerType.BLACK_QUEEN]