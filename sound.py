import os

import pygame


class GlobalMusic:

    @staticmethod
    def playmusicmenu():
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.abspath("assets/menu.mp3"))
        pygame.mixer.music.set_volume(0.03)
        pygame.mixer.music.play()

    @staticmethod
    def playgeneric():
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.abspath("assets/generique.mp3"))
        pygame.mixer.music.set_volume(0.03)
        pygame.mixer.music.play(loops=-1)

    @staticmethod
    def stopmusic():
        pygame.mixer.music.stop()


class PlayerSound:

    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(os.path.abspath("assets/laser.wav"))

    def play(self):
        self.sound.play()
        self.sound.set_volume(0.01)