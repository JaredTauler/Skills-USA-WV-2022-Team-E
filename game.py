import random

import gui
from function import *
import entity
import pygame
import pygame.draw
import pymunk as pm

class Player(entity.Sprite):
	def __init__(self, game, Seat, id):
		super().__init__()
		self.PlayerID = id
		self.InputID = id
		self.collision_ID = id + 1  # Collision_type = 0 is disasterous

		# pm
		self.body = pm.Body()
		self.body.position = (100, 100)
		self.shape = pm.Poly.create_box(self.body, (32, 32), radius=.1)
		self.shape.collision_type = self.collision_ID
		self.shape.density = 1
		self.shape.friction = 1
		self.shape.elasticity = .1
		game.space.add(self.body, self.shape)

		self.color = Seat.color
		self.surf = pg.Surface((32, 32)).convert_alpha()
		self.surf.fill(self.color)

		self.aim_dir = (0, 0)

		self.health = 100

		self.joystick = Seat.joystick

		self.damage = []

		self.rumble_tick = 0
		self.rumbling = False
		self.rotate = True

		self.dead = False
		self.respawn = 0

		self.kills = []
		self.suicide = 0

		## Pointer
		# Load animation
		img = pg.image.load("gui/pointer.png")
		self.pointer_surfs = strip_from_sheet(img, (0,0), (16,16))
		self.pointer_position = (0,0)

		self.action_cooldown = 0
		self.action_cooldown_max = 100

	# Rumble logic
	def RumbleLogic(self):
		if self.rumble_tick <= 0:
			self.stop_rumble()
		else:
			self.rumble_tick -= 1
			self.start_rumble()

	def stop_rumble(self):
		if self.rumbling:
			self.joystick.stop_rumble()
			self.rumbling = False

	def start_rumble(self):
		if not self.rumbling:
			if self.last_health < 20:
				self.joystick.rumble(100, 0, 0)
			else:
				self.joystick.rumble(0, 100, 0)
			self.rumbling = True

	def update(self, *args):
		game = args[0]
		if self.dead: # Dead
			self.RumbleLogic()
			self.respawn -= 1

			# Respawn logic
			if self.respawn <= 0:
				self.dead = False
				self.health = 100
				game.space.add(self.body)

				# Find least busy spawn point
				best_point = None
				best_dist = None
				for point in game.PlayerSpawnPoints:
					for player in game.group["player"]:  # Check every players pos
						if player is self:  # Dont care about self
							continue

						dist = math.dist(player.body.position, point["position"])
						if best_dist == None:
							best_dist = dist
							best_point = point

						# new best point set to current distance if current distance bigger than best point.
						elif dist > best_dist:
							print(dist, best_dist)
							best_dist = dist
							best_point = point

				if best_point != None: # Should happen under normal circumstances
					self.body.position = best_point["position"]
				self.rumble_tick = 5

			return

		# Get input
		dir = [0, 0]
		action = False
		# Joystick
		dir = (
			self.joystick.get_axis(0),
			self.joystick.get_axis(1)
		)

		aim_dir = (
			self.joystick.get_axis(2),
			self.joystick.get_axis(3)
		)

		if not_deadzone(aim_dir, .5):
			self.aim_dir = aim_dir
		# print(aim_dir)
		action = self.joystick.get_button(0) == 1

		# Right Trigger
		v = RangeChange(
			(-1, 1), (0, 1),
			self.joystick.get_axis(5)
		)
		RightTrigger = v if v == 0 else False

		# if self.body.velocity.y > 0: if

		# Calculate damage
		if len(self.damage):
			self.last_health = self.health
			while len(self.damage): # while there are items in list
				self.rumble_tick += self.damage[0]["damage"] * 2
				self.health -= self.damage[0]["damage"]

				# On death
				if self.health <= 0 and not self.dead:
					author = self.damage[0]["author"]
					if author == self.PlayerID:
						self.suicide += 1
					else:
						author.kills.append(self.PlayerID)
					game.space.remove(self.body)
					self.dead = True
					self.respawn = 500
					# Death particles
					for i in range(random.randint(30, 60)):
						game.group["entity"].append(
							entity.PlayerDeathParticle(
								game.space,
								self.body.position,
								self.color
							)
						)
				self.damage.pop(0)

			self.rumble_tick = round(self.rumble_tick)
			self.rumble_tick = clamp(self.rumble_tick,3,30)

		self.RumbleLogic()

		x = int(self.shape.body.position[0])
		y = int(self.shape.body.position[1])

		if action:
			if self.action_cooldown <= 0:
				self.action_cooldown = self.action_cooldown_max
				print(self.pointer_position)
				game.group["entity"].append(
					entity.Banana(
						game,
						self.aim_dir,
						self.pointer_position,
						self
					)
				)

		elif self.action_cooldown:
			self.action_cooldown -= 1

		mvspd = .2
		self.body.velocity = SumTup((dir[0] * mvspd, dir[1] * mvspd), self.body.velocity)
		self.draw(game)

		# Pointer
		d = 50
		rad = JoyToRad(self.aim_dir)
		pos = self.body.position
		x = pos.x + (d * math.sin(rad))
		y = pos.y + (d * math.cos(rad))
		self.pointer_position = (x,y)

		# Calculate which pointer frame to display
		a = self.action_cooldown_max/len(self.pointer_surfs) # when to increment (eg: 4/2=2, change frame every 2 ticks)
		# where countdown is, -max because we want the number to count up, +1 so no divide by 0 error
		b = (self.action_cooldown-self.action_cooldown_max) + 1

		index = -round(b / a)-1
		# Draw
		image, rect = rot_center(self.pointer_surfs[index], x,y)
		game.internal_surf.blit(
			image, rect
		)

