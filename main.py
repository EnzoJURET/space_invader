import pygame
import os
import time
import random
import config
import sound
import db
import getpass

pygame.font.init()

# Global values
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")),(config.LARGEUR, config.HAUTEUR))
FPS = 60
niveau = 0
vies = 5
wave_length = 5
enemie_vel = 3
laser_vel = 10
pauseEvent = pygame.USEREVENT + 1
alreadyloose = 0
playersoundmanager = sound.PlayerSound()
TEMPS_RECHARGE = 8

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def deplacement(self, vel):
        self.y += vel

    def h_ecran(self, hauteur):
        return not (self.y <= hauteur and self.y >= 0)

    def collision(self, obj):
        return collision(self, obj)


class Vaisseau:
    TEMPS_RECHARGE = 7

    def __init__(self, x, y, vie=100):
        self.x = x
        self.y = y
        self.vie = vie
        self.vaisseau_img = None
        self.laser_img = None
        self.lasers = []
        self.compteur_tmp_recharge = 0

    def draw(self, window):
        window.blit(self.vaisseau_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def mvt_laser(self, vel, obj):
        self.tmp_recharge()
        for laser in self.lasers:
            laser.deplacement(vel)
            if laser.h_ecran(config.HAUTEUR):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.vie -= 10
                self.lasers.remove(laser)

    def tmp_recharge(self):
        if self.compteur_tmp_recharge >= self.TEMPS_RECHARGE:
            self.compteur_tmp_recharge = 0
        elif self.compteur_tmp_recharge > 0:
            self.compteur_tmp_recharge += 1

    def tirer(self):
        if self.compteur_tmp_recharge == 0:
            playersoundmanager.play()
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.compteur_tmp_recharge = 1

    def get_width(self):
        return self.vaisseau_img.get_width()

    def get_height(self):
        return self.vaisseau_img.get_height()


class Joueur(Vaisseau):
    def __init__(self, x, y, vie=100, skin=config.LEVEL1):
        super().__init__(x, y, vie)
        self.vaisseau_img = skin
        self.laser_img = config.PLAYER_LASER_LEVEL1
        self.mask = pygame.mask.from_surface(self.vaisseau_img)
        self.max_vie = vie

    def mvt_laser(self, vel, objs):
        self.tmp_recharge()
        for laser in self.lasers:
            laser.deplacement(vel)
            if laser.h_ecran(config.HAUTEUR):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.barreVie(window)

    def barreVie(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.vaisseau_img.get_height() + 10, self.vaisseau_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
        self.x, self.y + self.vaisseau_img.get_height() + 10, self.vaisseau_img.get_width() * (self.vie / self.max_vie),
        10))


class Enemie(Vaisseau):
    COLOR_MAP = {
        "red": (config.RED_SPACE_SHIP, config.RED_LASER),
        "green": (config.GREEN_SPACE_SHIP, config.GREEN_LASER),
        "blue": (config.BLUE_SPACE_SHIP, config.BLUE_LASER)
    }

    def __init__(self, x, y, color, vie=100):
        super().__init__(x, y, vie)
        self.vaisseau_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.vaisseau_img)

    def deplacement(self, vel):
        self.y += vel

    def tirer(self):
        if self.compteur_tmp_recharge == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.compteur_tmp_recharge = 1


