import pygame
import os

LARGEUR, HAUTEUR = 1000, 1000
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Space Invader")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player
LEVEL1 = pygame.image.load(os.path.join("assets", "player_level1.png"))
LEVEL2 = pygame.image.load(os.path.join("assets", "player_level2.png"))
LEVEL3 = pygame.image.load(os.path.join("assets", "player_level3.png"))
LEVEL4 = pygame.image.load(os.path.join("assets", "player_level4.png"))


# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
PLAYER_LASER_LEVEL1 = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

LOGO = pygame.image.load(os.path.join("assets", "SpaceInvadersLogo.png"))