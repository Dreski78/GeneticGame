import random
import numpy as np
import pygame
from pygame import gfxdraw
from pygame.locals import *
from load_png import *
import math
import matplotlib.pyplot as plt


class Player(pygame.sprite.Sprite):

    mutation_rate = .1

    def __init__(self, DNA=False, *groups):
        super().__init__(*groups)
        self.image = load_png("player.png")
        self.rect = self.image.get_rect()

        if not DNA:
            self.speed = random.randrange(20, 80)
            self.seek_range = random.randrange(20, 80)
        else:
            if random.random() < self.mutation_rate:
                self.speed = DNA[0] + random.randrange(-20, 20)
                self.seek_range = DNA[1] + random.randrange(-20, 20)
            else:
                self.speed = DNA[0]
                self.seek_range = DNA[1]

        self.energy_loss = (self.speed // 10) ** 1.5 + (self.seek_range // 20)
        # print(self.energy_loss)

        w, h = pygame.display.get_surface().get_size()
        self.rect.x = random.randrange(w)
        self.rect.y = random.randrange(h)
        starting_vel = pygame.math.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
        starting_vel = starting_vel.normalize() * self.speed * .1
        self.vel = starting_vel

        self.hunger = 100
        self.age = 0
        self.dead = False

    def update(self, food):
        screen = pygame.display.get_surface()
        pygame.gfxdraw.aacircle(screen, self.rect.x+16, self.rect.y+16, self.seek_range, (255, 255, 255))
        self.move(food)
        if self.hunger <= 0:
            self.dead = True
            self.kill()
        else:
            self.hunger -= self.energy_loss * .05


    def eat(self):

        self.hunger += 50
        if self.hunger >= 200:
            self.hunger = 100
            return [self.speed, self.seek_range]

    def move(self, food):
        closest = self.seek_range
        closest_delta = None
        for food in food:
            if food.dist(self)[1] < closest:
                closest = food.dist(self)[1]
                closest_delta = food.dist(self)[0]

        delta = closest_delta
        # mouse = pygame.mouse.get_pos()
        # start = pygame.Vector2(self.rect.x + 16, self.rect.y + 16)
        # target = pygame.Vector2(mouse[0], mouse[1])
        # delta = target - start

        screen = pygame.display.get_surface()

        if not self.rect.colliderect(screen.get_rect()):
            self.vel = -self.vel[0], -self.vel[1]
        if delta:
            MAX_FORCE = .5
            accel = delta.normalize() * (MAX_FORCE)
            # self.vel = delta.normalize() * (self.speed * .1)
            self.vel += accel
            self.vel = self.vel.normalize() * (self.speed * .1)


        self.rect = self.rect.move(self.vel)


class Food(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = load_png("ball.png")
        self.rect = self.image.get_rect()

        w, h = pygame.display.get_surface().get_size()
        self.rect.x = random.randrange(w)
        self.rect.y = random.randrange(h)

    def eat(self, player):

        player.hunger += 50
        if player.hunger >= 200:
            player.hunger = 100
            return [player.speed, player.seek_range]

    def dist(self, player):
        start = pygame.math.Vector2(self.rect.x, self.rect.y)
        target = pygame.math.Vector2(player.rect.x + 16, player.rect.y + 16)
        delta = start - target
        return delta, delta.length()



class Poison(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = load_png("ball.png")
        fill(self.image, (255, 0, 0, 255))
        self.rect = self.image.get_rect()

        w, h = pygame.display.get_surface().get_size()
        self.rect.x = random.randrange(w)
        self.rect.y = random.randrange(h)

    def eat(self, player):

        player.hunger -= 50


class Game:

    def __init__(self):

        # Init
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))

        # Init Characters
        self.players = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        [Player(False, self.players) for i in range(10)]
        [Food(self.foods) for i in range(20)]

        # Initialize sprites
        self.playersprites = pygame.sprite.RenderPlain(self.players)
        self.foodsprites = pygame.sprite.RenderPlain(self.foods)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        # Init clock
        self.clock = pygame.time.Clock()

        # Game State
        self.frame = 0


        # data
        self.data = []
        self.data_speed = []
        self.data_seek_range = []
        self.data_age = []
        self.time = []


        self.main_loop()

    def reset(self):
        self.__init__()

    def main_loop(self):

        while True:
            self.clock.tick(300)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        self.clock.tick(60)
                    if event.key == K_ESCAPE:
                        fig = plt.figure(1)
                        plt.plot(self.time, self.data_age)
                        # fig = plt.figure(2)
                        plt.plot(self.time, self.data_speed)
                        plt.plot(self.time, self.data_seek_range)
                        plt.show()

            collided = pygame.sprite.groupcollide(self.players, self.foods, False, False)
            if collided:
                for player in collided:
                    for food in collided[player]:
                        food.kill()
                        reproduce = food.eat(player)
                        if reproduce:
                            Player([reproduce[0], reproduce[1]], self.players)

                            self.playersprites = pygame.sprite.RenderPlain(self.players)

            self.frame += 1
            if self.frame % 10 == 0:
                if len(self.foods) <= 25:
                    Food(self.foods)
                self.foodsprites = pygame.sprite.RenderPlain(self.foods)

                if len(self.players) == 0:
                    Player(False, self.players)
                    self.playersprites = pygame.sprite.RenderPlain(self.players)

                self.data.append(len(self.players))
                self.time.append(self.frame // 10)

                sum = 0
                sum1 = 0
                sum2 = 0
                for player in self.players:
                    player.age += 1

                    sum += player.seek_range
                    sum1 += player.speed
                    sum2 += player.age
                self.data_speed.append(sum / len(self.players))
                self.data_seek_range.append(sum1 / len(self.players))
                self.data_age.append(sum2 / len(self.players))

            font = pygame.font.SysFont("comicsansms", 32)
            text = font.render(f"Creatures Alive: {len(self.players.sprites())}", True, (0, 128, 0))

            self.screen.blit(self.background, self.screen.get_rect(), self.screen.get_rect())

            # self.screen.blit(text1, (0, 20))

            for player in self.players:
                player.update(self.foods)


            self.playersprites.draw(self.screen)
            self.foodsprites.draw(self.screen)

            self.screen.blit(text, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    Game()
