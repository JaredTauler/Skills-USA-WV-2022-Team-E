import json

import pygame
import pygame.draw
import pygame.gfxdraw as gfx
# import game
import pytmx
import xml.etree.ElementTree as ET

import pymunk as pm

from function import *

# class Bomb():
# 	def __init__(self, parent, space):
# 		self.body = pm.Body()
# 		self.body.position = (100,100)
# 		self.radius = 20
# 		self.shape = pm.Circle(self.body, self.radius)
# 		self.shape.density = 1
# 		self.shape.friction = 1
# 		self.shape.elasticity = .3
# 		space.add(self.body, self.shape)
# 		self.shape.collision_type = 1
#
# 		# self.surf = pg.image.load("bomb")
# 		self.surf = pg.transform.scale(
# 			pg.image.load("map/map1/bomb.png"),
# 			(self.radius*2, self.radius*2)
# 		)
# 		self.surf.set_colorkey((0, 0, 0))
#
# 	def draw(self, screen, space):
#
# 		loc = SumTup(self.shape.body.position, screen.location)
# 		x = int(loc[0]-self.radius)
# 		y = int(loc[1] - self.radius)
# 		screen.surf.blit(
# 			rot_center(self.surf, self.body.angle, 0, 0)[0],
# 			(x,y)
# 		)
#
# 	def update(self, screen, group, input, space):
# 		print(self.shape.body.position)
# 		self.draw(screen, space)
#
# class Projectile():
# 	def __init__(self, parent, space):
# 		self.body = pm.Body()
# 		self.body.position = (100,100)
# 		self.radius = 20
# 		self.shape = pm.Circle(self.body, self.radius)
# 		self.shape.density = 1
# 		self.shape.friction = 1
# 		self.shape.elasticity = .3
# 		space.add(self.body, self.shape)
# 		self.shape.collision_type = 1
#
# 	def update(self, screen, group, input, space):
# 		pass
# 		# print(self.shape.body.position)
# 		# self.draw(screen, space)


class Player():
	def __init__(self, screen, space, netplayer):
		# net
		self.netplayer = netplayer
		self.ticklist = []

		# pm
		self.body = pm.Body()
		self.body.position = (100,100)
		self.shape = pm.Poly.create_box(self.body, (30,30))
		self.shape.density = 1
		self.shape.friction = 1
		self.shape.elasticity = .3
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

	def update(self, screen, group, input, space, surf):

		while len(self.ticklist) != 0:
			t = self.ticklist[0]
			self.body.position = t["location"]
			self.body.velocity = t["velocity"]
			self.ticklist.pop(0)
			# print("BRUH")
		key = {"left": 97, "up": 119, "down": 115, "right": 100, "action": 102}
		dir = [0,0]
		action = False
		if not self.netplayer:
			if pg.key.get_pressed()[key["left"]]:
				dir = SumTup(dir, (-1, 0))
			if pg.key.get_pressed()[key["right"]]:
				dir = SumTup(dir, (1, 0))
			if pg.key.get_pressed()[key["up"]]:
				dir = SumTup(dir, (0, -1))
			if pg.key.get_pressed()[key["down"]]:
				dir = SumTup(dir, (0, 1))
			if pg.key.get_pressed()[key["action"]]:
				action = True

		# if action:
		# 	group["entity"].append(Bomb(self, space))

		mvspd = .2
		self.body.velocity = SumTup((dir[0]*mvspd, dir[1]*mvspd), self.body.velocity)

		if not self.netplayer:
			# Update camera location
			screen.location = (
				-self.body.position.x + screen.rect.center[0],
				-self.body.position.y + screen.rect.center[1]
			)

		# pg.draw.polygon(screen.surf, [255, 0, 0], verts(self.shape, screen))
		x = int(self.shape.body.position[0])
		y = int(self.shape.body.position[1])
		pygame.draw.rect(
			surf,
			[255, 255, 255],
			(x, y, 30, 30)
		)


