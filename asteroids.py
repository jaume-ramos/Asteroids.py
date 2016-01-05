#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Llibreries necessàries
import pygame
from pygame.locals import *
import time
import os
import math
import random

# Variables Globals
amplada = 800
altura = 600
punts = 0
vides = 3
time = 0
jugant = False


###############################################################################
#
#  Funcions auxiliars per adaptar el codi fet amb la llibreria SimpleGui
#  Implementen les mateixes funcionalitats cridant a la llibreria PyGame
#  Aquesta llibreria permet crear un arxiu exe, mentre que SimpleGUI
#  només funciona a la Web
#
#  El codi d'aquestaes funcions és adaptat de la llibreria SimpleGUICS2Pygame
#  https://pypi.python.org/pypi/SimpleGUICS2Pygame
#
###############################################################################

# Carrega una imatge a partir d'un fitxer
def carregar_imatge(nomFitxer):
    try:
        imatge = pygame.image.load(nomFitxer)
    except pygame.error as missatge:
        print('No puc carregar la imatge:', nomFitxer)
        raise SystemExit(missatge)

    imatge = imatge.convert_alpha()
    return imatge

# Carrega un so a partir d'un fitxer
def carregar_so(nomFitxer):
    try:
        so = pygame.mixer.Sound(nomFitxer)
    except pygame.error as missatge:
        print('No puc carregar el so:', nomFitxer)
        raise SystemExit(missatge)

    return so

# Mostra una imatge al canvas
def dibuixa_imatge(canvas, imatge,
               centre_origen, amplada_altura_origen,
               centre_desti, amplada_altura_desti,
               rotacio=0):

        # Calcula la imatge a mostrar
        amplada_origen, altura_origen = amplada_altura_origen

        x0_origen = centre_origen[0] - amplada_origen/2
        y0_origen = centre_origen[1] - altura_origen/2

        if x0_origen >= 0:
            x0_origen = int(round(x0_origen))
        elif -1 < x0_origen:
            amplada_origen -= x0_origen
            x0_origen = 0
        else:
            return

        if y0_origen >= 0:
            y0_origen = int(round(y0_origen))
        elif -1 < y0_origen:
            altura_origen -= y0_origen
            y0_origen = 0
        else:
            return

        amplada_origen = int(round(amplada_origen))
        altura_origen = int(round(altura_origen))

        if ((x0_origen + amplada_origen > imatge.get_width() + 1)
                or (y0_origen + altura_origen > imatge.get_height() + 1)):
            return

        if x0_origen + amplada_origen > imatge.get_width():
            amplada_origen -= 1

        if y0_origen + altura_origen > imatge.get_height():
            altura_origen -= 1

        if ((x0_origen == 0) and (y0_origen == 0)
            and (amplada_origen == imatge.get_width())
            and (altura_origen == imatge.get_height())):
            pygame_surface_imatge = imatge
        else:
            pygame_surface_imatge = imatge.subsurface(
                (x0_origen, y0_origen,
                 amplada_origen, altura_origen))

        if ((amplada_altura_desti[0] != amplada_origen)
            or (amplada_altura_desti[1] != altura_origen)):
            pygame_surface_imatge = pygame.transform.scale(
                pygame_surface_imatge, amplada_altura_desti)

        rotacio = int(round(-rotacio*180.0/math.pi)) % 360
        if rotacio != 0:
            pygame_surface_imatge = pygame.transform.rotate(
                pygame_surface_imatge, rotacio)

        canvas.blit(
            pygame_surface_imatge,
            (int(round(centre_desti[0] - pygame_surface_imatge.get_width()/2)),
             int(round(centre_desti[1] - pygame_surface_imatge.get_height()/2))))


###############################################################################
#
#  Classes definides pel joc
#
###############################################################################

