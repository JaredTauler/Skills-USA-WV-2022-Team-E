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
		self.shape = pm.Poly.create_box(self.body, (32,32))
		self.shape.density = 1
		self.shape.friction = 1
		self.shape.elasticity = .3
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

		self.surf = pg.Surface((32,32))
		pygame.draw.rect(
			self.surf,
			[255, 255, 255],
			(0, 0, 32, 32)
		)

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

		# if not self.netplayer:
		# 	# Update camera location
		# 	screen.location = (
		# 		-self.body.position.x + screen.get_centercenter[0],
		# 		-self.body.position.y + screen.get_center()[1]
		# 	)

		# pg.draw.polygon(screen.surf, [255, 0, 0], verts(self.shape, screen))
		x = int(self.shape.body.position[0])
		y = int(self.shape.body.position[1])
		screen.blit(self.surf, (x,y))


# Tiles
class TileLayer():
	def __init__(self, internal_surf_size):
		self.tiles = []
		self.tilemap = {}
		self.surf = pg.Surface(internal_surf_size, pg.SRCALPHA)


	def draw(self, screen):
		for tile in self.tiles:
				x = int(tile.shape.body.position[0])
				y = int(tile.shape.body.position[1])

				self.surf.blit(
					self.tilemap[tile.textureid],
					(x, y, 32, 32)
				)
		self.surf = pg.transform.scale(self.surf, screen.get_rect().size)

	# def update(self, screen, group, input, space, surf):
	# 	pass
	# 	# self.draw(screen, space, surf)


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
		n = 32
		dir = "map/map1/"  # base dir from which files being getten from.

		def strip_from_sheet(sheet, start, size, columns, rows=1):
			frames = []
			for j in range(rows):
				for i in range(columns):
					location = (start[0] + size[0] * i, start[1] + size[1] * j)
					frames.append(sheet.subsurface(pg.Rect(location, size)))
			return frames

		sheet = pg.image.load(dir + 'rocks.png')
		TL.tilemap = strip_from_sheet(sheet, (0, 0), (32, 32), 9, 4)

		import json
		with open(dir + "map1.json") as f:
			js = json.load(f)
			x = 0
			y = 0
			for gid in js["layers"][0]["data"]:
				if gid != 0:
					gid = gid -1
					TL.tiles.append(Tile((n, n), (x * n, y * n), space, gid))

				x += 1
				if x == js["width"]:
					y += 1
					x = 0

	def __init__(self, screen, Forclient):
		self.screen = screen
		self.surf = None
		self.zoom_scale = .5

		n = 32
		ratio = (16,9)
		tiles = 5
		func = lambda ratio: (ratio*tiles)*n
		self.internal_surf_size = (
			func(ratio[0])
			,func(ratio[1])
		)

		self.internal_surf = pg.Surface(self.internal_surf_size, pygame.SRCALPHA)
		self.internal_rect = self.internal_surf.get_rect(center = (screen.get_width()/2, screen.get_height()/2))
		self.internal_surf_size_vector = pg.math.Vector2(self.internal_surf_size)

		self.space = pm.Space()  # PyMunk simulation
		self.space.gravity = (0, .1)

		self.Terrain = TileLayer(self.internal_surf_size)
		self.LoadMap(self.Terrain, self.space)
		self.Terrain.draw(screen)
		# bg = BG("bg.png")

		self.group = {}


		self.group["world"] = []
		# self.group["world"].append(bg)
		# self.group["world"].append(self.Terrain)

		self.group["player"] = []
		self.group["player"].append(Player(screen, self.space, False))
		self.group["entity"] = []
		import copy
	def update(self, screen, group, input, resize):
		if resize:
			self.Terrain.draw(screen)
		self.space.step(1) # Step pymunk sim

		# Update entities
		self.internal_surf.fill([0,0,0])
		for e in self.group.values():
			for obj in e:
				obj.update(self.internal_surf, self.group, input, self.space, self.internal_surf)

		blit = pg.transform.scale(self.internal_surf, screen.get_rect().size)
		screen.blit(blit, (0,0))
		screen.blit(self.Terrain.surf, (0, 0))