# Tiles
class TileLayer():
	def __init__(self):
		self.tiles = []
		self.tilemap = {}
		# self.surf = pg.Surface((10000, 10000))

	def draw(self, screen, space, surf):
		# return
		for tile in self.tiles:
				# x = int(tile.shape.body.position[0] + screen.location[0])
				# y = int(tile.shape.body.position[1] + screen.location[1])
				x = int(tile.shape.body.position[0])
				y = int(tile.shape.body.position[1])

				pygame.draw.rect(
					surf,
					[255,255,255],
					(x, y, 30, 30)
				)
				# print(verts(tile.shape, screen))
				pass
			# except:
			# 	pass

	def update(self, screen, group, input, space, surf):
		self.draw(screen, space, surf)


class Tile(pg.sprite.Sprite):
	def __init__(self, size, loc, space, textureid):
		pg.sprite.Sprite.__init__(self)
		# textures make game slow. idk why.
		self.textureid = textureid # Remember texture ID rather than texture
		# pm
		self.body = pm.Body(body_type=pm.Body.STATIC)
		self.body.position = loc
		self.shape = pm.Poly.create_box(self.body, size)
		self.shape.density = 1
		self.shape.elasticity = 1
		space.add(self.body, self.shape)
		self.shape.collision_type = 1




class BG:
	def __init__(self, bg):
		dir = "map/map1/"
		img = pg.image.load(dir + bg).convert()

		self.surf = pg.transform.scale(img, (1800,1800))

	def draw(self, screen, space):
		x = int(screen.location[0] * .3)
		y = int(screen.location[1] * .3)
		screen.surf.blit(self.surf, (x,y))

	def update(self, screen, group, input, space):
		self.draw(screen, space)

class Game:

	def LoadMap(self, TL, space):
		dir = "map/map1/"  # base dir from which files being getten from.

		# PARSE TSX FILE
		tree = ET.parse(dir + "base.tsx")
		root = tree.getroot()
		tiles = {}  # surfs
		for child in root:  # For elem in XML
			if child.tag == "tile":  # Make sure getting a tile
				for i in child:
					loc = dir + i.attrib["source"]
					surf = pygame.image.load(dir + i.attrib["source"]).convert()
					tiles[int(child.attrib["id"]) + 1] = surf
		TL.tilemap = tiles
		tm = pytmx.load_pygame(dir + ".tmx")  # FIXME stop this from auto loading images... ill do it myself thank you.
		for x, y, gid, in tm.get_layer_by_name("terrain"):
			# print(gid)
			if gid == 0:
				continue
			n = 30
			TL.tiles.append(Tile((n, n), (x * n, y * n), space, gid))

	def __init__(self, screen, Forclient):
		self.screen = screen
		self.zoom_scale = .5
		self.internal_surf_size = (2400,1400)
		self.internal_surf = pg.Surface(self.internal_surf_size, pygame.SRCALPHA)
		self.internal_rect = self.internal_surf.get_rect(center = (screen.rect.width/2, screen.rect.height/2))
		self.internal_surf_size_vector = pg.math.Vector2(self.internal_surf_size)

		self.space = pm.Space()  # PyMunk simulation
		self.space.gravity = (0, .1)

		self.Terrain = TileLayer()
		self.LoadMap(self.Terrain, self.space)
		# bg = BG("bg.png")

		self.group = {}


		self.group["world"] = []
		# self.group["world"].append(bg)
		self.group["world"].append(self.Terrain)

		self.group["player"] = []
		self.group["player"].append(Player(screen, self.space, False))
		self.group["entity"] = []

	def update(self, screen, group, input):
		self.space.step(1) # Step pymunk sim

		# Update entities
		self.internal_surf.fill([0, 0, 0])
		for e in self.group.values():
			for obj in e:
				obj.update(screen, self.group, input, self.space, self.internal_surf)
		blit = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
		screen.surf.blit(blit, (0,0))
