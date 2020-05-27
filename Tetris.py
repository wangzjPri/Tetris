import logging
import random
import time
import os
import curses

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='Tetris.log', filemode='w')
logger = logging.getLogger(__name__)

EMPTY_SQAURE = ' '
TYPES = [x for x in range(6)]
COLORS = ['r', 'g', 'b', 'o']
# COLORS = ['x']
MOVE = ['L', 'R', 'U', 'D']  # 


class Pieces:
    """
    0: ▉▉  1: ▉ 2:  ▉▉▉  3:     ▉▉  4 :   ▉▉    5:      ▉     6:   ▉▉▉
       ▉▉     ▉         ▉       ▉▉            ▉▉        ▉▉▉        ▉
                ▉
                ▉
    """

    def __init__(self, type, color):
        """
        :param x:  x
        :param y:  y
        :param type:  0 ~6
        :param color: 'r': red  ,'g': green  , 'b': blue , 'o': orange
        """
        self._x = 4
        self._y = 0
        self._color = color
        self._type = type
        self._to_draw = []
        self._to_clear = []
        self._pos = None
        self.init_matrix()
        self._rotate_count = [0 for x in range(7)]  # rotate count for every type of shape
        # print(f'init {self._pos}')
        """
        self.type1_rotates = [self.spawn_shapes((0, -1), (0, 1), (0, 2)),
                              self.spawn_shapes((-1, 0), (1, 0), (2, 0))]

        self.type2_rotates = [self.spawn_shapes((-1, 0), (1, 0), (1, 1)),
                              self.spawn_shapes((0, -1), (0, 1), (-1, 1)),
                              self.spawn_shapes((-1, -1), (-1, 0), (1, 0)),
                              self.spawn_shapes((0, -1), (1, -1), (0, 1)),
                              self.spawn_shapes((0, -1), (1, -1), (0, 1))
                              ]
        self.type3_rotates = [self.spawn_shapes((1, 0), (-1, 1), (0, 1)),
                              self.spawn_shapes((-1, -1), (-1, 0), (0, 1))
                              ]
        self.type4_rotates = [self.spawn_shapes((-1, 0), (0, 1), (1, 1)),
                              self.spawn_shapes((0, -1), (-1, 0), (-1, 1))]
        self.type5_rotates = [self.spawn_shapes((0, -1), (-1, 0), (1, 0)),
                              self.spawn_shapes((0, -1), (1, 0), (0, 1)),
                              self.spawn_shapes((-1, 0), (1, 0), (0, 1)),
                              self.spawn_shapes((0, -1), (-1, 0), (0, 1))
                              ]
        self.type6_rotates = [self.spawn_shapes((-1, 0), (1, 0), (-1, 1)),
                              self.spawn_shapes((-1, -1), (0, -1), (0, 1)),
                              self.spawn_shapes((1, -1), (-1, 0), (1, 0)),
                              self.spawn_shapes((0, -1), (0, 1), (1, 1)),
                              ]
        """

        self.type1_angle = [[(0, -1), (0, 1), (0, 2)],
                            [(-1, 0), (1, 0), (2, 0)]]
        self.type2_angle = [[(-1, 0), (1, 0), (1, 1)],
                            [(0, -1), (0, 1), (-1, 1)],
                            [(-1, -1), (-1, 0), (1, 0)],
                            [(0, -1), (1, -1), (0, 1)],
                            [(0, -1), (1, -1), (0, 1)]
                            ]
        self.type3_angle = [[(1, 0), (-1, 1), (0, 1)],
                            [(-1, -1), (-1, 0), (0, 1)]
                            ]
        self.type4_angle = [[(-1, 0), (0, 1), (1, 1)],
                              [(0, -1), (-1, 0), (-1, 1)]]
        self.type5_angle = [[(0, -1), (-1, 0), (1, 0)],
                              [(0, -1), (1, 0), (0, 1)],
                              [(-1, 0), (1, 0), (0, 1)],
                              [(0, -1), (-1, 0), (0, 1)]
                              ]
        self.type6_angle = [[(-1, 0), (1, 0), (-1, 1)],
                              [(-1, -1), (0, -1), (0, 1)],
                              [(1, -1), (-1, 0), (1, 0)],
                              [(0, -1), (0, 1), (1, 1)],
                              ]

    def angle_to_points(self, angle):
        res = []
        for l in angle:
            res.append(self.spawn_shapes(l[0], l[1], l[2]))
        return res

    def spawn_shapes(self, b, c, d):
        x1, y1 = b
        x2, y2 = c
        x3, y3 = d

        return [(self._x, self._y, self._color), (self._x + x1, self._y + y1, self._color),
                (self._x + x2, self._y + y2, self._color), (self._x + x3, self._y + y3, self._color)
                ]  # 2x2 matrix

    def move(self):
        if self._pos is not None:
            self._to_draw = self.spawn_shapes(self._pos[0], self._pos[1], self._pos[2])
        else:
            self.init_matrix()

    def _rotate_index(self, direction, type, mod):
        if direction == 0:
            self._rotate_count[type] += 1
        elif direction == 1:
            self._rotate_count[type] -= 1
        if self._rotate_count[type] < 0:
            self._rotate_count[type] = mod - 1
        if self._rotate_count[type] > mod - 1:
            self._rotate_count[type] = 0
        return self._rotate_count[type]

    def rotate(self, direction=0):  # 0 for right , 1 for left
        type = self._type
        if type is 0:
            return  # no change for square ^^
        elif type is 1:
            choice = self._rotate_index(direction, type, 2)
            self.type1_rotates = self.angle_to_points(self.type1_angle)
            self._to_draw = self.type1_rotates[choice]
            self._pos = self.type1_angle[choice]
        elif type is 2:
            choice = self._rotate_index(direction, type, 4)
            self.type2_rotates = self.angle_to_points(self.type2_angle)
            self._to_draw = self.type2_rotates[choice]
            self._pos = self.type2_angle[choice]
        elif type is 3:
            choice = self._rotate_index(direction, type, 2)
            self.type3_rotates = self.angle_to_points(self.type3_angle)
            self._to_draw = self.type3_rotates[choice]
            self._pos = self.type3_angle[choice]
        elif type is 4:
            choice = self._rotate_index(direction, type, 2)
            self.type4_rotates = self.angle_to_points(self.type4_angle)
            self._to_draw = self.type4_rotates[choice]
            self._pos = self.type4_angle[choice]
        elif type is 5:
            choice = self._rotate_index(direction, type, 4)
            self.type5_rotates = self.angle_to_points(self.type5_angle)
            self._to_draw = self.type5_rotates[choice]
            self._pos = self.type5_angle[choice]
        elif type is 6:
            choice = self._rotate_index(direction, type, 2)
            self.type6_rotates = self.angle_to_points(self.type6_angle)
            self._to_draw = self.type6_rotates[choice]
            self._pos = self.type5_angle[choice]

    def init_matrix(self):
        type = self._type
        if type is 0:
            self._to_draw = self.spawn_shapes((1, 0), (0, 1), (1, 1))
        elif type is 1:
            self._to_draw = self.spawn_shapes((0, -1), (0, 1), (0, 2))
        elif type is 2:
            self._to_draw = self.spawn_shapes((-1, 0), (1, 0), (1, 1))
        elif type is 3:
            self._to_draw = self.spawn_shapes((1, 0), (-1, 1), (0, 1))
        elif type is 4:
            self._to_draw = self.spawn_shapes((-1, 0), (0, 1), (1, 1))
        elif type is 5:
            self._to_draw = self.spawn_shapes((0, -1), (-1, 0), (1, 0))
        elif type is 6:
            self._to_draw = self.spawn_shapes((-1, 0), (1, 0), (-1, 1))

    def draw(self, broad):
        for x, y, c in self._to_draw:
            if x < 0 or y < 0:
                continue
            broad[y][x] = c

    def clear(self, broad):
        for x, y, c in self._to_draw:
            broad[y][x] = EMPTY_SQAURE

    def next(self, broad, move=None):
        # print(self)
        # print('before clear')
        # (self._to_draw)
        self.clear(broad)
        if move is 'D':
            self._y += 1
            self.move()
        elif move is 'L':
            self._x -= 1
            self.move()
        elif move is 'R':
            self._x += 1
            self.move()
        elif move is 'U':
            self.rotate(direction=0)

        # print('before draw')
        # print(self._to_draw)
        self.draw(broad)


