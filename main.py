import math

import game
from function import *
import gui

import pygame as pg
from pygame.locals import (
    MOUSEBUTTONDOWN,
    KEYDOWN,
    KEYUP,
    QUIT
)

pg.joystick.init()
class ClassPlayArea():
    def __init__(self, surfsize, loc):
        self.surf = pg.Surface(surfsize)
        self.rect = self.surf.get_rect()
        self.location = loc
        self.zoom = 2

class Seat():
    def __init__(self, color):
        self.color = color
        self.joystick = None

class ClassEventHandle():
    def __init__(self):
        pass
        # self.Controllers = []

    def update(self, surface):
        input = {}
        # input["joystick"] = self.Controllers
        input["mouse"] = []
        key = []

        resize = False
        for event in pg.event.get():
            if event.type in [KEYDOWN, KEYUP]:
                key.append(event)
            elif event.type == MOUSEBUTTONDOWN:
                input["mouse"].append(event)
            elif event.type == QUIT:
                quit()
            elif event.type == pg.VIDEORESIZE:
                old_surface_saved = surface
                surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                surface.blit(old_surface_saved, (0, 0))
                del old_surface_saved
                resize= True

        return input, resize


pg.init()

SCREEN = pg.display.set_mode((1200, 800),pg.RESIZABLE, pg.OPENGLBLIT, vsync=0)
CLOCK = pg.time.Clock()

FLOW = {}
FLOW["seat"] = []
FLOW["seat"].append(Seat([255,0,0]))
FLOW["seat"].append(Seat([0,255,0]))
FLOW["seat"].append(Seat([0,0,255]))
FLOW["seat"].append(Seat([255,255,0]))

FLOW["seat"][0].joystick = pg.joystick.Joystick(0)

PLAYAREA = [ClassPlayArea((1200, 800), (0,0))]

INPUT = ClassEventHandle()

# Initial GUI menu.
FLOW["state"] = gui.MainMenu(PLAYAREA[0])
while True:
    input, resize = INPUT.update(PLAYAREA[0].surf)
    FLOW["state"].update(SCREEN, FLOW, input, resize)
    pg.display.update()

    pg.display.set_caption(str(CLOCK.get_fps()))
    if pg.key.get_pressed()[32]:
        CLOCK.tick(5)
    else:
        CLOCK.tick(60)
        pass

