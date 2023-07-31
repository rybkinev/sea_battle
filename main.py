import random


class Cell:
    EMPTY = ' '
    SHIP = '■'
    MISS = 'T'
    HIT = 'X'


class Ship:
    def __init__(self, _size, is_horizontal):
        self.__size = _size
        self.__is_horizontal = is_horizontal
        self.__coords = []
        self.__damage = []

    @property
    def size(self):
        return self.__size

    @property
    def is_horizontal(self):
        return self.__is_horizontal

    @property
    def health(self):
        return self.__size - len(self.__damage)

    @property
    def damage(self):
        return len(self.__damage)

    def damage_deck(self, coord: tuple):
        return coord in self.__damage

    @damage.setter
    def damage(self, value: tuple):
        self.__damage.append(value)
        # self.__coords.remove(value)

    @property
    def coordinates(self):
        return self.__coords

    @coordinates.setter
    def coordinates(self, value: tuple):
        self.__coords.append(value)


class Board:
    def __init__(self, size_field):
        self.__grid = [[Cell.EMPTY for _ in range(size_field)] for _ in range(size_field)]
        self.__size = size_field

    @staticmethod
    def display(player_board, computer_board, show_computer_ships: bool = False):
        player_grid = player_board.grid
        computer_grid = computer_board.grid
        # if not len(player_grid) or not len(computer_grid):
        #     print('Поле для вывода недоступно')
        #     return
        cell_sep = ' | '
        board_sep = '  |||  '

        def append_names(grid, replace: bool = False):
            names = ['']
            names.extend([str(o) for o in range(1, len(grid) + 1)])

            board = [names.copy()]

            for r in range(len(grid)):
                _row = [names.pop(1)]
                for c in range(len(grid)):
                    cell = grid[r][c]
                    if isinstance(cell, Ship) and not cell.damage_deck((r, c)):
                        cell = Cell.SHIP
                    elif isinstance(cell, Ship) and cell.damage_deck((r, c)):
                        cell = Cell.HIT
                    if replace:
                        cell = cell.replace(Cell.SHIP, Cell.EMPTY)
                    _row.append(cell)
                board.append(_row)
            return board

        field_player = append_names(player_grid)
        field_computer = append_names(computer_grid, not show_computer_ships)

        field = []
        for i in range(len(field_computer)):
            new_row = field_player[i] + [board_sep] + field_computer[i]
            field.append(new_row)

        rows = len(field)
        cols = len(field[0])

        col_width = []
        col_width_grid = []
        for col in range(cols):
            columns = [field[row][col] for row in range(rows)]
            col_width.append(len(max(columns, key=len)))
            if col < len(field_player):
                col_width_grid.append(len(max(columns, key=len)))

        separator_field = "-+-".join('-' * n for n in col_width_grid)
        separator = separator_field + '-+ ' + board_sep + ' +-' + separator_field

        for i, row in enumerate(range(rows)):
            # if i == 1:
            #     print(separator)

            result = []
            for col in range(cols):
                item = field[row][col].rjust(col_width[col])
                result.append(item)

            print(cell_sep.join(result))
            print(separator)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        self.__size = value

    @property
    def grid(self):
        return self.__grid

    @grid.setter
    def grid(self, value):
        self.__grid = value

    def get_cell(self, x, y):
        return self.grid[x][y]

    def place_miss(self, x, y):
        self.grid[x][y] = Cell.MISS

    def place_empty(self, x, y):
        self.grid[x][y] = Cell.EMPTY

    def place_hit(self, x, y):
        self.grid[x][y].damage = (x, y)

    def is_valid_coordinate(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def is_miss_coordinate(self, x, y):
        return self.grid[x][y] == Cell.MISS

    def is_ship_coordinate(self, x, y):
        return isinstance(self.grid[x][y], Ship)

    def is_available_ship_coordinate(self, x, y):
        cell = self.grid[x][y]
        if isinstance(cell, Ship) and cell.damage_deck((x, y)):
            return False
        return True

    def is_empty_coordinate(self, x, y):
        return self.grid[x][y] == Cell.EMPTY

    def place_ship(self, ship):
        x, y = ship.coordinates[-1]
        self.grid[x][y] = ship

    def can_place_ship(self, x, y, ship):
        if ship.is_horizontal:
            return all(0 <= y + i < self.size and self.is_empty_coordinate(x, y + i) for i in range(ship.size))
        else:
            return all(0 <= x + i < self.size and self.is_empty_coordinate(x + i, y) for i in range(ship.size))

    def place_ship_with_padding(self, x, y, ship):
        for i in range(ship.size):
            if ship.is_horizontal:
                x_new = x
                y_new = y + i
            else:
                x_new = x + i
                y_new = y

            ship.coordinates = (x_new, y_new)
            self.place_ship(ship)
        self.place_miss_around_ship(ship)

    def place_miss_around_ship(self, ship: Ship):
        for x, y in ship.coordinates:
            # Заполняю клетки вокруг палубы промахами для корректной дальнейшей установки кораблей
            for j in range(-1, 2):
                x_miss = x
                y_miss = y + j
                if 0 <= x_miss < self.size and 0 <= y_miss < self.size and self.is_empty_coordinate(x_miss, y_miss):
                    self.place_miss(x_miss, y_miss)
                x_miss = x + j
                y_miss = y
                if 0 <= x_miss < self.size and 0 <= y_miss < self.size and self.is_empty_coordinate(x_miss, y_miss):
                    self.place_miss(x_miss, y_miss)

    def replace_miss_on_empty(self):
        for coord in self.coordinates:
            if self.is_miss_coordinate(*coord):
                self.place_empty(*coord)

    @property
    def grid_len(self):
        return len(self.grid)

    @property
    def coordinates(self):
        return [(x, y) for x in range(self.grid_len) for y in range(self.grid_len)]

    @property
    def available_coordinates(self):
        return [
            (x, y) for x in range(self.grid_len) for y in range(self.grid_len)
            if self.is_empty_coordinate(x, y)
        ]

    def ships_on_board(self):
        for row in self.grid:
            for cell in row:
                if isinstance(cell, Ship):
                    if cell.health > 0:
                        return True
        return False
        # return not any(Cell.SHIP in row for row in self.grid)


class Player:
    def __init__(self, name):
        self.name = name

    def make_move(self, board):
        while True:
            try:
                x = input(f"{self.name}, введите номер строки (от 1 до {board.size}): ")
                if x == 'want to win':
                    return -1, -1
                if x == 'help':
                    Game.display_help()
                    continue

                y = input(f"{self.name}, введите номер столбца (от 1 до {board.size}): ")
                if y == 'want to win':
                    return -1, -1
                if y == 'help':
                    Game.display_help()
                    continue

                x = int(x) - 1
                y = int(y) - 1

                if not board.is_valid_coordinate(x, y):
                    print(f"Некорректные координаты. Нужны целые числа от 1 до {board.size}. Попробуйте ещё раз.")
                    continue

                if (board.is_empty_coordinate(x, y)
                        or board.is_available_ship_coordinate(x, y)
                        and board.is_ship_coordinate(x, y)):
                    return x, y
                elif not board.is_empty_coordinate(x, y):
                    print('Вы уже били в эту клетку. Попробуйте еще раз')
            except ValueError:
                print("Некорректный ввод. Введите целые числа.")


class Game:
    def __init__(self, _size, _ships):
        self.size = _size
        self.ships = _ships
        self.player_board = Board(self.size)
        self.computer_board = Board(self.size)
        self.player = Player("Игрок")

    def setup(self):
        self.place_ships(self.player_board)
        self.place_ships(self.computer_board)

    def place_ships(self, board):
        self.ships.sort(reverse=True)
        for ship_size in self.ships:
            placed = False
            available_coord = board.available_coordinates
            while not placed:
                if not len(available_coord):
                    raise """Закончились доступные клетки при расстановке кораблей.
                    Попробуйте увеличить размер поля или уменьшить количество кораблей.
                    После этого попробуйте еще раз запустить игру"""

                xy = random.choice(range(len(available_coord)))
                x, y = available_coord.pop(xy)
                is_horizontal = random.choice([True, False])
                new_ship = Ship(ship_size, is_horizontal)
                if board.can_place_ship(x, y, new_ship):
                    board.place_ship_with_padding(x, y, new_ship)
                    # Board.display(self.player_board, self.computer_board)
                    # print('///////////////////////////')
                    placed = True

        board.replace_miss_on_empty()

    def player_move(self, cheat_active):
        print('Ваш ход')
        print("Ваше поле слева, справа компьютера:")
        Board.display(self.player_board, self.computer_board, cheat_active)

        while not self.check_game_over():
            x, y = self.player.make_move(self.computer_board)

            if x == -1 and y == -1:
                # код активирован до конца игры
                return True

            if self.computer_board.is_ship_coordinate(x, y):
                print("Попадание!!")
                self.computer_board.place_hit(x, y)
                ship = self.computer_board.get_cell(x, y)
                if ship.health == 0:
                    self.computer_board.place_miss_around_ship(ship)
                print('Снова Ваш ход')
                print("Ваше поле слева, справа компьютера:")
                Board.display(self.player_board, self.computer_board, cheat_active)
                continue
            else:
                print("Промах!")
                self.computer_board.place_miss(x, y)
                break

        return False

    def computer_move(self):
        coord = self.player_board.coordinates
        while not self.check_game_over():
            # x = random.randint(0, self.size - 1)
            # y = random.randint(0, self.size - 1)
            if not len(coord):
                # По идее невозможная ситуация, к этому моменту игра должна закончится
                raise """Закончились доступные ходы у компьютера"""
            ind = random.choice(range(len(coord)))
            x, y = coord.pop(ind)
            if self.player_board.is_empty_coordinate(x, y):
                print("Компьютер промахнулся.")
                self.player_board.place_miss(x, y)
                break
            elif self.player_board.is_ship_coordinate(x, y) and self.player_board.is_available_ship_coordinate(x, y):
                print("Компьютер попал в ваш корабль!")
                self.player_board.place_hit(x, y)
                ship = self.player_board.get_cell(x, y)
                if ship.health == 0:
                    self.player_board.place_miss_around_ship(ship)
                continue

    def check_game_over(self):
        return not self.player_board.ships_on_board() or not self.computer_board.ships_on_board()

    def play(self):
        self.display_about()
        self.display_help()
        self.setup()

        cheat_active = False
        while not self.check_game_over():
            result = self.player_move(cheat_active)

            if result:
                cheat_active = True
                continue

            if self.check_game_over():
                break

            print("Ход компьютера:")
            self.computer_move()

        if not self.player_board.ships_on_board():
            print("Вы проиграли! Компьютер победил.")
        else:
            print("Поздравляем! Вы победили!")

    @staticmethod
    def display_about():
        print("Добро пожаловать в игру 'Морской бой'!")
        print()
        print("'Морской бой' - игра для двух участников, в которой игроки по очереди называют, сообщают иным способом,")
        print('координаты на карте соперника.')
        print('Если у врага с этими координатами имеется "корабль", то корабль или его палуба (дека) убивается,')
        print('попавший делает еще один ход. Цель игрока: первым убить все игровые "корабли" врага.')
        print()

    @staticmethod
    def display_help():
        print('Помощь по игре')
        print()
        print('Корабли расставляются на поле в произвольном порядке и только по вертикали или горизонтали.')
        print('Соседние корабли могут располагаться в соседней клетке по диагонали')
        print('Чтобы сделать ход нужно указать последовательно сначала строку, потом столбец')
        print('И конечно же, как в любой игре с ИИ, есть секретный код чтобы открыть поле соперника)))))')
        print()


if __name__ == "__main__":
    ships = [1, 1, 1, 1, 2, 2, 3]  # Список кораблей, размещаемых на поле
    size = 6  # Размер поля

    game = Game(size, ships)
    game.play()
