import logging
import random
import time
import os
import curses
import copy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='Tetris.log', filemode='w')
logger = logging.getLogger(__name__)

EMPTY_SQAURE = ' '
TYPES = [x for x in range(6)]
COLORS = ['r', 'g', 'b', 'o']
# COLORS = ['x']
MOVE = ['L', 'R', 'U', 'D']  # 
BROAD_HEIGHT = 20
BROAD_WIDTH = 16


class Pieces:
    """
    0: ▉▉  1: ▉ 2:  ▉▉▉  3:     ▉▉  4 :   ▉▉    5:      ▉     6:   ▉▉▉
       ▉▉     ▉       ▉        ▉▉          ▉▉          ▉▉▉         ▉
              ▉
              ▉
    """
    global BROAD_WIDTH
    global BROAD_HEIGHT

    def __init__(self, type, color,x=int(BROAD_WIDTH/2),y=0):
        """
        :param x:  x
        :param y:  y
        :param type:  0 ~6
        :param color: 'r': red  ,'g': green  , 'b': blue , 'o': orange
        """
        self._x = x
        self._y = y
        self._color = color
        self._type = type
        self._pre_to_draw = []
        self._to_draw = []
        self._pos = None
        self._pre_pos = None
        self.init_matrix()
        self._alive = True
        self._callback = None
        self._rotate_count = [0 for x in range(7)]  # rotate count for every type of shape
        self._pre_rotate_count = []  # prev  rotate count 

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
            type1_rotates = self.angle_to_points(self.type1_angle)
            self._to_draw = type1_rotates[choice]
            self._pos = self.type1_angle[choice]
        elif type is 2:
            choice = self._rotate_index(direction, type, 4)
            type2_rotates = self.angle_to_points(self.type2_angle)
            self._to_draw = type2_rotates[choice]
            self._pos = self.type2_angle[choice]
        elif type is 3:
            choice = self._rotate_index(direction, type, 2)
            type3_rotates = self.angle_to_points(self.type3_angle)
            self._to_draw = type3_rotates[choice]
            self._pos = self.type3_angle[choice]
        elif type is 4:
            choice = self._rotate_index(direction, type, 2)
            type4_rotates = self.angle_to_points(self.type4_angle)
            self._to_draw = type4_rotates[choice]
            self._pos = self.type4_angle[choice]
        elif type is 5:
            choice = self._rotate_index(direction, type, 4)
            type5_rotates = self.angle_to_points(self.type5_angle)
            self._to_draw = type5_rotates[choice]
            self._pos = self.type5_angle[choice]
        elif type is 6:
            choice = self._rotate_index(direction, type, 4)
            type6_rotates = self.angle_to_points(self.type6_angle)
            self._to_draw = type6_rotates[choice]
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
        #logger.info(f'draw pieces :  {self._to_draw} before  broad: {broad}')
        for x, y, c in self._to_draw:
            if x >= 0 and y >= 0:
                broad[y][x] = c
                #logger.info(f'draw pieces :  {self._to_draw} after broad: {broad}')


    def clear(self, broad):
        for x, y, c in self._to_draw:
            if x >= 0 and y >= 0:
                #logger.info(f'clear pos : x: {x} y: {y}')
                #logger.info(f'clear broad: {broad}')
                broad[y][x] = EMPTY_SQAURE

    def next(self, broad, move=None):
        self._pre_to_draw = self._to_draw
        self._pre_rotate_count = self._rotate_count
        self._pre_pos = self._pos
        logger.info(f'next: {self._to_draw} ')
        last_x = self._x
        last_y = self._y
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
        die = self.check_for_border(broad, last_x, last_y, move)
        self.draw(broad)
        if die :
            self._callback.pieces_dead()

    def check_for_border(self, broad, last_x, last_y, move):
        for x, y, c in self._to_draw:
            if x < 0 or x > BROAD_WIDTH - 1:
                logger.info(f'check for border  exceed x to_draw: {self._to_draw} pre: {self._pre_to_draw} ')
                self._to_draw = self._pre_to_draw  # back to last
                self._rotate_count = self._pre_rotate_count
                self._pos = self._pre_pos
                self._x = last_x
                self._y = last_y
                return False
            if y > BROAD_HEIGHT - 1:
                self._alive = False
                self._to_draw = self._pre_to_draw  # back to last
                self._x = last_x
                self._y = last_y

                return True
            if broad[y][x] != EMPTY_SQAURE:
                self._to_draw = self._pre_to_draw  # back to last
                self._rotate_count = self._pre_rotate_count
                self._pos = self._pre_pos
                self._x = last_x
                self._y = last_y
                if move is 'D':
                    return True
                else:
                    return False
        return False

    def set_dead_callback(self, callback):
        self._callback = callback
        # callback.pieces_dead()


"""
scoreing chart
0-1 100 400 900 2000    1 per line
2-3 200 800 1800    4000    2 per line
4-5 300 1200    2700    6000    3 per line
6-7 400 1600    3600    8000    4 per line
8+  500 2000    4500    10000   5 per line
"""

SCOREING =[100,400,900,2000]


