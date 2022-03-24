import json
import random

import pygame
import pygame.draw
import pygame.gfxdraw as gfx
# import game
import pymunk
import pytmx
import xml.etree.ElementTree as ET

import pymunk as pm
import math
from function import *

class Sprite():
	def __init__(self):
		self.surf = None
		self.last_angle = None
		self.last_imagecenter = None

		self.shape = None
		self.body= None

		self.rotate = False

	def draw(self, game):
		x = self.shape.body.position[0]
		y = self.shape.body.position[1]

		if self.rotate:
			if self.last_angle == self.body.angle:
				image, center = rot_center(
					self.last_imagecenter[0],
					x, y
				)
			else:
				image, center = rot_center(
					self.surf,
					x, y,
					-self.body.rotation_vector.angle_degrees
				)
				self.last_angle = self.body.angle
				self.last_imagecenter = image, center
		else:
			image, center = rot_center(self.surf, x,y)
			center = self.surf.get_rect(center=self.surf.get_rect(center=(x, y)).center)

		game.internal_surf.blit(
			self.surf,
			(
				center.x + 16,
				center.y + 16,
			)
		)

class Throwable(Sprite):
	def __init__(self,
				 space, size, position, throw_rad
	):
		super().__init__()

		self.body = pm.Body()
		self.body.position = position
		self.shape = pm.Poly.create_box(self.body, size)
		self.shape.density = 1
		self.shape.friction = .1
		self.shape.elasticity = .5
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

		# Convert Joystick Values to an angle
		self.body.velocity = (
			math.sin(throw_rad) *10,
			math.cos(throw_rad) *10
		)

class Banana(Throwable):
	def __init__(self, space, aim_dir, spawn):
		x = 32
		y = 16
		super().__init__(
			space,
			(x,y),
			spawn,
			JoyToRad(aim_dir)
		 )
		self.surf = pg.Surface((x,y)).convert_alpha()
		self.surf = pg.image.load("entity/banana.png")
		self.surf = pg.transform.scale(self.surf, (x,y))

class Particle(Sprite):
	def __init__(self,
				 space, radius, position, throw_vect2
	):
		super().__init__()

		self.body = pm.Body()
		self.body.position = (400,400)#position
		self.shape = pm.Circle(self.body, radius=radius)
		self.shape.collision_type = 10
		self.shape.density = .001
		self.shape.friction = .1
		self.shape.elasticity = .5
		space.add(self.body, self.shape)
		# self.shape.collision_type = 1

		self.body.velocity = (
			math.sin(throw_vect2[0]) *10,
			math.cos(throw_vect2[1]) *10
		)


class Fire(Particle):
	Collision_ID = 10

	@staticmethod
	def Collision_Callback(arbiter, space, data):
		game = data["game"]
		shape = arbiter.shapes[1]
		space.remove(shape, shape.body)
		game.group["entity"].remove(
			shape.body.ParentObject
		)
		import gc
		print(gc.get_referrers(arbiter.shapes[1].body.ParentObject))

		return False

	def __init__(self, space, position, throw_vect2, group):
		# super().__init__(space, radius, position, throw_vect2)
		radius = random.randint(2, 4)

		super().__init__(
			space,
			radius,
			position,
			throw_vect2,
		)
		self.surf = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA).convert_alpha()
		self.surf.fill([255,0,0])
		self.start_ticker()

		self.death_tick = 0
		self.start_death = 500
		self.alpha = 255

		# Keep a reference to this Object on self.body so we can smuggle it into Collision_Callback.
		self.body.ParentObject = self

	def start_ticker(self):
		self.ticker = 0
		self.tick_cycle = random.randint(5, 10)

	def update(self, *args):
		game = args[0]
		self.ticker += 1

		if self.ticker == self.tick_cycle:
			self.start_ticker()
			self.surf.fill(
				[
					random.randint(150,255),
					random.randint(0, 100),
					0,
					self.alpha
				 ]
			)

		# if self.death_tick == self.start_death:
		# 	self.alpha -= 1
		# 	if self.alpha == 100:
		# 		game.space.remove(self.shape, self.body)
		# 		return True
		# else:
		# 	self.death_tick += 1

		self.draw(game)

