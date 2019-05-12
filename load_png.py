import pygame
import os


def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('img', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        return image
    except pygame.error:
        print('Cannot load image:', fullname)