def collision(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def afficherMessageSucces(niveau):
    message = pygame.font.SysFont("comicsans", 30)
    label = message.render(f"Félicitation, niveau {niveau} atteint !", 1, (255, 255, 255))
    config.fenetre.blit(label, (config.LARGEUR / 2 - label.get_width() / 2, config.HAUTEUR / 2 + label.get_height()))
    pygame.display.update()


def main():
    sound.GlobalMusic.playgeneric()
    paused = False
    debut = True

    FPS = 60
    niveau = 0
    vies = 5
    wave_length = 5
    enemie_vel = 4
    joueur_vel = 8
    laser_vel = 7

    main_font = pygame.font.SysFont("comicsans", 50)
    coeur_image = pygame.image.load(os.path.join("assets", "vie.png"))
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []

    joueur = Joueur(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-ingame.png")),
                                    (config.LARGEUR, config.HAUTEUR))
        config.fenetre.blit(BG, (0, 0))
        # draw text
        for i in range(vies):
            if i == 0:
                config.fenetre.blit(coeur_image, (0, 10))
            if i >= 1:
                config.fenetre.blit(coeur_image, ((coeur_image.get_width() + 5) * i, 10))

        label_niveaux = main_font.render(f"Niveau : {niveau}", 1, (255, 255, 255))

        config.fenetre.blit(label_niveaux, (config.LARGEUR - label_niveaux.get_width() - 10, 10))

        for enemie in enemies:
            enemie.draw(config.fenetre)

        joueur.draw(config.fenetre)

        if lost:
            if lost_count == 1:
                mydb = db.BDD()
                mydb.savePlayerScore(getpass.getuser(), niveau)
                sound.GlobalMusic.stopmusic()
            label_go = lost_font.render("Game Over !", 1, (255, 255, 255))
            config.fenetre.blit(label_go, (
            config.LARGEUR / 2 - label_go.get_width() / 2, config.HAUTEUR / 2 - label_go.get_height()))

        pygame.display.update()

    while debut:
        if paused and niveau > 1:
            afficherMessageSucces(niveau)

        clock.tick(FPS)
        redraw_window()

        if vies <= 0 or joueur.vie <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                sound.GlobalMusic.playmusicmenu()
                debut = False
            else:
                continue

        if len(enemies) == 0:
            niveau += 1
            if niveau == 5:
                paused = True
                pygame.time.set_timer(pauseEvent, 5000)
                del joueur
                joueur = Joueur(300, 630, 100, config.LEVEL2)
                joueur_vel = 10
                print(joueur_vel)
            elif niveau == 11:
                paused = True
                pygame.time.set_timer(pauseEvent, 5000)
                del joueur
                joueur = Joueur(300, 630, 100, config.LEVEL3)
                joueur_vel = 12
            elif niveau == 20:
                paused = True
                pygame.time.set_timer(pauseEvent, 5000)
                del joueur
                joueur = Joueur(300, 630, 100, config.LEVEL4)
                joueur_vel = 13

            wave_length += 5
            for i in range(wave_length):
                enemie = Enemie(random.randrange(50, config.LARGEUR - 100), random.randrange(-1500, -100),
                                random.choice(["red", "blue", "green"]))
                enemies.append(enemie)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pauseEvent:
                pygame.time.set_timer(pauseEvent, 0)
                paused = False

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_q] or keys[pygame.K_LEFT]) and joueur.x - joueur_vel > 0:  # left
            joueur.x -= joueur_vel
        if (keys[pygame.K_d] or keys[
            pygame.K_RIGHT]) and joueur.x + joueur_vel + joueur.get_width() < config.LARGEUR:  # right
            joueur.x += joueur_vel
        if (keys[pygame.K_z] or keys[pygame.K_UP]) and joueur.y - joueur_vel > 0:  # up
            joueur.y -= joueur_vel
        if (keys[pygame.K_s] or keys[
            pygame.K_DOWN]) and joueur.y + joueur_vel + joueur.get_height() + 15 < config.HAUTEUR:  # down
            joueur.y += joueur_vel
        if keys[pygame.K_SPACE] or keys[pygame.MOUSEBUTTONDOWN]:
            joueur.tirer()
        if keys[pygame.K_ESCAPE]:
            main_menu()

        for enemie in enemies[:]:
            enemie.deplacement(enemie_vel)
            enemie.mvt_laser(laser_vel, joueur)

            if random.randrange(0, 2 * 60) == 1:
                enemie.tirer()

            if collision(enemie, joueur):
                joueur.vie -= 10
                enemies.remove(enemie)
            elif enemie.y + enemie.get_height() > config.HAUTEUR:
                vies -= 1
                enemies.remove(enemie)

        joueur.mvt_laser(-laser_vel, enemies)


