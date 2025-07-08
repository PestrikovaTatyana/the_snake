from math import log
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
# Константа информационного меню:
INFO_LINES: str = f'Змейка\n{" " * 4}Нажмите ESC - для выхода{" " * 4}'
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
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Применяется в дочернем классе Snake."""
        raise NotImplementedError(f'Пропущен метод в описании класса'
                                  f' {type(self).__name__}.')

    def draw_cell(
            self,
            color_cell: tuple,
            position: tuple
    ):
        """Отрисовывает новое положение объекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color_cell, rect)
        # Отрисовка границы применяется только к занятым ячейкам.
        if color_cell != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Дочерний класс для экземпляров stone, poison, apple."""

    def randomize_position(self, busy_cells: list[tuple]):
        """Метод для изменения положения экземпляров Apple,
        сравнение ведется по всем занятым ячейкам.
        """
        self.position = choice(tuple(ALL_CELLS - set(busy_cells)))

    def __init__(
            self,
            busy_cells: list[tuple] | None = None,
            body_color: tuple = APPLE_COLOR
    ):
        super().__init__(body_color)
        self.randomize_position(busy_cells or [])

    def draw(self):
        """Метод отрисовки экземпляров stone, poison, apple."""
        self.draw_cell(self.body_color, self.position)


class Snake(GameObject):
    """Дочерний класс для экземпляра snake."""

    def __init__(
            self,
            body_color: tuple = SNAKE_COLOR
    ):
        super().__init__(body_color)
        self.reset()
        self.direction = RIGHT  # В первый раз змейка стартует вправо

    def get_head_position(self):
        """Возврат координат головы змейки."""
        return self.positions[0]

    def draw(self):
        """Отрисовка змейки. Затирание следа."""
        # Отрисовка головы змейки.
        self.draw_cell(SNAKE_COLOR, self.get_head_position())
        # Затирание следа змейки. Если нашла яблоко self.last==[]
        # и ячейка не затирается.
        while self.last:
            self.draw_cell(BOARD_BACKGROUND_COLOR, self.last.pop())

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
        # Покинутые змеёй ячейки складываем в self.last.
        # Если просто ползет или попала в камень - одна ячейка,
        # если столкнулась с ядом - две,
        # если нашла яблоко self.last не пополняется.
        # Нужен методу Snake.draw, где такие ячейки затираются.
        while self.length < len(self.positions):
            self.last.append(self.positions.pop())

    def reset(self) -> None:
        """Возврат змейки в исходное состояние, старт с
        другого направления движения.
        """
        # Задает стартовое направление движения случайным образом.
        # Устанавливает настройки змейки в первоначальные.
        self.direction = choice((UP, RIGHT, DOWN, LEFT))
        self.positions = [BOARD_CENTER]
        self.length = 1
        self.last: list[tuple[int, int]] = []


def save_score(data_set_name: str, score: int):
    """Сохраняет в файл результат лучшей игры."""
    data_set = open(data_set_name, 'w')
    data_set.write(str(score))


def read_score(data_set_name='score.txt', high_score: int = 0):
    """Чтение лучшего результата из файла."""
    # Если файл не может быть прочитан или в файле не число,
    # то лучшим результатом принять результат текущей сессии игр.
    try:
        with open(data_set_name, 'r') as f:
            if line := next(f, '').strip():
                return int(line) if line.isdigit() else high_score
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
    # Очистка поля
    screen.fill(BOARD_BACKGROUND_COLOR)

    # Сравнение текущего результата с рекордным, запись нового рекорда.
    if high_score < snake.length:
        save_score('score.txt', snake.length)
        high_score = snake.length

    snake.reset()
    for index, item in enumerate(items):
        item_busy_positions = [items[num].position for num in range(index)]
        item.randomize_position([*snake.positions, *item_busy_positions])
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

        head_pos = snake.get_head_position()

        # Объединенная обработка встречи змейки с яблоком или ядом.
        if head_pos in (apple.position, poison.position):
            # Создаю список занятых ячеек. Голова змеи или в яблоке, или в яде,
            # поэтому по змее беру срез, чтобы не задваивать голову.
            busy = [*snake.positions[1:], *(item.position for item in items)]
            delta = 1 if head_pos == apple.position else -1
            snake.length += delta
            (apple if delta > 0 else poison).randomize_position(busy)
            speed = int(SPEED * log(3 + snake.length / 4))

            if snake.length == 0:            # Погибла от яда
                # Сбрасываю скорость, проверяю счет, перезапускаю игру.
                speed, high_score = update_game(snake, items, high_score)

        # Условия завершения игры.
        elif any((
            head_pos == stone.position,      # Угодила в камень
            head_pos in snake.positions[4:]  # Откусила хвост
        )):
            # Сбрасываю скорость, проверяю счет, перезапускаю игру.
            speed, high_score = update_game(snake, items, high_score)

        snake.draw()
        [item.draw() for item in items]
        pg.display.set_caption(f'{INFO_LINES} Лучший результат: {high_score}')
        pg.display.update()


if __name__ == '__main__':
    main()
