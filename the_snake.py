from math import log
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_CENTER = (640 // 2, 480 // 2)
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
SNAKE_HEAD_COLOR = (0, 135, 0)
STONE_COLOR = (211, 211, 211)
POISON_COLOR = (255, 255, 0)
FONT_COLOR = (40, 40, 40)
# Скорость движения змейки:
SPEED = 5
# Начальная длина змейки:
START_LENGTH = 1
# Константный словарь направлений:
ROTATIONS = {
    (DOWN, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (UP, pg.K_LEFT): LEFT,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
}
# Множество координат всех ячеек доски:
ALL_CELLS = {
    (x, y)
    for x in range(0, SCREEN_WIDTH, 20)
    for y in range(0, SCREEN_HEIGHT, 20)
}
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Заголовок окна игрового поля:
INFO_LINES: str = 'Змейка\n     Нажмите ESC - для выхода    '
pg.display.set_caption(INFO_LINES)
# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Родительский класс для всех объектов игры."""

    def __init__(
            self,
            body_color: tuple | None = None,
            position: tuple = BOARD_CENTER
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Применяется в дочернем классе Snake"""
        raise NameError(
            f'Пропущен метод в описании класса'
            f' {type(self).__name__}.'
        )

    def draw_cell(
            self,
            position: tuple,
            color_cell: tuple = SNAKE_COLOR
    ):
        """Отрисовывает новое положение объекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color_cell, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Дочерний класс для экземпляров stone, poison, apple."""

    def randomize_position(self, busy_cells: list[tuple]):
        """Метод для изменения положения экземпляров Apple,
        сравнение ведется по всем занятым ячейкам snake.positions,
        apple.position, stone.position, poison.position.
        """
        self.position = choice(tuple(ALL_CELLS - set(busy_cells)))

    def __init__(
            self,
            busy_cells: list[tuple] | None = None,
            body_color: tuple = APPLE_COLOR
    ):
        super().__init__(body_color)
        self.randomize_position(busy_cells if busy_cells is not None else [])


class Snake(GameObject):
    """Дочерний класс для экземпляра snake."""

    def __init__(
            self,
            body_color: tuple = SNAKE_COLOR
    ):
        super().__init__(body_color)
        self.reset()
        # В задании в первый раз змейка стартует вправо
        self.direction = RIGHT

    def get_head_position(self):
        """Возвращение координат головы змейки."""
        return self.positions[0]

    def draw(self):
        """Отрисовка змейки. Ячейки следа отрисовывать не надо,
        они такого же цвета, как и поле.
        """
        # Очищение игрового поля.
        screen.fill(BOARD_BACKGROUND_COLOR)
        # Отрисовка тела змейки.
        for position in self.positions[1:]:
            self.draw_cell(position)
        # Отрисовка головы змейки.
        self.draw_cell(self.get_head_position(), SNAKE_HEAD_COLOR)

    def update_direction(self, new_direction):
        """Метод обновления направления после нажатия на кнопку."""
        self.direction = new_direction

    def get_new_head(self):
        """Получение кортежа новой головы. Используется в self.move()."""
        return tuple(map(
            lambda x, y, modul:
            (x + y * GRID_SIZE) % modul,
            self.get_head_position(),
            self.direction,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        ))

    def move(self):
        """Обновление положения змейки."""
        self.positions.insert(0, self.get_new_head())
        while self.length < len(self.positions):
            self.traces.append(self.positions.pop())
        self.traces = [self.get_head_position()]

    def reset(self):
        """Возврат змейки в исходное состояние, старт с
        другого направления движения.
        """
        # Откатить изменяемые в ходе игры настройки к первоначальным.
        self.positions = [BOARD_CENTER]
        self.length = 1
        self.traces = [BOARD_CENTER]
        # Задание стартового направления движения случайным образом.
        self.direction = choice((UP, RIGHT, DOWN, LEFT))


def save_score(data_set_name: str, score: int):
    """Создает файл и сохраняет в него результат лучшей игры."""
    data_set = open(data_set_name, 'w')
    data_set.write(str(score))


def read_score(data_set_name='score.txt', high_score: int = 0):
    """Чтение лучшего результата или сообщение о том, что
    игра первая.
    """
    try:
        with open(data_set_name, 'r') as f:
            for line in f:
                return int(line.strip().isdigit())
            return high_score
    except (FileNotFoundError, PermissionError, ValueError):
        return high_score


def handle_keys(snake: Snake):
    """Функция обработки действий пользователя.
    На клавиатуре отвечает на действия клавиш: UP, DOWN, LEFT, RIGHT, ESC.
    Управляемый объект получает новое значение атрибута direction.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            snake.update_direction(
                ROTATIONS.get((snake.direction, event.key),
                              snake.direction)
            )


def update_game(snake: Snake, items: list[Apple], high_score: int):
    """Сохранение рекордного результата. Перезапуск игры с новой
    расстановкой предметов и маленькой змейкой в центре.
    """
    # Сравнение текущего результата с рекордным, запись нового рекорда.
    if high_score < snake.length:
        save_score('score.txt', snake.length)
        high_score = snake.length

    snake.reset()
    for index, item in enumerate(items):
        item.randomize_position(
            [*snake.positions, *(items[i].position for i in range(index))])
    return SPEED, high_score


def main():
    """Основная логика игры"""
    # Инициализация PyGame:
    pg.init()
    # Настройка игрового окна:
    screen.fill(BOARD_BACKGROUND_COLOR)

    # Создание экземпляров классов и необходимых переменных.
    snake = Snake()
    stone = Apple([*snake.positions], STONE_COLOR)
    poison = Apple([*snake.positions, stone.position], POISON_COLOR)
    apple = Apple([*snake.positions, stone.position, poison.position])
    items = [stone, poison, apple]
    high_score = read_score('score.txt')
    speed = SPEED

    while True:

        clock.tick(speed)
        handle_keys(snake)
        snake.move()

        match snake.get_head_position():
            case apple.position:
                snake.length += 1
                apple.randomize_position(
                    [
                        *snake.positions,
                        *(items[i].position for i in range(3))
                    ]
                )
                # Плавное изменение скорости по логарифму.
                speed = int(SPEED * log(3 + snake.length / 4))
            case poison.position:
                snake.length -= 1
                if snake.length > 0:
                    poison.randomize_position(
                        [
                            *snake.positions,
                            *(items[i].position for i in range(3))
                        ]
                    )
                else:
                    speed, high_score = update_game(snake, items, high_score)
            case _ as hd if hd == stone.position or hd in snake.positions[4:]:
                speed, high_score = update_game(snake, items, high_score)

        snake.draw()
        for item in items:
            item.draw_cell(item.position, item.body_color)
        pg.display.set_caption(f'{INFO_LINES} Лучший результат: {high_score}')
        pg.display.update()


if __name__ == '__main__':
    main()
