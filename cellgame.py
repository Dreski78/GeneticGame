import pygame
import random
import numpy as np


class Cell:

    def __init__(self, pos):
        if pos is None:
            global grid
            pos = [random.randrange(grid[0]), random.randrange(grid[1])]
        self.position = pos

    def step(self):
        pass

    def move(self):
        direction = np.random.randint(0, 4)
        if direction == 0:
            self.position[0] += 1
        elif direction == 1:
            self.position[0] -= 1
        elif direction == 2:
            self.position[1] += 1
        elif direction == 3:
            self.position[1] -= 1

    def bound(self):
        global grid
        if self.position[0] >= grid[0]:
            self.position[0] = grid[0] - 1
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[1] >= grid[1]:
            self.position[1] = grid[1] - 1
        if self.position[1] < 0:
            self.position[1] = 0


class Prey(Cell):

    def __init__(self, pos):
        super().__init__(pos)
        self.color = (0, 255, 0)
        self.hp = 0

    def step(self):
        self.move()
        self.bound()
        self.hp += 1

    def conclude(self):
        global living_things
        if self.hp >= 50:
            self.hp = 0
            living_things.append(Prey(self.position.copy()))


class Predator(Cell):

    def __init__(self, pos):
        super().__init__(pos)
        self.color = (255, 0, 0)
        self.hp = 50

    def step(self):
        self.move()
        self.bound()
        self.hp -= 1

    def conclude(self):
        global living_things
        if self.hp <= 0:
            living_things.remove(self)

WIDTH = 280
HEIGHT = 280
cell_size = 2
MAX_THINGS = ((HEIGHT // cell_size) * (WIDTH // cell_size))
MAX_THINGS *= .1
MAX_THINGS = int(MAX_THINGS)

print(MAX_THINGS)

def resolve(list):
    global living_things

    if len(list) < 2:
        return
    if all(type(thing) is Predator for thing in list):
        return
    if all(type(thing) is Prey for thing in list):
        return
    if any(type(thing) is Predator for thing in list):
        _ = [living_things.remove(thing) for thing in list if type(thing) is Prey]
        _ = [list.remove(thing) for thing in list if type(thing) is Prey]
        for thing in list:
                thing.hp = 50
        living_things.append(Predator(list[0].position.copy()))
        return

grid = (WIDTH // cell_size, HEIGHT // cell_size)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

starting_things = [Prey(None) for i in range(1000)] + [Predator(None) for j in range(1000)]

living_things = []
living_things += starting_things

clock = pygame.time.Clock()

while True:

    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill((0, 0, 0))

    conflicts = [[[] for col in range(HEIGHT // cell_size)] for row in range(WIDTH // cell_size)]

    for thing in living_things:
        thing.step()
        pygame.draw.rect(screen, thing.color,
                         (thing.position[0] * cell_size, thing.position[1] * cell_size, cell_size, cell_size))

        conflicts[thing.position[0]][thing.position[1]].append(thing)

    for row in conflicts:
        for cell in row:
            if cell:
                resolve(cell)

    _ = [thing.conclude() for thing in living_things]

    if not any(type(thing) is Predator for thing in living_things):
        living_things.append(Predator(None))
    if not any(type(thing) is Prey for thing in living_things):
        living_things.append(Prey(None))
    if len(living_things) > MAX_THINGS:
        for i in range(len(living_things) - MAX_THINGS):
            del living_things[random.randrange(MAX_THINGS)]

    pygame.display.flip()
