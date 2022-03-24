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

class Joystick():
    def __init__(self):
        self.type = "joy"
        self.joystick = pg.joystick.Joystick(0)


class Keyboarder():
    def __init__(self):
        self.type = "key"
        self.map = {
            97: "left",
            119: "up",
            115: "down",
            100: "right",
            102: "action"
        }
        self.order = []

class ClassEventHandle():
    def __init__(self):
        self.Controllers = []
        self.Controllers.append(
            Joystick()
        )

    def update(self, surface):
        input = {}
        input["controller"] = self.Controllers
        input["mouse"] = []
        key = []

        resize = False
        for event in pg.event.get():
            # if event.type == pg.USEREVENT:
            #     frame += 1
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
                # print("BRUH")

        for event in key:
            for controller in self.Controllers:
                if controller.type == "joy":
                    continue
                mapping = controller.map.get(event.key)
                if mapping:
                    controller.order = [i for i in controller.order if i != mapping]
                    if event.type == 768:
                        controller.order.append(mapping)

        return input, resize


pg.init()

SCREEN = pg.display.set_mode((1200, 800),pg.RESIZABLE, pg.OPENGLBLIT, vsync=0)
CLOCK = pg.time.Clock()

GROUP = {}


PLAYAREA = [ClassPlayArea((1200, 800), (0,0))]

INPUT = ClassEventHandle()

# Initial GUI menu.
GROUP[0] = gui.MainMenu(PLAYAREA[0])
while True:
    # Update Playareas
    for obj in GROUP.values():
        input, resize = INPUT.update(PLAYAREA[0].surf)
        obj.update(SCREEN, GROUP, input, resize)

    pg.display.flip()

    pg.display.set_caption(str(CLOCK.get_fps()))
    if pg.key.get_pressed()[32]:
        CLOCK.tick(5)
    else:
        CLOCK.tick(2000)
        pass