class Player():
	def __init__(self, game, PlayerID):
		self.InputID = PlayerID
		self.collision_ID = PlayerID # Might have to be changed in future

		# pm
		self.body = pm.Body()
		self.body.position = (100,100)
		self.shape = pm.Poly.create_box(self.body, (32,32))
		self.shape.collision_type = self.collision_ID
		self.shape.density = 1
		self.shape.friction = 1
		self.shape.elasticity = .3
		game.space.add(self.body, self.shape)


		self.surf = pg.Surface((32,32))
		pygame.draw.rect(
			self.surf,
			[255, 255, 255],
			(0, 0, 32, 32)
		)

		self.aim_dir = (0,0)

		self.health = 100

		self.bruh = False

	def update(self, *args):
		game = args[0]
		input = args[1]

		dir = [0,0]
		action = False

		controller = input["controller"][self.InputID]
		if controller.type == "key":
			for map in controller.order:
				if map == "left":
					dir = SumTup(dir, (-1, 0))
				elif map == "right":
					dir = SumTup(dir, (1, 0))
				elif map == "up":
					dir = SumTup(dir, (0, -1))
				elif map == "down":
					dir = SumTup(dir, (0, 1))
				elif map == "action":
					action = True
		else:
			dir = (
				controller.joystick.get_axis(0),
				controller.joystick.get_axis(1)
			)


			aim_dir = (
				controller.joystick.get_axis(2),
				controller.joystick.get_axis(3)
			)

			if not_deadzone(aim_dir, .5):
				self.aim_dir = aim_dir
			# print(aim_dir)
			action = controller.joystick.get_button(0) == 1

			# Right Trigger
			v = RangeChange(
				(-1,1), (0,1),
				controller.joystick.get_axis(5)
			)
			RightTrigger = v if v == 0 else False

		x = int(self.shape.body.position[0])
		y = int(self.shape.body.position[1])

		if action:

			# if not self.bruh:
			# 	self.bruh = True
				game.group["entity"].append(
					Fire(
						game.space,
						self.body.position,
						aim_dir,
						game.group
					)
				)
				# group["entity"].append(Banana(space, self.aim_dir, self.body.position))
		else:
			self.bruh = False

		mvspd = .2
		self.body.velocity = SumTup((dir[0]*mvspd, dir[1]*mvspd), self.body.velocity)


		game.internal_surf.blit(self.surf,
			(x,y)
		)


# Tiles
class TileLayer():
	def __init__(self, internal_surf_size):
		self.tiles = []
		self.tilemap = {}
		self.clean_surf = pg.Surface(internal_surf_size, pg.HWSURFACE)
		self.surf = self.clean_surf.copy()


	def draw(self, screen, bg):
		self.surf = self.clean_surf.copy()
		self.surf.blit(bg, (0,0))
		for tile in self.tiles:
				x = int(tile.shape.body.position[0])
				y = int(tile.shape.body.position[1])

				self.surf.blit(
					self.tilemap[tile.textureid],
					(x, y, 32, 32)
				)
		self.surf = pg.transform.scale(self.surf, screen.get_rect().size)

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

		self.internal_surf = pg.Surface(self.internal_surf_size, pg.HWSURFACE, ).convert_alpha()
		self.internal_rect = self.internal_surf.get_rect(center = (screen.get_width()/2, screen.get_height()/2))
		self.internal_surf_size_vector = pg.math.Vector2(self.internal_surf_size)

		self.space = pm.Space()  # PyMunk simulation
		self.space.gravity = (0, .1)



		dir = "map/map1/"
		img = pg.image.load(dir + "rainy.png").convert()
		self.bg = pg.transform.scale(img, self.internal_surf_size)

		self.Terrain = TileLayer(self.internal_surf_size)
		self.LoadMap(self.Terrain, self.space)
		self.Terrain.draw(screen, self.bg)



		self.group = {}


		self.group["world"] = []
		# self.group["world"].append(self.Terrain)

		self.group["player"] = []

		self.group["player"].append(Player(self, 0))

		self.group["entity"] = []

		# Collision IDs:
		for c in [
			Fire,
		]:
			for player in self.group["player"]:
				handler = self.space.add_collision_handler(
					player.collision_ID,
					c.Collision_ID
				)
				handler.data["game"] = self
				handler.begin = c.Collision_Callback

	def update(self, screen, group, input, resize):
		if resize:
			self.Terrain.draw(screen, self.bg)
		self.space.step(1) # Step pymunk sim

		# Update entities
		self.internal_surf.fill([0,0,0,0])
		for e in self.group.values():
			for obj in e:
				obj.update(self, input, e)
		blit = pg.transform.scale(self.internal_surf, screen.get_rect().size)
		screen.blit(self.Terrain.surf, (0, 0))
		screen.blit(blit, (0,0))

