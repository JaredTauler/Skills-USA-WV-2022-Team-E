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

class ClassPlayArea():
    def __init__(self, surfsize, loc):
        self.surf = pg.Surface(surfsize)
        self.rect = self.surf.get_rect()
        self.location = loc
        self.zoom = 2


class ClassEventHandle():
    def __init__(self):
        self.input = {}
        self.input["key"] = []
        self.input["mouse"] = []
        self.input["order"] = []

    def update(self, surface):
        resize = False
        for event in pg.event.get():
            # if event.type == pg.USEREVENT:
            #     frame += 1
            if event.type in [KEYDOWN, KEYUP]:
                self.input["key"].append(event)
            elif event.type == MOUSEBUTTONDOWN:
                self.input["mouse"].append(event)
            elif event.type == QUIT:
                quit()

        for event in self.input["key"]:
            Key = event.key
            State = event.type
            # Keep track of what keys are pressed. Their order in the list is important.
            for i, j in enumerate(self.input["order"]):
                if j == Key:
                    self.input["order"].pop(i)
                self.input["order"].append(Key)

            if event.type == pg.VIDEORESIZE:
                old_surface_saved = surface
                surface = pg.display.set_mode((event.w, event.h),
                                                  pg.RESIZABLE)
                surface.blit(old_surface_saved, (0, 0))
                del old_surface_saved
                resize= True


        return self.input, resize


pg.init()

SCREEN = pg.display.set_mode((1200, 800),pg.RESIZABLE, vsync=0)
CLOCK = pg.time.Clock()

GROUP = {}


PLAYAREA = [ClassPlayArea((1200, 800), (0,0))]

INPUT = ClassEventHandle()

# Initial GUI menu.
GROUP[0] = gui.MainMenu(PLAYAREA[0])
while True:
    # Update Playareas
    for obj in GROUP.values():
        obj.update(SCREEN, GROUP, INPUT.update(PLAYAREA[0].surf))

    pg.display.update()

    pg.display.set_caption(str(CLOCK.get_fps()))
    #
    # pg.display.update()
    if pg.key.get_pressed()[32]:
        CLOCK.tick(5)
    else:
        CLOCK.tick(2000)
        pass

