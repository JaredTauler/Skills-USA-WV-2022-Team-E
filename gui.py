import pygame as pg

import game
from function import *

class MainMenu:
    def __init__(self, screen, flow):
        self.surf = pg.Surface((1920,1080))
        self.elem = []

        self.ready = [{"a_hold":0,"b_hold":0} for i in range(len(flow["seat"]))]

        self.ready_surf = pg.image.load("gui/check.png").convert_alpha()
        self.not_ready_surf = pg.image.load("gui/x.png").convert_alpha()

        self.last_joy_count = pg.joystick.get_count()


    def update(self, screen, flow, Input, resize):
        self.surf.fill([0,0,0,0])
        for i, seat in enumerate(flow["seat"]):

            surf = pg.Surface((32, 32))

            if seat.joystick:
                if seat.joystick.get_button(0) == 1 and \
                flow["seat"][i].ready == 1 and \
                self.ready[i]["a_hold"] == 0:
                    flow["seat"][i].ready = 0
                    self.ready[i]["a_hold"] = 1

                elif seat.joystick.get_button(0) == 1 and self.ready[i]["a_hold"] == 0:
                    flow["seat"][i].ready = 1
                    self.ready[i]["a_hold"] = 1

                elif seat.joystick.get_button(0) == 0:
                    self.ready[i]["a_hold"] = 0

                if seat.joystick.get_button(1) == 1 and \
                flow["seat"][i].ready == -1 and \
                self.ready[i]["b_hold"] == 0:
                    flow["seat"][i].ready = 0
                    self.ready[i]["b_hold"] = 1

                elif seat.joystick.get_button(1) == 1 and self.ready[i]["b_hold"] == 0:
                    flow["seat"][i].ready = -1
                    self.ready[i]["b_hold"] = 1

                elif seat.joystick.get_button(1) == 0:
                    self.ready[i]["b_hold"] = 0

                surf.fill(seat.color)
            else:
                surf.fill([255,255,255])
            x = (
                        (screen.get_size()[0] / (len(flow["seat"]) + 1)) * (i + 1)
                        - surf.get_width()/2
                    )
            self.surf.blit(
                surf,
                (x, 500)
            )

            indicator = None
            if flow["seat"][i].ready == 1:
                indicator = self.ready_surf
            elif flow["seat"][i].ready == -1:
                indicator = self.not_ready_surf
            if indicator:
                self.surf.blit(
                    indicator,
                    (x, 600)
                )
        
        # Start game if everyone with a controller is ready or not playing.
        fail = False
        playing = 0
        for ready, seat in zip(self.ready, flow["seat"]):
            print(seat.joystick)
            if seat.joystick is None:            
                continue
            if seat.ready == 0:
                fail = True
            elif seat.ready == 1:
                playing += 1
        if playing >= 1 and not fail:
            flow["state"] = game.Game(flow, Input, screen)

        screen.blit(
            self.surf,
            (0,0)
        )


class Win():
    def __init__(self, flow, screen,  player):
        self.surf = pg.Surface((1920,1080))
        self.winner = player
        winner_seat = flow["seat"][player.PlayerID]
        font = pg.font.Font(None, 32)

        c = [255,255,255]
        self.lines = [
            [font.render(f"Court adjourned!", True, c), 50],
            [player.surf, 50],
            [font.render(f"{winner_seat.name} has won this trial!", True, c), 50],
            [font.render(f"Throughout due process they:", True, c), 50],
            [font.render(f"Blew themselves up {self.winner.suicide} times.", True, c), 50],
        ]
        self.push_button = font.render(f"Press A to return to the main menu.", True, c), 70,

        self.no_input = 150

    def update(self, screen, flow, Input, resize):
        self.surf.fill([0,0,0,0])

        for i, line in enumerate(self.lines):
            line, dist = line
            # height = line.get_height() + (20* (i + 1))
            height = (dist * i) + line.get_height()
            print(height)
            self.surf.blit(line, line.get_rect(center=(screen.get_width()/2, height)))

        if self.no_input <= 0:
            if self.push_button not in self.lines:
                self.lines.append(self.push_button)
            for seat in flow["seat"]:
                if seat.joystick:
                    if seat.joystick.get_button(0):
                        flow["state"] = MainMenu(screen ,flow)
        else:
            self.no_input -= 1
        screen.blit(
            self.surf,
            (0,0)
        )
