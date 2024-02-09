from random import randint, choice
from string import ascii_lowercase


class GameException(Exception):
    pass


class InitialException(GameException):
    pass


class Ship:
    MARK_CELL = 1
    MARK_CELL_KILL = 'X'

    def __init__(self, length, tp=1, x=None, y=None):
        self._length: int = length
        self._tp: int = tp
        self._x: int = x
        self._y: int = y
        # self._cells = [self.MARK_CELL for _ in range(length)]
        ##########################################################
        self._cells = [i + 1 for i in range(length)]
        # self._cells[0] = self.MARK_CELL_KILL
        ##########################################################
        self._is_move = False if any(map(lambda x: x == self.MARK_CELL_KILL, self._cells)) else True
        # self._is_move = True

    def set_start_coords(self, x, y):
        self._x, self._y = x, y

    def get_start_coords(self) -> tuple:
        return self._x, self._y

    def move(self, go) -> tuple:
        if self._is_move:
            if self._tp == 1:
                return self._x + go, self._y
            if self._tp == 2:
                return self._x, self._y + go
        return self._x, self._y

    @staticmethod
    def contour(cell) -> list:
        contour = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        result = []
        for i, j in cell:
            for dx, dy in contour:
                cell_contour = i + dx, j + dy
                result.append(cell_contour)
        return result

    def build_ship_tuples(self) -> list:
        result = []
        for i in range(self._length):
            if self._tp == 1:
                result.append((self._x + i, self._y))
            if self._tp == 2:
                result.append((self._x, self._y + i))
        return result

    def is_collide(self, ship) -> bool:
        ship_1 = self.build_ship_tuples()
        ship_2 = ship.build_ship_tuples()
        result = set(ship_1) & set(self.contour(ship_2))
        return len(result) > 0

    def is_out_pole(self, size) -> bool:
        if self._tp == 1:
            return not (self._x + self._length < size and self._x in range(size))
        if self._tp == 2:
            return not (self._y + self._length < size and self._y in range(size))

    def __getitem__(self, item):
        return self._cells[item]

    def __setitem__(self, key, value):
        self._cells[key] = value


