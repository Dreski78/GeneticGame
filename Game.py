import random

import pygame
from pygame.locals import *
from load_png import load_png


class Player(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = load_png("player.png")
        self.rect = self.image.get_rect()

        self.rect.x = 200
        self.rect.y = 200

        self.food = 0
        self.health = 100
        self.hunger = 100
        self.dead = False

    def update(self):
        screen = pygame.display.get_surface()
        self.rect.clamp_ip(screen.get_rect())

    def step(self):
        if self.hunger == 0:
            self.health -= 25
            if self.health == 0:
                self.dead = True

        else:
            self.hunger -= 1

    def eat(self):
        if self.food == 0:
            return

        self.hunger += 50
        self.food -= 1


class Food(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = load_png("ball.png")
        self.rect = self.image.get_rect()

        w, h = pygame.display.get_surface().get_size()
        self.rect.x = random.randrange(w)
        self.rect.y = random.randrange(h)


class Game:

    def __init__(self):

        # Init
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))

        # Init Characters
        self.player = Player()
        self.foods = pygame.sprite.Group()

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))


        # Initialize sprites
        self.playersprites = pygame.sprite.RenderPlain(self.player)
        self.foodsprites = pygame.sprite.RenderPlain(self.foods)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        # Init clock
        self.clock = pygame.time.Clock()

        # Game State
        self.frame = 0

        self.main_loop()

    def reset(self):
        self.__init__()

    def main_loop(self):

        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        self.player.eat()

            keys = pygame.key.get_pressed()

            if not max(keys[K_w], keys[K_s], keys[K_a], keys[K_d]) == 0:  # Moved
                self.player.step()
                food = pygame.sprite.spritecollideany(self.player, self.foods)
                if food:
                    food.kill()
                    self.player.food += 1
                print(self.player.hunger)
                self.frame += 1
                if self.frame == 10:
                    Food(self.foods)
                    self.foodsprites = pygame.sprite.RenderPlain(self.foods)
                    self.frame = 0

            if keys[K_w]:
                self.player.rect.y -= 10

            if keys[K_s]:
                self.player.rect.y += 10

            if keys[K_a]:
                self.player.rect.x -= 10

            if keys[K_d]:
                self.player.rect.x += 10

            self.screen.blit(self.background, self.screen.get_rect(), self.screen.get_rect())

            self.playersprites.draw(self.screen)
            self.foodsprites.draw(self.screen)
            pygame.display.flip()


if __name__ == '__main__':
    Game()
