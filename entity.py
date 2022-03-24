import json
import random
import math
import pygame as pg
from function import *
import pymunk as pm

def Destroy(game, shape, space):
	space.remove(shape, shape.body)
	game.group["entity"].remove(
		shape.body.ParentObject
	)
	shape.body.ParentObject = None

class Sprite():
	def __init__(self):
		self.surf = None
		self.last_angle = None
		self.last_imagecenter = None

		self.shape = None
		self.body = None

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
			image, center = rot_center(self.surf, x, y)
			center = self.surf.get_rect(center=self.surf.get_rect(center=(x, y)).center)

		game.internal_surf.blit(
			image,
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
			math.sin(throw_rad) * 10,
			math.cos(throw_rad) * 10
		)

class Banana(Throwable):
	Collision_ID = 11

	@staticmethod
	def Collide_Player(arbiter, space, data):
		return False

	@staticmethod
	def Collide_Wall(arbiter, space, data):
		# if random.choices([True, False], weights = (1,4))[0]:
		if True:
			game = data["game"]
			shape = arbiter.shapes[1]
			# print(shape.body.rotation_vector.angle_degrees)
			v = shape.body.rotation_vector.angle_degrees
			rad = lambda: math.radians(
				( 180 if random.choice([True,False]) else 0) +
				((v+90) + random.randint(-1,1))
			)

			particles = []
			for i in range(random.randrange(10, 20)):
				game.group["entity"].append(
					BananaParticle(
						game.space,
						shape.body.position,
						rad(),
						velocity=random.randint(5,15)
					)
				)

			space.remove(shape, shape.body)
			try:
				game.group["entity"].remove(
					shape.body.ParentObject
				)
			except:
				pass
			shape.body.ParentObject = None

			return False
		else:
			return True

	def __init__(self, game, aim_dir, spawn):
		x = 32
		y = 16
		super().__init__(
			game.space,
			(x, y),
			spawn,
			JoyToRad(aim_dir)
		)
		self.shape.collision_type = Banana.Collision_ID
		self.body.ParentObject = self
		self.rotate = True
		# Change rotation of thrown object according to joystick aim
		self.body.apply_force_at_local_point(
			(0,100),
			(JoyToRad(aim_dir)*10,0)
		)

		self.surf = pg.Surface((x, y)).convert_alpha()
		self.surf = pg.image.load("entity/banana.png")
		self.surf = pg.transform.scale(self.surf, (x, y))

	def update(self, *args):
		game = args[0]
		self.draw(game)

class Particle(Sprite):
	def __init__(self,
				 space, radius, position, throw_rad, velocity
				 ):
		super().__init__()

		self.body = pm.Body()
		self.body.position = position
		self.shape = pm.Circle(self.body, radius=radius)
		self.shape.density = .001
		self.shape.friction = .1
		self.shape.elasticity = .5
		space.add(self.body, self.shape)
		# self.shape.collision_type = 1

		self.body.velocity = (
			math.sin(throw_rad) * velocity,
			math.cos(throw_rad) * velocity
		)

		self.death_countdown = 0
		self.alpha = 255


	def Die(self, *args):
		game = args[0]
		if self.body.position[0] < 0 or self.body.position[0] > game.internal_surf_size[0] or \
				self.body.position[1] < 0 or self.body.position[1] > game.internal_surf_size[1]:
			game.space.remove(self.shape, self.body)
			game.group["entity"].remove(
				self.body.ParentObject
			)
			self.body.ParentObject = None
		#


		self.death_countdown -= 1
		if self.death_countdown <= 0:
			self.alpha -= 1
			if self.alpha <= 200:
				self.alpha -= 7
				try:
					self.body.collision_type = 0
				except: pass
				if self.alpha <= 0:
					print("BRUH")
					try:
						game.space.remove(self.shape, self.body)
						game.group["entity"].remove(
							self.body.ParentObject
						)
						self.body.ParentObject = None
					except: pass
		if self.alpha < 0:
			self.alpha = 0

class BananaParticle(Particle):
	Collision_ID = 12

	@staticmethod
	def Collide_Player(arbiter, space, data):
		game = data["game"]
		player = data["player"]
		shape = arbiter.shapes[1]

		player.damage.append(
			arbiter.total_ke * (shape.body.mass * 10)
		)

		Destroy(game, shape, space)

		return False

	@staticmethod
	def Collide_Wall(arbiter, space, data):
		return True

	def __init__(self, space, position, throw_rad, velocity):
		radius = random.randint(1, 6)

		super().__init__(
			space,
			radius,
			position,
			throw_rad,
			velocity=velocity
		)
		self.shape.collision_type = BananaParticle.Collision_ID
		self.shape.density = .001
		self.surf = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA).convert_alpha()
		self.surf.fill([255, 255, 0])
		self.start_ticker()

		self.death_countdown = 100
		self.alpha = 255

		# Keep a reference to this Object on self.body so we can smuggle it into Collision_Callback.
		self.body.ParentObject = self

	def start_ticker(self):
		self.ticker = 0
		self.tick_cycle = random.randint(5, 10)

	def update(self, *args):
		game = args[0]
		self.Die(game)
		self.ticker += 1
		if self.ticker == self.tick_cycle:  # Cycle over
			self.start_ticker()  # Restart
			self.surf.fill(
				[
					random.randint(200, 255),
					random.randint(200, 255),
					0,
					self.alpha
				]
			)
		self.draw(game)

class Fire(Particle):
	Collision_ID = 10

	@staticmethod
	def Collide_Player(arbiter, space, data):
		print("BRUH")
		game = data["game"]
		shape = arbiter.shapes[1]
		space.remove(shape, shape.body)
		game.group["entity"].remove(
			shape.body.ParentObject
		)
		shape.body.ParentObject = None

		return False

	@staticmethod
	def Collide_Wall(arbiter, space, data):
		return True

	def __init__(self, space, position, throw_rad):
		radius = random.randint(2, 4)

		super().__init__(
			space,
			radius,
			position,
			throw_rad,
		)
		self.surf = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA).convert_alpha()
		self.surf.fill([255, 0, 0])
		self.start_ticker()

		self.death_countdown = 100
		self.alpha = 255

		# Keep a reference to this Object on self.body so we can smuggle it into Collision_Callback.
		self.body.ParentObject = self

	def start_ticker(self):
		self.ticker = 0
		self.tick_cycle = random.randint(5, 10)

	def update(self, *args):
		game = args[0]

		if self.ticker == self.tick_cycle:  # Cycle over
			self.start_ticker()  # Restart
			self.surf.fill(
				[
					random.randint(150, 255),
					random.randint(0, 155),
					0,
					self.alpha
				]
			)

		self.Die(game)
		self.draw(game)


