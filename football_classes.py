import pygame
from pygame.color import THECOLORS

pygame.font.init()

"""
Класс GameObject
1. Поля класса в идеале должны быть приватными с геттерами и сеттерами
2. Для указания координат лучше создать отдельный класс Vector
3. Возможно, лучше будет кидать исключение в виртуальном методе
4. GameObject имеет абстрактный (виртуальный) метод, значит он должен быть абстрактным классом, и у нас не должно быть возможности его создать.
Класс Person
1. Лучше сделать переменную ableToMove приватной и добавить ей статические сеттер и геттер. Метод freeze можно обойти и он не обеспечивает полный функционал
2. Лучше вместо присваивания переменной self.stop какого-либо значения добавить сеттер (приватный или публичный). Так мы сможем обрабатывать событие остановки person
Класс Ball
1. В set_speed нужно делать копию массива, приходящего в виде аргумента
В целом
1. Было бы неплохо переопределить str() в каждом классе наследнике
2. Если планируется расширение кода, то лучше было бы создать логгер
3. В football.py код после if-а можно разбить на функции по типу init(), update(), render() и т.д.
"""


class GameObject(pygame.sprite.Sprite):
    """Класс для описания отрисовки всех игровых объектов"""

    def __init__(self, x=0, y=0, xrec=50, yrec=50):
        """Конструктор класса GameObject"""
        super().__init__()
        # инициализация атрибутов класса
        self.position = [x, y]
        # инициализируем графический объект ("спрайт") для визуализаци
        self.image = pygame.Surface((xrec, yrec))
        self.rect = self.image.get_rect()

    # Методы класса
    def check_collision(self, group=pygame.sprite.Group()):
        others = group.copy()
        if group.has(self):
            others.remove(self)
        collided = pygame.sprite.spritecollideany(self, others)
        if collided:
            self.update_on_collision(collided)

    # виртуальный метод
    def update_on_collision(self, collided):
        pass  # виртуальня метод реализуется в классах-наследниках

    def update(self):
        """Используется группой спрайтов для обновления спрайта"""
        # обновляем графический объект ("спрайт")
        self.rect.center = (self.position[0], self.position[1])

    # метод-сеттер
    def set_position(self, pos):
        """Устанавливает значение атрибута"""
        self.position = pos.copy()

    def add_position(self, pos):
        self.position[0] += pos[0]
        self.position[1] += pos[1]

    def move(self, dx, dy):
        self.position[0] += dx
        self.position[1] += dy

    # специальный метод для отображения экземпляра класса
    def __str__(self):
        return "Object position %s" % self.position


class Person(GameObject):
    """Класс для описания любого участника игры"""

    # Аттрибуты класса
    ableToMove = True

    # Методы класса
    def __init__(self):
        """Конструктор класса Person"""
        super().__init__()
        self.stop = False

    # реализация виртуального метода
    def update_on_collision(self, collided):
        if isinstance(collided, Person):
            self.stop = True

    def move(self, dx, dy):
        """Метод класса для перемещения участника игры"""
        if not self.stop:
            super().move(dx, dy)

    @classmethod
    def freeze(cls):
        """Метод для остановки всех участников игры"""
        cls.ableToMove = False

    def __str__(self):
        return "Person ableToMove, stop: %s, %s" % (self.ableToMove, self.stop)


class Player(Person):
    """Класс для описания игроков, потомок класса Person"""

    def __init__(self, num, col=THECOLORS["red"]):
        """Конструктор класса Player"""
        super().__init__()
        self.number = num
        self.color = col
        self.has_ball = False
        # инициализируем графический объект цветом и номером
        self.image.fill(col)
        font = pygame.font.SysFont(None, 24)
        img = font.render(self.number, True, "white")
        self.image.blit(img, self.rect.center)

    def dribble(self, ball):
        """Метод для ведения мяча"""
        ball.set_speed()
        ball.set_position(self.position)
        self.has_ball = True

    def kick(self, ball):
        """Метод для передачи паса"""
        if self.has_ball:
            ball.add_position([0, -31])
            ball.set_speed([0, -1])
        self.has_ball = False

    # реализация виртуального метода
    def update_on_collision(self, collided):
        super().update_on_collision(collided)
        if isinstance(collided, Ball):
            self.dribble(collided)

    def __str__(self):
        return "Игрок %s цвет %s" % (self.number, self.color)


class Goalkeeper(Player):
    """Класс для описания вратаря, потомок класса Player"""

    pass


class Ball(GameObject):

    def __init__(self, x=0, y=0):
        super().__init__(x, y, xrec=10, yrec=10)
        self.speed = [0, 0]

    def update_on_collision(self, collided):
        self.speed[0] = -self.speed[0]
        self.speed[1] = -self.speed[1]

    def move(self, dt=0):
        self.position[0] += self.speed[0] * dt
        self.position[1] += self.speed[1] * dt

    def set_speed(self, speed=[0, 0]):
        self.speed = speed


class GateBar(GameObject):
    """Класс для описания штанги ворот"""

    def __init__(self, x=0, y=0):
        super().__init__(x, y, xrec=15, yrec=15)


class Gate(GameObject):
    """Класс для описания ворот"""

    def __init__(self, x=0, y=0):
        super().__init__(x, y, xrec=200, yrec=10)

    def update_on_collision(self, collided):
        if isinstance(collided, Ball):
            self.image.fill("red")
            collided.set_position(self.position)
            collided.speed = [0, 0]


class TestClass:
    """Для демонстрации приватных аттрибутов класса"""

    def __init__(self, x=0):
        self.__x = x  # аттрибут недоступен для обращения напрямую

    # метод-геттер для обращения к приватному аттрибуту
    def get_x(self):
        return self.__x


"""
1)update_on_collision нет в GateBar
"""