def afficherScore():
    debut = True
    pygame.time.set_timer(pauseEvent, 5000)

    BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-ingame.png")),
                                (config.LARGEUR, config.HAUTEUR))
    config.fenetre.blit(BG, (0, 0))

    fontTitle = pygame.font.SysFont("comicsans", 30)
    font = pygame.font.SysFont("comicsans", 60)
    label = fontTitle.render("BEST PLAYERS", 1, (255, 255, 255))
    config.fenetre.blit(BG, (0, 0))
    config.fenetre.blit(label, (config.LARGEUR / 2 - label.get_width() / 2, config.HAUTEUR / 2 - 50))

    font_color = (255, 255, 255)

    mydb = db.BDD()
    spacing = 0
    nbscoretoprint = 5
    for score in mydb.getLeaderBoard():
        if nbscoretoprint == 0:
            break
        labelleaderboard = font.render(f"{score[0]} - {score[1]}", True, font_color)
        config.fenetre.blit(labelleaderboard, (config.LARGEUR / 2 - labelleaderboard.get_width() / 2,
                                               config.HAUTEUR / 2 + labelleaderboard.get_height() / 2 + spacing))
        spacing += labelleaderboard.get_height() + 20
        nbscoretoprint -= 1
        pygame.display.update()

    pygame.display.update()
    while debut:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                debut = False

    pygame.quit()


def event_bouton(x, y, targetrect, positionx, positiony):
    if pygame.mouse.get_focused():
        if positionx <= x <= positionx + targetrect.width and positiony <= y <= positiony + targetrect.height:
            return True
        else:
            return False


def main_menu():
    pygame.init()
    keys = pygame.key.get_pressed()
    sound.GlobalMusic.playmusicmenu()
    title_font = pygame.font.SysFont("comicsans", 40)
    debut = True
    y = 35
    x_m2 = 0
    y_m2 = 0
    backTo = False
    METEORITE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "meteorite.png")), (100, 100))
    METEORITE2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "meteorite2.png")), (35, 27))
    while debut:

        if (y == METEORITE.get_width()):
            backTo = True
        elif (y == 35):
            backTo = False

        if (backTo == True):
            y -= 0.5
        else:
            y += 0.5

        x_m2 += 60
        y_m2 += 60


        BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")),(config.LARGEUR, config.HAUTEUR))
        LOGO = pygame.transform.scale(pygame.image.load(os.path.join("assets", "SpaceInvadersLogo.png")), (540, 215))
        SCORE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "trophee.png")), (58, 68))
        TUTO = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tuto.png")), (412, 230))
        config.fenetre.blit(BG, (0, 0))
        label_commencer = title_font.render("Cliquez pour commencer...", 1, (255, 255, 255))
        config.fenetre.blit(METEORITE, (config.LARGEUR - METEORITE.get_width() - 30, y))
        config.fenetre.blit(METEORITE2, (x_m2,y_m2))
        config.fenetre.blit(LOGO, (config.LARGEUR / 2 - LOGO.get_width() / 2, 30))
        #config.fenetre.blit(SCORE,(config.LARGEUR / 2 - SCORE.get_width() / 2, config.HAUTEUR - SCORE.get_height() - 40))
        config.fenetre.blit(SCORE,(40, 40))
        config.fenetre.blit(TUTO, (config.LARGEUR / 2 - TUTO.get_width() / 2, TUTO.get_height() + 50))
        config.fenetre.blit(label_commencer, (
        config.LARGEUR / 2 - label_commencer.get_width() / 2, config.HAUTEUR / 2 + label_commencer.get_height()))
        pygame.display.update()
        score_rect = SCORE.get_rect()

        x_mouse, y_mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                debut = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                #if event_bouton(x_mouse, y_mouse, score_rect, config.LARGEUR / 2 - SCORE.get_width() / 2,config.HAUTEUR - SCORE.get_height() - 40):
                if event_bouton(x_mouse, y_mouse, score_rect, 40, 40):
                    afficherScore()
                else:
                    main()
    pygame.quit()


main_menu()