class Game:
    global EMPTY_SQAURE
    global TYPES
    global COLORS

    def __init__(self, w, h):
        self._width = w  # broad width
        self._height = h  # broad height
        self._broad = []  # matrix for game broad
        self.init_broad()
        self._pieces = None
        self._next_pieces = None
        self._screen = None
        self._win = None
        self.init_curses()

    def init_curses(self):
        self._screen = curses.initscr()
        curses.curs_set(0)
        sh, sw = self._screen.getmaxyx()
        self._win = curses.newwin(sh, sw, 0, 0)
        self._win.keypad(1)
        self._win.timeout(100)

    def set_block(self, x, y, ch):
        """
        :param x,y: corrdinatesj
        :param ch: a char used to fill the block
        :return: null
        """
        self._broad[x][y] = ch

    def init_broad(self):
        self._broad = [[EMPTY_SQAURE for x in range(self._width)] for y in range(self._height)]
        logger.info(f'init_broad for {self._width} * {self._height}')
        logger.info(self._broad)

    def gen_pieces(self):
        self._pieces = Pieces(random.choice(TYPES), random.choice(COLORS))
        self._next_pieces = Pieces(random.choice(TYPES), random.choice(COLORS))
        logger.info(f' current pieces gen: {self._pieces._type}  next : {self._next_pieces._type}  ')

    def draw_pieces(self):
        if self._pieces is None:
            logger.info(f' current pieces is None return ')
            return
        self._pieces.draw(self._broad)

    def step(self, action=None):

        logger.info(f' step action: {action} ')
        self._pieces.next(self._broad, action)
        self.show_broad_curses()
        # self.set_block(1, 3, 'h')

    def show_broad(self):
        # os.system('cls')
        for r in self._broad:
            print(r)
        print('\n')

    def show_broad_curses(self):
        for j in range(self._height):
            for i in range(self._width):
                # print(f'{j},{i}')
                if self._broad[j][i] == ' ':
                    self._win.addch(j, i, ord(' '))
                else:
                    self._win.addch(j, i, curses.ACS_BLOCK)

    def run(self):
        self.gen_pieces()
        loop_count = 0
        while True:
            key = self._win.getch()
            time.sleep(0.1)  # every loop takes 0.1 second
            loop_count += 1
            if loop_count % 5 == 0:
                self.step('D')
            if key == curses.KEY_UP:
                self.step('U')
            if key == curses.KEY_LEFT:
                self.step('L')
            if key == curses.KEY_RIGHT:
                self.step('R')
            if key == curses.KEY_DOWN:
                self.step('D')
            """
            actionlist = ['D'] * 1 + ['U'] * 4 + ['D'] * 3
            for action in actionlist:
                time.sleep(0.5)
                self.step(action)
            """


if __name__ == '__main__':
    game = Game(10, 20)
    game.run()