# Tiles
class TileLayer():
	def __init__(self, internal_surf_size):
		self.tiles = []
		self.tilemap = {}
		self.clean_surf = pg.Surface(internal_surf_size, pg.HWSURFACE)
		self.surf = self.clean_surf.copy()

	def draw(self, screen):
		self.surf = self.clean_surf.copy()
		# self.surf.blit(bg, (0, 0))
		for tile in self.tiles:
			x = int(tile.shape.body.position[0])
			y = int(tile.shape.body.position[1])
			try:
				self.surf.blit(
					self.tilemap[tile.textureid],
					(x, y, 32, 32)
				)
			except:
				pass
		self.surf = pg.transform.scale(self.surf, screen.get_rect().size)


class Tile(pg.sprite.Sprite):
	Collision_ID = 9

	def __init__(self, size, loc, space, textureid):
		pg.sprite.Sprite.__init__(self)
		# textures make game slow. idk why.
		self.textureid = textureid  # Remember texture ID rather than texture
		# pm
		self.body = pm.Body(body_type=pm.Body.STATIC)
		self.body.position = loc
		self.shape = pm.Poly.create_box(self.body, size)
		self.shape.density = 1
		self.shape.elasticity = 1
		self.shape.collision_type = 9
		space.add(self.body, self.shape)


class Game:

	def LoadMap(self, TL, space):
		n = 32
		dir = "map/map1/"  # base dir from which files being getten from.

		sheet = pg.image.load(dir + 'rocks.png')
		t = 32
		TL.tilemap = strip_from_sheet(sheet, (0, 0), (t, t))

		import json
		with open(dir + "map1.json") as f:
			js = json.load(f)
			x = 0
			y = 0
			for layer in js["layers"]:
				if layer["name"] == "spawner":
					for point in layer["objects"]:
						self.PlayerSpawnPoints.append(
							{
								"position": (point["x"], point["y"])
							}
						)

				elif layer["name"] == "terrain":
					for gid in layer["data"]:
						if gid != 0:
							TL.tiles.append(Tile((n, n), (x * n, y * n), space, gid - 1))

						x += 1
						if x == js["width"]:
							y += 1
							x = 0


	def __init__(self, Flow, input, screen):
		self.PlayerSpawnPoints = []
		self.screen = screen
		self.surf = None
		self.zoom_scale = .5

		n = 32
		ratio = (16, 9)
		tiles = 5
		func = lambda ratio: (ratio * tiles) * n
		self.internal_surf_size = (
			func(ratio[0])
			, func(ratio[1])
		)

		self.internal_surf = pg.Surface(self.internal_surf_size, pg.HWSURFACE, ).convert_alpha()
		print(screen)
		self.internal_rect = self.internal_surf.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
		self.internal_surf_size_vector = pg.math.Vector2(self.internal_surf_size)

		self.space = pm.Space()  # PyMunk simulation
		self.space.gravity = (0, .1)

		dir = "map/map1/"
		img = pg.image.load(dir + "rainy.png").convert()
		self.bg = pg.transform.scale(img, self.internal_surf_size)

		self.Terrain = TileLayer(self.internal_surf_size)
		self.LoadMap(self.Terrain, self.space)
		self.Terrain.draw(screen)

		self.group = {}

		self.group["world"] = []
		# self.group["world"].append(self.Terrain)

		self.group["player"] = []

		for i, j in enumerate(Flow["seat"]):
			if Flow["seat"][i].ready:
				self.group["player"].append(Player(self, j, i))


		self.group["entity"] = []


		# Collision IDs:
		for c in [
			entity.Fire, entity.Banana, entity.BananaParticle
		]:
			for player in self.group["player"]:
				handler = self.space.add_collision_handler(
					player.collision_ID,
					c.Collision_ID
				)
				handler.data["player"] = player
				handler.data["game"] = self
				handler.post_solve = c.Collide_Player

			# Collision with tiles
			handler = self.space.add_collision_handler(
				Tile.Collision_ID,
				c.Collision_ID
			)
			handler.data["game"] = self
			handler.begin = c.Collide_Wall

		self.rects = []

	def update(self, screen, flow, input, resize):
		if resize:
			self.Terrain.draw(screen)
			screen.blit(self.Terrain.surf, (0, 0))
			pg.display.update()
		self.space.step(1)  # Step pymunk sim

		# Update entities
		self.internal_surf.fill([0,0,0,0])
		for e in self.group.values():
			for obj in e:
				obj.update(self, input, e, )

		for player in self.group["player"]:
			if len(player.kills) == 10:
				flow["state"] = gui.Win(player.PlayerID) # Handoff gameflow to win GUI

		blit = pg.transform.scale(self.internal_surf, screen.get_rect().size)

		screen.blit(self.bg, (0,0))
		screen.blit(self.Terrain.surf, (0, 0))
		screen.blit(blit, (0, 0))
