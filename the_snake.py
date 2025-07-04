from math import log
from random import choice
from re import findall

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MODUL = (640, 480)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_CENTER = (320, 240)
# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
# Игровые цвета:
BOARD_BACKGROUND_COLOR = (245, 245, 245)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (211, 211, 211)
POISON_COLOR = (255, 255, 0)
FONT_COLOR = (40, 40, 40)
# Скорость движения змейки:
SPEED = 5
# Начальная длина змейки:
START_LENGTH = 1
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)
# Заголовок окна игрового поля:
info_lines: str = 'Змейка\n     Нажмите ESC - для выхода    '
pg.display.set_caption(info_lines)
# Настройка времени:
clock = pg.time.Clock()
# Константный словарь направлений:
directions = {
    (DOWN, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (UP, pg.K_LEFT): LEFT,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
}


# Описание родительского класса GameObject
# и дочерних - Snake и Apple.
class GameObject:
    """Родительский класс для всех объектов игры."""

    _busy_cells: list = [(BOARD_CENTER)]

    def __init__(
            self,
            body_color: tuple | None = None,
            position: tuple = BOARD_CENTER
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Применяется в дочернем классе Snake"""
        raise AttributeError('Пропущен метод в описании класса ' + str(
            self.__class__.__name__))

    def draw_cell(self, position, color_cell: tuple = BOARD_BACKGROUND_COLOR):
        """Отрисовывает новое положение объекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color_cell, rect)


class Apple(GameObject):
    """Дочерний класс для экземпляров stone, poison, apple."""

    def randomize_position(self):
        """Метод для изменения положения экземпляров Apple,
        сравнение ведется по всем занятым ячейкам аттрибута
        родительского класса GameObject._busy_cells.
        """
        while True:
            random_cell = (choice(range(0, SCREEN_WIDTH, 20)),
                           choice(range(0, SCREEN_HEIGHT, 20)))
            if random_cell not in GameObject._busy_cells:
                try:
                    GameObject._busy_cells.remove(self.position)
                except ValueError:
                    pass
                self.position = random_cell
                break

        GameObject._busy_cells.insert(0, self.position)

    def __init__(
            self,
            body_color: tuple = APPLE_COLOR
    ):
        super().__init__(body_color)
        self.body_color = body_color
        self.randomize_position()


class Snake(GameObject):
    """Дочерний класс для экземпляра snake."""

    def __init__(
            self,
            body_color: tuple = SNAKE_COLOR
    ):
        super().__init__(body_color)
        self.positions: list[tuple] = [(BOARD_CENTER)]
        self.length: int = 1
        self.direction: tuple = RIGHT
        self.trace: tuple | None = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def draw(self):
        """Дорисовать голову."""
        # Отрисовка головы змейки.
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        # Затирание в родительском GameObject методе draw_cell перенесено
        # в move(), в случае яда в self.trace оказывается сразу 2 клетки.

    def update_direction(self, new_direction):
        """Метод обновления направления после нажатия на кнопку."""
        self.direction = new_direction

    def get_new_head(self):
        """Обновление кортежа головы. Используется в self.move()
        и в теле match-case функции main, чтобы проверить положение
        головы до отрисовки змейки.
        """
        return tuple(map(lambda x, y, MODUL: (x + y * GRID_SIZE) % MODUL,
                         self.get_head_position(), self.direction, MODUL))

    def move(self):
        """Обновление положения змейки."""
        self.positions.insert(0, self.get_new_head())
        GameObject._busy_cells.insert(3, self.positions[0])
        GameObject._busy_cells = GameObject._busy_cells[:(3 + self.length)]
        while self.length < len(self.positions):
            self.trace = self.positions.pop()
            self.draw_cell(self.trace)

    def reset(self):
        """Возврат змейки в исходное состояние, старт спше
        другого направления движения.
        """
        # Очистить игровое поле.
        screen.fill(BOARD_BACKGROUND_COLOR)
        # Откатить изменяемые в ходе игры настройки к первоначальным.
        self.positions.clear()
        self.positions.append(BOARD_CENTER)
        GameObject._busy_cells.insert(3, self.positions[0])
        self.length = 1
        self.trace = None
        # Изменить только направление движения на случайное.
        self.direction = choice((UP, RIGHT, DOWN, LEFT))


def save_score(data_set_name: str, score: int):
    """Создает файл и сохраняет в него результат лучшей игры."""
    data_set = open(data_set_name, 'w')
    data_set.write('Лучший результат:  ' + str(score))


def read_score(data_set_name):
    """Чтение лучшего результата или сообщение о том, что
    игра первая.
    """
    high_score = 'Это Ваша первая игра!'
    try:
        with open(data_set_name, 'r') as f:
            for line in f:
                try:
                    high_score = line.strip()
                except ValueError:
                    pass
            f.close()
    except FileNotFoundError:
        pass
    return high_score


def handle_keys(snake_obj: Snake):
    """Функция обработки действий пользователя.
    На клавиатуре отвечает на действия клавиш: UP, DOWN, LEFT, RIGHT, ESC.
    Управляемый объект получает новое значение атрибута direction.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            else:
                snake_obj.update_direction(
                    directions.get((snake_obj.direction, event.key),
                                   snake_obj.direction)
                )


def update_game(snake_obj: Snake, items: list[Apple]):
    """Сохранение рекордного результата. Перезапуск игры с новой
    расстановкой предметов и маленькой змейкой в центре.
    """
    # Сравнение текущего результата с рекордным, запись нового рекорда.
    high_score = read_score('score.txt')
    try:
        numbers_score = int(''.join(findall(r'\b\d+\b', high_score)))
    except TypeError:
        numbers_score = 0

    if numbers_score < snake_obj.length:
        save_score('score.txt', snake_obj.length)

    snake_obj.reset()
    for item in items:
        item.randomize_position()
    return SPEED


def main():
    """Основная логика игры"""
    # Инициализация PyGame:
    pg.init()

    # Создание экземпляров классов.
    snake = Snake()
    items = [Apple(STONE_COLOR), Apple(POISON_COLOR), Apple()]
    stone, poison, apple = items
    high_score = read_score('score.txt')
    # Изменение скорости игры, сначала равно 0.
    speed = SPEED

    while True:

        clock.tick(speed)
        handle_keys(snake)
        snake.move()

        match snake.positions[0]:
            case apple.position:
                snake.length += 1
                apple.randomize_position()
                # Плавное изменение скорости по логарифму.
                speed = int(SPEED * log(3 + snake.length / 4))
            case poison.position:
                snake.length -= 1
                if snake.length > 0:
                    poison.randomize_position()
                else:
                    speed = update_game(snake, items)
            case stone.position:
                speed = update_game(snake, items)
            case _:
                if snake.positions[0] in snake.positions[4:]:
                    speed = update_game(snake, items)

        for item in items:
            item.draw_cell(item.position, item.body_color)
        snake.draw()
        high_score = read_score('score.txt')
        pg.display.set_caption(info_lines + high_score + '\n')
        pg.display.update()


if __name__ == '__main__':
    main()