class Game:
    global EMPTY_SQAURE
    global TYPES
    global COLORS
    global SCOREING

    def __init__(self, w, h):
        self._width = w  # broad width
        self._height = h  # broad height
        self._level = 0  # game level
        self._score = 0  # game score
        self._broad = []  # matrix for game broad
        self._broad2 = []  # matrix for next pieces display 4*4
        self._empty_line=[]
        self.init_broad()
        self._pieces = None
        self._next_pieces = None
        self._screen = None
        self._win = None
        self._win2 = None
        self._dx = 5
        self._dy = 5
        self.init_curses()
        self.pause = False

    def init_curses(self):
        self._screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        # sh, sw = self._screen.getmaxyx()
        self._win = curses.newwin(self._height + self._dy + 1, self._width + self._dx + 1, self._dy - 3, self._dx)
        self._win2 = curses.newwin(self._height + self._dy + 1, self._width + self._dx + 1, self._dy - 3, int(self._dx+self._width*1.5))
        self._win.keypad(1)
        self._win.timeout(0)
        self._win.border()
        self._win2.keypad(1)
        self._win2.timeout(0)
        self._win2.border()

    def set_block(self, x, y, ch):
        """
        :param x,y: corrdinatesj
        :param ch: a char used to fill the block
        :return: null
        """
        self._broad[x][y] = ch

    def init_broad(self):
        self._empty_line = [EMPTY_SQAURE for x in range(self._width)] 
        self._broad = [[EMPTY_SQAURE for x in range(self._width)] for y in range(self._height)]
        self._broad2 = [[EMPTY_SQAURE for x in range(4)] for y in range(4)]
        logger.info(f'init_broad for {self._width} * {self._height}')

    def pieces_dead(self):
        self.check_for_clear()
        self._next_pieces.clear(self._broad2)
        self._pieces = self._next_pieces
        self._pieces.set_dead_callback(self)
        self._next_pieces = Pieces(random.choice(TYPES), random.choice(COLORS),x=1,y=1)

    def gen_pieces(self):
        self._pieces = Pieces(random.choice(TYPES), random.choice(COLORS))
        self._pieces.set_dead_callback(self)
        self._next_pieces = Pieces(random.choice(TYPES), random.choice(COLORS),x=1,y=1)
        logger.info(f' current pieces gen: {self._pieces._type}  next : {self._next_pieces._type}  ')

    def clear_pieces(self):
        if self._pieces is None:
            logger.info(f' current pieces is None return ')
            return
        self._pieces.clear(self._broad)

    def step(self, action=None):
        logger.info(f' step action: {action} ')
        self._pieces.next(self._broad, action)
        self._win2.addstr(self._dy, self._dx, f'Score: {self._score}')
        self.show_broad_curses()
        self.show_next_pieces()

    def show_broad(self):
        # os.system('cls')
        for r in self._broad:
            print(r)
        print('\n')

    def show_broad_curses(self):
        for l in self._broad:
            logger.info(f' show_broad_curses: {l} ')
        for j in range(self._height):
            for i in range(self._width):
                if self._broad[j][i] == EMPTY_SQAURE:
                    self._win.addch(j + self._dy, i + self._dx - 2, ord(' '))
                else:
                    self._win.addch(j + self._dy, i + self._dx - 2, ord('X'))

    def show_next_pieces(self):
        self._next_pieces.next(self._broad2)
        self._win2.addstr(self._dy+2, self._dx , 'next block : ')
        for j in range(4):
            for i in range(4):
                if self._broad2[j][i] == EMPTY_SQAURE:
                    self._win2.addch(j + self._dy+4, i + self._dx , ord(' '))
                else:
                    self._win2.addch(j + self._dy+4, i + self._dx , ord('X'))


        
        

    def end_game(self):
        self._broad = [[EMPTY_SQAURE for x in range(self._width)] for y in range(self._height)]
        self._win2.addstr(int(BROAD_HEIGHT/2), self._dx, 'Game Over ,\n Play again? Y/N')
        self._win2.timeout(-1)
        self.pause = True
        key = self._win2.getch()
        if key == ord('n'):
            close_curses()
        elif key == ord('y') :
            self.pause = False    
        return

    def check_for_clear(self):
        upper_part = []
        down_part = []
        cleared = 0
        new_broad = []
        for i, l in enumerate(self._broad):
            if i == 0 and l != self._empty_line:
                logger.info('broad is full end game')
                return self.end_game();

            if EMPTY_SQAURE not in l:
                cleared += 1
                logger.info(f'check for clear {cleared} ')
            elif cleared == 0:
                upper_part.append(l)
            else : 
                down_part.append(l)
        if cleared is 0:
            return
        for i in range(cleared):
            new_broad.append(copy.deepcopy(self._empty_line))
        if upper_part is not []:
            for lu in upper_part:
                new_broad.append(lu)
        if down_part is not []:
            for ld in down_part:
                new_broad.append(ld)
        self._broad = new_broad
        self.clear_pieces()
        self._score += SCOREING[cleared-1]
        logger.info(f'check for clear new broad   len : {len(new_broad)} len1: {cleared} len2: {len(upper_part)} len3: {len(down_part)}')

    def close_curses(self):
        curses.nocbreak()  # 关闭字符终端功能（只有回车时才发生终端）
        self._win.keypad(0)
        curses.echo()  # 打开输入回显功能
        curses.endwin()

    def run(self):
        self.gen_pieces()
        loop_count = 0
        while True:
            time.sleep(0.01)  # every loop takes 0.01 second
            if self.pause : 
                continue
            key = self._win.getch()
            self._win2.refresh()

            loop_count += 1
            if loop_count % 50 == 0:
                self.step('D')
            if key == curses.KEY_UP:
                self.step('U')
            if key == curses.KEY_LEFT:
                self.step('L')
            if key == curses.KEY_RIGHT:
                self.step('R')
            if key == curses.KEY_DOWN:
                self.step('D')
            if key == ord('q'):
                logger.info('q  pressed quit now')
                self.close_curses()
                return


if __name__ == '__main__':
    game = Game(BROAD_WIDTH, BROAD_HEIGHT)
    game.run()
