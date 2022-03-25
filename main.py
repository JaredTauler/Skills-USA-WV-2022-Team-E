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
        self.ready = 0

class ClassEventHandle():
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

            elif event.type == pg.JOYDEVICEREMOVED:
                for seat in FLOW["seat"]:
                    if seat.joystick:
                        if seat.joystick.get_instance_id() == event.instance_id:
                            seat.joystick = None
                            break

            elif event.type == pg.JOYDEVICEADDED:
                for seat in FLOW["seat"]:
                    if seat.joystick is None:
                        seat.joystick = pg.joystick.Joystick(
                            event.device_index
                        )
                        break


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

# Assign controllers to seats.
for i, j in zip(
        FLOW["seat"],
        range(pg.joystick.get_count())
):
    i.joystick = pg.joystick.Joystick(j)

PLAYAREA = [ClassPlayArea((1200, 800), (0,0))]

INPUT = ClassEventHandle()

# Initial GUI menu.
FLOW["state"] = gui.MainMenu(PLAYAREA[0], FLOW)
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

