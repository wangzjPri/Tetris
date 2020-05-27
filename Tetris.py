import logging
import random
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EMPTY_SQAURE = '0'
TYPES = [x for x in range(6)]
COLORS = ['r', 'g', 'b', 'o']
COLORS = ['x']
MOVE = ['L', 'R', 'U', 'D']  # 


class Pieces:
    """
    0: ▉▉  1: ▉ 2:  ▉▉▉  3:     ▉▉  4 :   ▉▉    5:      ▉     6:   ▉▉▉
       ▉▉     ▉         ▉       ▉▉            ▉▉        ▉▉▉        ▉
                ▉
                ▉
    """

    def __init__(self, type, color):
        self.orange_ = """
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
        self.init_matrix()
        self._rotate_count = [0 for x in range(7)]  # rotate count for every type of shape

    def spawn_shapes(self, b, c, d):
        x1, y1 = b
        x2, y2 = c
        x3, y3 = d
        return [(self._x, self._y, self._color), (self._x + x1, self._y + y1, self._color)
            , (self._x + x2, self._y + y2, self._color), (self._x + x3, self._y + y3, self._color)
                ]  # 2x2 matrix

    def _rotate_index(self, direction, type, mod):
        if direction == 0:
            self._rotate_count[type] += 1
        elif direction == 1:
            self._rotate_count[type] -= 1
        if self._rotate_count[type] < 0:
            self._rotate_count[type] = mod - 1
        if self._rotate_count[type] > mod - 1:
            self._rotate_count[type] = 0;
        return self._rotate_count[type]

    def rotate(self, direction=0):  # 0 for right , 1 for left
        type = self._type
        if type is 0:
            return  # no change for square ^^
        elif type is 1:
            self._type1_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type1_rotates[self._rotate_index(direction, type, 2)]
        elif type is 2:
            self._type2_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type2_rotates[self._rotate_index(direction, type, 2)]
        elif type is 3:
            self._type3_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type3_rotates[self._rotate_index(direction, type, 2)]
        elif type is 4:
            self._type4_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type4_rotates[self._rotate_index(direction, type, 2)]
        elif type is 5:
            self._type5_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type5_rotates[self._rotate_index(direction, type, 2)]
        elif type is 6:
            self._type6_rotates = [self.spawn_shapes((0, 1), (0, 2), (0, 3)),
                                   self.spawn_shapes((0, 1), (0, 2), (0, 3))]
            self._to_draw = self._type6_rotates[self._rotate_index(direction, type, 2)]

    def init_matrix(self):
        type = self._type
        if type is 0:
            self._to_draw = self.spawn_shapes((1, 0), (0, 1), (1, 1))
        elif type is 1:
            self._to_draw = self.spawn_shapes((0, 1), (0, 2), (0, 3))
        elif type is 2:
            self._to_draw = self.spawn_shapes((1, 0), (2, 0), (2, 1))
        elif type is 3:
            self._to_draw = self.spawn_shapes((1, 0), (-1, 1), (0, 1))
        elif type is 4:
            self._to_draw = self.spawn_shapes((1, 0), (1, 1), (2, 1))
        elif type is 5:
            self._to_draw = self.spawn_shapes((-1, 1), (0, 1), (1, 1))
        elif type is 6:
            self._to_draw = self.spawn_shapes((1, 0), (2, 0), (0, 1))

    def draw(self, broad):
        for x, y, c in self._to_draw:
            broad[y][x] = c

    def clear(self, broad):
        for x, y, c in self._to_draw:
            broad[y][x] = '0'

    def next(self, broad, move=None):
        # print(self)
        # print('before clear')
        # (self._to_draw)
        self.clear(broad)
        if move is 'D':
            self._y += 1
            self.init_matrix()
        elif move is 'L':
            self._x -= 1
            self.init_matrix()
        elif move is 'R':
            self._x += 1
            self.init_matrix()
        elif move is 'U':
            self._x += 1
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
        self._pieces.next(self._broad, action)
        self.show_broad()
        # self.set_block(1, 3, 'h')

    def show_broad(self):
        os.system('cls')
        for r in self._broad:
            print(r)

    def run(self):
        # while(True):
        self.gen_pieces()
        self.step()
        actionlist = ['D'] * 5 + ['L'] * 2 + ['R'] * 2 + ['D'] * 3
        for action in actionlist:
            time.sleep(0.5)
            self.step(action)
        pass


if __name__ == '__main__':
    game = Game(10, 20)
    game.run()