# Classe que ens simplificarà conèixer les dimensions dels elements gràfics
class InfoImatge:
    def __init__(self, centre, mida, radi = 0, durada = None, animat = False):
        self.centre = centre
        self.mida = mida
        self.radi = radi
        if durada:
            self.durada = durada
        else:
            self.durada = float('inf')
        self.animat = animat

    def get_centre(self):
        return self.centre

    def get_mida(self):
        return self.mida

    def get_radi(self):
        return self.radi

    def get_durada(self):
        return self.durada

    def get_animat(self):
        return self.animat

# Classe que gestiona els elements gràfics o sprites
class Sprite:
    def __init__(self, pos, vel, ang, vel_ang, imatge, info, so = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.vel_angular = vel_ang
        self.imatge = imatge
        self.imatge_centre = info.get_centre()
        self.imatge_mida = info.get_mida()
        self.radi = info.get_radi()
        self.durada = info.get_durada()
        self.age = 0
        self.animat = info.get_animat()
        self.animation_index = 0
        if so:
            so.stop()
            ch = so.play()

    def get_radi(self):
        return self.radi

    def get_pos(self):
        return self.pos

    def dibuixa(self, canvas):
        if self.animat:
            imatge_centre = (self.imatge_centre[0]+(self.animation_index*self.imatge_mida[0]), self.imatge_centre[1])
            self.animation_index += 1
            dibuixa_imatge(canvas, self.imatge, imatge_centre, self.imatge_mida, self.pos, self.imatge_mida, self.angle)
        else:
            dibuixa_imatge(canvas, self.imatge, self.imatge_centre, self.imatge_mida, self.pos, self.imatge_mida, self.angle)

    def actualitza(self):
        global age, durada, bala_gropue
        self.angle += self.vel_angular
        self.pos[0] = (self.pos [0] + self.vel[0]) % amplada
        self.pos[1] = (self.pos [1] + self.vel[1]) % altura
        self.age = self.age + 1
        if self.age >= self.durada:
            return True
        elif self.age < self.durada:
            return False


    def colisiona(self, un_objecte):
        distancia = dist(self.pos, un_objecte.get_pos())
        if distancia < (self.radi + un_objecte.get_radi()):
            return True
        else:
            return False

# Classe que gestiona la nau del joc
class nauEspacial:
    def __init__(self, pos, vel, angle, imatge, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.accelera = False
        self.angle = angle
        self.vel_angular = 0
        self.acceleracio_angular = 0
        self.imatge = imatge
        self.imatge_centre = info.get_centre()
        self.imatge_mida = info.get_mida()
        self.radi = info.get_radi()
        self.direccio = [math.cos(self.angle), math.sin(self.angle)]

    def get_radi(self):
        return self.radi

    def get_pos(self):
        return self.pos

    def dibuixa(self,canvas):
        if self.accelera:
            dibuixa_imatge(canvas, nau_imatge, [135,45], self.imatge_mida, self.pos, self.imatge_mida, self.angle)
            nau_accelera_sound.play()
        else:
            dibuixa_imatge(canvas, nau_imatge, self.imatge_centre, self.imatge_mida, self.pos, self.imatge_mida, self.angle)
            nau_accelera_sound.stop()

    def actualitza(self):

        #Friccio
        self.vel[0] *= (1-0.015)
        self.vel[1] *= (1-0.015)

        #Direcció
        self.direccio = [math.cos(self.angle), math.sin(self.angle)]

        #Acceleracio
        if self.accelera:
            self.vel[0] += self.direccio[0]*(1-0.7*abs(math.atan(self.vel[0])) / (math.pi / 2))
            self.vel[1] += self.direccio[1]*(1-0.7*abs(math.atan(self.vel[1])) / (math.pi / 2))

        # Posicio
        self.pos[0] = (self.pos[0] + self.vel[0]) % amplada
        self.pos[1] = (self.pos[1] + self.vel[1]) % altura

        #Angle
        self.vel_angular += self.acceleracio_angular
        self.angle += self.vel_angular


    def giraEsquerra(self):
        self.vel_angular -= 0.05

    def giraDreta(self):
        self.vel_angular += 0.05

    def aturaRotacio(self):
        self.vel_angular = 0

    def accelera(self):
        self.accelera = True

    def aturaAcceleracio(self):
        self.accelera = False

    def dispara(self):
        global bales

        bala_vel = [self.vel[0]+( self.direccio[0]*4), self.vel[1]+(self.direccio[1]*4)]
        bala_pos = [(self.pos[0] + self.direccio[0] * self.radi), (self.pos[1] + self.direccio[1] * self.radi)]

        if jugant == True:
            bales.add(Sprite(bala_pos, bala_vel, self.angle, 0, bala_imatge, bala_info, bala_sound))
        else:
            for bala in bales.copy():
                bales.remove(bala)


###############################################################################
#
#  Funcions auxiliars
#
###############################################################################

# Torna un vector amb la direcció de l'angle en radians
def angle_a_vector(ang):
    return [math.cos(ang), math.sin(ang)]

# Calcula la distància entre dos punts 2D
def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Callback per quan es prem una tecla
def teclaAvall(tecla):
    #print tecla
    if tecla == 276:
        nau.giraEsquerra()
    elif tecla == 275:
        nau.giraDreta()
    elif tecla == 273:
        nau.accelera()
    elif tecla == 32:
        nau.dispara()

# Callback per quan s'allibera una tecla
def teclaAmunt(tecla):
    if tecla == 276:
        nau.aturaRotacio()
    elif tecla == 275:
        nau.aturaRotacio()
    elif tecla == 273:
        nau.aturaAcceleracio()

# Callback per quan es clica amb el ratolí
def ratoliClic(pos):
    global jugant
    centre = [amplada / 2, altura / 2]
    mida = inici_info.get_mida()
    dinsMida_amplada = (centre[0] - mida[0] / 2) < pos[0] < (centre[0] + mida[0] / 2)
    dinsMida_altura = (centre[1] - mida[1] / 2) < pos[1] < (centre[1] + mida[1] / 2)
    if (not jugant) and dinsMida_amplada and dinsMida_altura:
        musica.play()
        jugant = True

# Afegeix un asteroide al joc
def afegeixAsteroide():
    global roques, vides, punts
    if jugant == False:
        vides = 3
        punts = 0
        for roca in roques.copy():
            roques.remove(roca)

    if jugant == True:
        if len(roques) < 12:
            while True:
                pos = [random.randrange(0, amplada), random.randrange(0, altura)]
                if dist(nau.pos, pos) > 150:
                    break
            vel = [random.randrange(-4,4) , random.randrange(-4,4)]
            velAng = (random.choice([-1,1])*random.choice([0.05,0.1]))
            roques.add(Sprite(pos, vel, 0, velAng , asteroide_imatge, asteroide_info))

# Comprova si hi ha colisions entre els elements de dos grups
def colisionen(roques, bales):
    global punts, explosions
    for roca in roques.copy():
        for bala in bales.copy():
            if roca.colisiona(bala) is True:
                explosions.add(Sprite(roca.pos, roca.vel, 0, 0 ,
                                     explosio_imatge, explosio_info, explosio_sound))
                roques.discard(roca)
                bales.discard(bala)
                punts += 1

# Actualitza les posicions dels elements del joc i els dibuixa
def dibuixa(canvas):
    global time, vides, jugant, bales, roques

    # Dibuixa el fons i mou les pedres
    time += 1
    wtime = (time / 4) % amplada
    centre = pedres_info.get_centre()
    mida = pedres_info.get_mida()
    dibuixa_imatge(canvas, nebulosa_imatge, nebulosa_info.get_centre(), nebulosa_info.get_mida(), [amplada / 2, altura / 2], [amplada, altura])
    dibuixa_imatge(canvas, pedres_imatge, centre, mida, (wtime - amplada / 2, altura / 2), (amplada, altura))

    # Dibuixa la nau i els asteroides
    nau.dibuixa(canvas)

    # Comprova si hi ha coli·lisions entre roques i bales
    colisionen(roques, bales)

    # Dibuixa els asteroides i verifica si col·lisionen amb la nau
    for roca in roques.copy():
        roca.dibuixa(canvas)
        roca.actualitza()
        if roca.colisiona(nau):
            roques.remove(roca)
            vides = vides - 1
            if vides == 0:
                musica.stop()
                jugant = False

    # Dibuixa les bales i verifica si han superat el temps de vida
    for bala in bales.copy():
        bala.dibuixa(canvas)
        if bala.actualitza() is True:
            bales.remove(bala)

    # Dibuixa les explosions detectades
    for explosio in explosions:
        explosio.dibuixa(canvas)

    # Actualitza la posició de la nau
    nau.actualitza()

    # Si la partida està en marxa mostra la puntuació i les vides restants
    # Si la partida està aturada mostra la imatge inicial fins que facin clic
    if jugant:
        text_dibuixa = fontObj.render("Vides:"+ "  " + str(vides), True, white_color)
        canvas.blit(text_dibuixa, (50, 50))
        text_dibuixa = fontObj.render("Punts:"+ "  " + str(punts), True, white_color)
        canvas.blit(text_dibuixa, (640, 50))
    else:
        dibuixa_imatge(canvas, inici_imatge, inici_info.get_centre(), inici_info.get_mida(), [amplada / 2, altura / 2], inici_info.get_mida())


###########################################################
#                                                         #
#   Programa Principal                                    #
#                                                         #
###########################################################

# Inicialitza la llibreria PyGame
canvas = pygame.display.set_mode((amplada, altura))
pygame.display.set_caption("asteroides")
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()

# Carrega les imatges
pedres_info = InfoImatge([320, 240], [640, 480])
pedres_imatge = carregar_imatge("assets/pedres.png")

nebulosa_info = InfoImatge([400, 300], [800, 600])
nebulosa_imatge = carregar_imatge("assets/nebulosa.png")

inici_info = InfoImatge([200, 150], [400, 300])
inici_imatge = carregar_imatge("assets/asteroids.png")

nau_info = InfoImatge([45, 45], [90, 90], 35)
nau_imatge = carregar_imatge("assets/nau-x2.png")

bala_info = InfoImatge([5,5], [10, 10], 3, 50)
bala_imatge = carregar_imatge("assets/bala.png")

asteroide_info = InfoImatge([45, 45], [90, 90], 40)
asteroide_imatge = carregar_imatge("assets/asteroide.png")

explosio_info = InfoImatge([64, 64], [128, 128], 17, 24, True)
explosio_imatge = carregar_imatge("assets/explosio.png")

# Carrega els sons
musica = carregar_so("assets/musica.ogg")
musica.stop()

bala_sound = carregar_so("assets/bala.ogg")
bala_sound.set_volume(.5)

nau_accelera_sound = carregar_so("assets/accelera.ogg")

explosio_sound = carregar_so("assets/explosio.ogg")

# Carrega les fonts
fontObj = pygame.font.Font(pygame.font.match_font('comic sans ms'), 32)

# Defineix els colors
white_color = pygame.Color(255, 255, 255)

# Crea la nau espacial
nau = nauEspacial([amplada / 2, altura / 2], [0,0], 0, nau_imatge, nau_info)

# Crea els conjunts(sets) de roques, bales i explosions
roques = set()
bales = set()
explosions = set()

# Crea el temporitzador per controlar els FPS del joc
clock = pygame.time.Clock()

# Crea un temporitzador per generar un event cada segon
temporitzador_asteroide=USEREVENT+1;
pygame.time.set_timer(temporitzador_asteroide, 1000)

#
# Bucle principal del joc. Actiu fins que tanquen la finestra del joc.
#
treballant = True
while treballant:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # window GUI ('x' the window)
            treballant = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            ratoliClic(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            teclaAvall(event.key)
        elif event.type == pygame.KEYUP:
            teclaAmunt(event.key)
        elif event.type == temporitzador_asteroide:
            afegeixAsteroide()

    # Actualitza el joc i el mostra
    dibuixa(canvas)
    pygame.display.update()

    # Temporitzador per mostrar el joc a 60FPS
    clock.tick(60)

# Surt del joc
pygame.quit ()