class GamePole:
    MARK_WATER = '-'
    MARK_CONTOUR = '+'

    def __init__(self, size):
        self._size = size
        self._ships = []
        self._ships_ghost = []
        self._pole = [[self.MARK_WATER for _ in range(size)] for _ in range(size)]

    def __build_ships_stek(self):
        ships_collection = []
        deck = 4
        var = [(i + 1, j) for i, j in enumerate(range(deck, 0, -1))]
        for a, b in var:
            for _ in range(b):
                ship = Ship(a, tp=randint(1, 2))
                ships_collection.append(ship)
        ships_collection.reverse()
        return ships_collection

    def init(self):
        self.__install()
        self.__draw_pole()

    def __install(self):
        for ship in self.__build_ships_stek():
            while True:
                ship.set_start_coords(
                    randint(0, self._size - 1),
                    randint(0, self._size - 1)
                )
                if not ship.is_out_pole(self._size):
                    result = any([check_ship.is_collide(ship) for check_ship in self._ships])
                    if not result:
                        self._ships.append(ship)
                        break

    def get_ships(self):
        return self._ships

    def get_ships_move(self):
        return [x for x in self._ships_ghost]

    @staticmethod
    def __check_go_perimetr(go, coord, size, ln):
        return go + coord in range(0, size - ln)

    @staticmethod
    def __check_go_collision(ghost_ship, ships, ghost_ships):
        result = []
        cnt = 1
        if len(ghost_ships) == 0:
            for x in range(len(ships)):
                if ships[x]._length != ghost_ship._length:
                    if ghost_ship.is_collide(ships[x]):
                        result.append(ships[x])
        else:
            for x in range(len(ghost_ships)):
                cnt += 1
                if ghost_ship.is_collide(ghost_ships[x]):
                    result.append(ghost_ships[x])
            for x in range(cnt, len(ships)):
                if ghost_ship.is_collide(ships[x]):
                    result.append(ships[x])
        return not len(result) > 0

    def __is_collision_is_perimert(self, ship_ln, ship_tp, ship, go, ship_axis):
        collision = self.__check_go_collision(Ship(
            ship_ln,
            ship_tp,
            ship.move(go)[0],
            ship.move(go)[1]),
            self._ships,
            self._ships_ghost
        )
        perimetr = self.__check_go_perimetr(
            go,
            ship_axis,
            self._size,
            ship_ln
        )
        return collision, perimetr

    def __calculate_go(self, go, ship, ship_axis, ship_ln, ship_tp):
        collision, perimetr = self.__is_collision_is_perimert(
            ship_ln,
            ship_tp,
            ship,
            go,
            ship_axis
        )
        if not (collision and perimetr):
            go *= -1
        else: go
        collision, perimetr = self.__is_collision_is_perimert(
            ship_ln,
            ship_tp,
            ship,
            go,
            ship_axis
        )
        if not (collision and perimetr):
            go = 0
        self._ships_ghost.append(Ship(
            ship_ln,
            ship_tp,
            ship.move(go)[0],
            ship.move(go)[1],
        ))
        return go

    def move_ships(self):
        self.reset_pole()
        for ship in self._ships:
            cell = 0
            positive = 1
            negative = -1
            go = choice([positive, negative])
            if ship._tp == 1:
                go_result = self.__calculate_go(
                    go,
                    ship,
                    ship._x,
                    ship._length,
                    ship._tp
                )
                for i in range(ship._length):
                    for y, x in [ship.move(go_result)]:
                        self._pole[x][y + i] = ship._cells[cell]
                        cell += 1
                        contour = Ship.contour([(y + i, x)])
                        self.__fill_contour(contour)
            if ship._tp == 2:
                go_result = self.__calculate_go(
                    go,
                    ship,
                    ship._y,
                    ship._length,
                    ship._tp
                )
                for i in range(ship._length):
                    for y, x in [ship.move(go_result)]:
                        self._pole[x + i][y] = ship._cells[cell]
                        cell += 1
                        contour = Ship.contour([(y, x + i)])
                        self.__fill_contour(contour)

    def __draw_pole(self):
        for ship in self._ships:
            start_coord = ship.get_start_coords()
            x = start_coord[0]
            y = start_coord[1]
            if ship._tp == 1:
                for i in range(ship._length):
                    self.__fill_position(x + i, y, ship._cells[i])
            if ship._tp == 2:
                for i in range(ship._length):
                    self.__fill_position(x, y + i, ship._cells[i])

    def __fill_position(self, x, y, cell):
        self._pole[y][x] = cell
        contour = Ship.contour([(x, y)])
        self.__fill_contour(contour)

    def __fill_contour(self, contour, verbose_contour=False):
        for b, a in contour:
            if a in range(0, self._size) and b in range(0, self._size):
                if self._pole[a][b] == self.MARK_WATER:
                    if verbose_contour:
                        self._pole[a][b] = self.MARK_CONTOUR
                    else:
                        self._pole[a][b] = self.MARK_WATER

    def show(self):
        # self.__draw_pole()
        abc = list(map(lambda x: x, ascii_lowercase))
        print('  ', ' '.join([abc[x] for x in range(self._size)]))
        print('  ', ' '.join([str(x) for x in range(self._size)]))
        for num, line in enumerate(self._pole):
            print(str(num).rjust(2, '0'), *line)

    def get_pole(self):
        return tuple(tuple(self.MARK_WATER if type(i) is str else i for i in line)
                     for line in self._pole)

    def reset_pole(self):
        self._pole = [[self.MARK_WATER for _ in line] for line in self._pole]
        return self._pole


SIZE_GAME_POLE = 10

pole = GamePole(SIZE_GAME_POLE)
pole.init()
pole.show()
print()
pole.move_ships()
pole.show()


print('-' * 30)
print('ships:')
for num, i in enumerate(pole.get_ships()):
    print(f'- {str(num+1).rjust(2, "0")} ln: {i._length} | tp: {i._tp} | ({i._x}, {i._y}) | '
          f'cells: {i._cells} | move: {i._is_move}')

print('-' * 30)
print('ships move:')
for num, i in enumerate(pole.get_ships_move()):
    print(f'- {str(num+1).rjust(2, "0")} ln: {i._length} | tp: {i._tp} | ({i._x}, {i._y}) | '
          f'cells: {i._cells} | move: {i._is_move}')













