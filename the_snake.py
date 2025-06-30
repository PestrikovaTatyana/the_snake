from functools import lru_cache
from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_ABSCISSA, CENTER_ORDINATE = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвета экземпляров класса Apple:
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (211, 211, 211)
POISON_COLOR = (255, 255, 0)

# Скорость движения змейки:
SPEED = 2

# Начальная длина змейки:
START_LENGTH = 1

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Описание родительского класса GameObject
# и дочерних - Snake и Apple.
class GameObject:
    """Родительский класс для всех объектов игры."""

    def __init__(
            self,
            body_color: tuple | None = None,
            position: tuple = (CENTER_ABSCISSA, CENTER_ORDINATE)
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объекты, задается внутри каждого
        дочернего класса отдельно.
        """
        pass

    def erase(self):
        """Затирает след от экземпляра, когда его нужно переставить."""
        pass


class Apple(GameObject):
    """Дочерний класс для экземпляров stone, poison, apple."""

    @staticmethod
    @lru_cache
    def get_cortege(start: int = 0, stop: int = 0, step: int = 20):
        """Кортеж для генератора случайной позиции, теперь кортежи будут
        в быстром вызове. Принимает границы поля и шаг сетки.
        """
        return tuple(range(start, stop, step))

    @staticmethod
    def randomize_position(first_cortege, second_cortege):
        """Генератор для определения новой позиции экземпляра,
        принимает 2 кортежа: 0, SCREEN_WIDTH и 0, SCREEN_HEIGHT,
        a выводит кортеж из двух координат с шагом GRID_SIZE.
        """
        while True:
            yield choice(first_cortege), choice(second_cortege)

    def __init__(
            self,
            body_color: tuple = APPLE_COLOR
    ):
        super().__init__(body_color)
        self.coordinate_producer = self.randomize_position(
            self.get_cortege(0, SCREEN_WIDTH),
            self.get_cortege(0, SCREEN_HEIGHT)
        )
        self.body_color = body_color
        self.position = tuple(self.coordinate_producer.__next__())

    def draw(self):
        """Отрисовывает новое положение объекта."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def erase(self):
        """Затирает сегмент со старым положением."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class Snake(GameObject):
    """Дочерний класс для экземпляра snake."""

    def __init__(
            self,
            positions: list[tuple] | tuple = (None,),
            position: tuple = (CENTER_ABSCISSA, CENTER_ORDINATE),
            body_color: tuple = SNAKE_COLOR,
            length: int = START_LENGTH,
            direction: tuple = RIGHT,
            next_direction: tuple | None = None,
            last: tuple | None = None
    ):
        super().__init__(body_color,
                         position)
        self.position = position
        self.body_color = body_color
        self.positions = list(positions)
        self.positions[0] = position
        self.length = length
        self.direction = direction
        self.next_direction = next_direction
        self.last = last

    def get_head_position(self):
        """Возвращает координаты головы змейки"""
        return self.positions[0]

    def erase(self):
        """Затирает последний сегмент, если змейка голодна,
        и при проигрыше все тело змейки в self.reset().
        """
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None

    def draw(self):
        """Перерисовать тело, дорисовать голову, затереть последний элемент."""
        for position in self.positions[1:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки.
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание вынесено в отдельный метод,
        # используется при удалении всей змейки при проигрыше
        # и последнего элемента при движении.
        self.erase()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction, self.next_direction = self.next_direction, None

    def get_new_head(self):
        """Обновление кортежа головы. Используется в self.move()
        и в теле match-case функции main, чтобы проверить положение
        головы до отрисовки змейки.
        """
        modul = (SCREEN_WIDTH, SCREEN_HEIGHT)
        return tuple(map(lambda x, y, modul: (x + y * GRID_SIZE) % modul,
                         self.get_head_position(), self.direction, modul))

    def move(self):
        """Обновление положения змейки."""
        new_head = self.get_new_head()
        self.positions.insert(0, new_head)
        if self.length < len(self.positions):
            self.last = self.positions.pop()

    def reset(self):
        """Возврат змейки в исходное состояние, другое направление движения."""
        # Затереть тело змейки.
        for position in self.positions:
            self.last = position
            self.erase()

        # Откатить изменяемые в ходе игры настройки к первоначальным.
        self.positions.clear()
        self.positions.append(self.position)
        self.length = START_LENGTH
        # Изменить только направление движения на случайное.
        self.direction = choice((UP, RIGHT, DOWN, LEFT))


def handle_keys(game_object):
    """Функция обработки действий пользователя.
    На клавиатуре отвечает только на действия клавиш: UP, DOWN, LEFT, RIGHT.
    Управляемый объект получает новое значение атрибута next_direction.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
                return True
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
                return True
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
                return True
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
                return True
    return False


def main():
    """Основная логика игры"""
    # Инициализация PyGame:
    pygame.init()

    # Создание экземпляров классов.
    snake = Snake()
    items = [Apple() for _ in range(3)]
    stone, poison, apple = items
    stone.body_color = STONE_COLOR
    poison.body_color = POISON_COLOR

    # Изменение скорости игры, сначала равно 0.
    diff_speed = 0

    while True:

        clock.tick(SPEED + diff_speed)
        handle_keys(snake)
        snake.update_direction()

        match snake.get_new_head():
            case apple.position:
                snake.length += 1
                for item in items:
                    item.erase()
                    item.position = item.coordinate_producer.__next__()
                    # Исключение попадания нового положения на тело змейки.
                    while item.position in snake.positions:
                        item.position = item.coordinate_producer.__next__()
                # Изменение скорости игры каждые 5 съеденных яблок.
                diff_speed = (snake.length - 1) // 5
            case poison.position:
                snake.reset()
                diff_speed = 0
            case stone.position:
                snake.reset()
                diff_speed = 0
            case _:
                if snake.get_new_head() in snake.positions[1:]:
                    snake.reset()
                    diff_speed = 0

        snake.move()
        snake.draw()
        for item in items:
            item.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
