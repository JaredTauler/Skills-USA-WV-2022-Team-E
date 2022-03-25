###############################
#
# Edited by Shane M.D.
#
###############################
import pygame
import pygame as pg
import pygame.font as pgfont
from function import *
import math
import game

def SurfCenter(s1, s2):
    return (
        s1.get_rect().center[0] - s2.get_rect().center[0],
        s1.get_rect().center[1] - s2.get_rect().center[1]
    )

def MouseOver(r):
    m = pg.mouse.get_pos()
    return (
        m[0] in range(r.x, r.width + r.x)
        and
        m[1] in range(r.y, r.height + r.y)
    )

# Made by Shane M.D.
class ClassButton():
    def __init__(self,x,y,width,height,image,imagehover,button_type):       # Button type has to be a string value of "Button" or "Joystick"
        self.width = width
        self.height = height
        self.img1path = pg.image.load(image)
        self.img2path = pg.image.load(imagehover)
        self.image = pg.transform.scale(self.img1path,(self.width,self.height)).convert_alpha()
        self.image2 = pg.transform.scale(self.img2path,(self.width,self.height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
        self.curimg = self.image

        self.Type = button_type

    def update(self,surface,Input):
        action = False
        pos = pygame.mouse.get_pos()
        if self.Type == 'Button':
            if self.rect.collidepoint(pos):
                self.curimg = self.image2

                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    self.clicked = True
                    action = True
                    self.curimg = self.image

                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

            if not self.rect.collidepoint(pos) and self.clicked == False:
                self.curimg = self.image

        # This is to get the A/B input of the controller to Ready Up
        elif self.Type == 'Joystick':
            pass

        else:
            print('Button_Type not Defined/Recognized.')

        surface.blit(self.curimg,(self.rect.x, self.rect.y))
        return action


class MainMenu:
    def __init__(self, screen):
        # self.surf = pg.Surface(surf)
        # self.rect = self.surf.get_rect()
        self.elem = {}

        font = pg.font.SysFont("calibri", 100)

        self.elem["background"] = ClassButton(0,0,1200,800,'./gui/background.png','./gui/background.png','Button')
        self.elem["logo"] = ClassButton(32, 50, 653, 329, './gui/logo.png', './gui/logo.png', 'Button')

        self.elem["startcase"] = ClassButton(32,430,691,145,'./gui/startcase.png','./gui/startcasehover.png','Button')
        self.elem["quit"] = ClassButton(32,600,500,138,'./gui/quit.png','./gui/quithover.png','Button')

    def update(self, screen, group, Input, resize):

        # Events are called using the update of the Button now
        if self.elem["startcase"].update(screen,Input):
            group[0] = game.Game(screen, Input)

        if self.elem["quit"].update(screen,Input):
            pg.quit()

        for e in self.elem.values():
            act = e.update(screen, Input)



class P_Select:
    def __init__(self, screen, back):
        # self.surf = pg.Surface(surf)
        # self.rect = self.surf.get_rect()
        self.back = back
        self.elem = {}

        self.elem["p1"] = ClassButton(32, 50, 691, 145, './gui/p2nr.png', './gui/p2r.png',"Joystick")

    def update(self, screen, group, Input, resize):

        screen.fill([121, 100, 100])
        for e in self.elem.values():
            act = e.update(screen, Input)
            if act != None:
                if act == "test":
                    pass
                elif act == "back":
                    group[0] = self.back

class Win:
    def __init__(self, screen, back):
        # self.surf = pg.Surface(surf)
        # self.rect = self.surf.get_rect()
        self.back = back
        self.elem = {}

        self.elem[''] = ClassButton()

    def update(self, screen, group, Input, resize):

        for e in self.elem.values():
            act = e.update(screen, Input)
            if act != None:
                if act == "test":
                    pass
                elif act == "back":
                    group[0] = self.back