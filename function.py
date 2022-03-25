import copy
import pygame as pg
import math
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def RadToDeg(rad):
	return (rad / math.pi * 180) + (0 if rad > 0 else 360)
def JoyToRad(a):
	return math.atan2(a[0], a[1])
def not_deadzone(a, deadzone):
	for x in a:
		if (-x if x < 0 else x) > deadzone:
			return True

def RangeChange(Old, New, val):
    OldRange = (Old[1] - Old[0])
    NewRange = (New[1] - New[0])
    return (((val - Old[0]) * NewRange) / OldRange) + Old[0]


class WorldRect():
	def __init__(self, xy, wh):
		self.x, self.y = xy
		if type(wh) is pg.Rect:
			self.w, self.h = wh.w, wh.h
		else:
			self.w, self.h = wh.w

	def set(self, iter):
		self.x = iter[0]
		self.y = iter[1]

	def xy(self):
		return self.x, self.y
	def left(self):
		return self.x
	def right(self):
		return self.x + self.w
	def top(self):
		return self.y
	def bottom(self):
		return self.y + self.h

def SumTup(*a):
	x = [0,0]
	for i in a:
		x[0] += i[0]
		x[1] += i[1]
	return x

def DifTup(*a):
	x = [0,0]
	for i in a:
		x[0] -= i[0]
		x[1] -= i[1]
	return x
# this is going to happen thousands of times a frame and needs to be quick

left = lambda rect: rect[0][0]
right = lambda rect: rect[0][0] + rect[1][0]
top = lambda rect: rect[0][1]
bottom = lambda rect: rect[0][1] + rect[1][1]
def overlap(rect1, rect2):
	return (
		left(rect1) < right(rect2) and
		right(rect1) > left(rect2) and
		top(rect1) < bottom(rect2) and
		bottom(rect1) > top(rect2)
	)
def aspect_scale(rect, desired_rect):
    ix,iy = rect
    if ix > iy:
        # fit to width
        scale_factor = desired_rect[0]/float(ix)
        sy = scale_factor * iy
        if sy > desired_rect[1]:
            scale_factor = desired_rect[1]/float(iy)
            sx = scale_factor * ix
            sy = desired_rect[1]
        else:
            sx = desired_rect[0]
    else:
        # fit to height
        scale_factor = desired_rect[1]/float(iy)
        sx = scale_factor * ix
        if sx > desired_rect[0]:
            scale_factor = desired_rect[0]/float(ix)
            sx = desired_rect[0]
            sy = scale_factor * iy
        else:
            sy = desired_rect[1]

    return sx, sy

def strip_from_sheet(sheet, start, size):
	columns = int(sheet.get_width() / size[0])
	rows = int(sheet.get_height() / size[1])
	frames = []
	for j in range(rows):
		for i in range(columns):
			location = (start[0] + size[0] * i, start[1] + size[1] * j)
			frames.append(sheet.subsurface(pg.Rect(location, size)))
	return frames

def rot_center(image, x, y, angle=None):
	if angle != None:
		rotated_image = pg.transform.rotate(image, angle)
	else:
		rotated_image = image
	new_rect = rotated_image.get_rect(center=image.get_rect(center=(x+16, y+16)).center)

	return rotated_image, new_rect

def verts(shape):
	verts = []
	for v in shape.get_vertices():
		n = SumTup(
			v.rotated(shape.body.angle),
			# screen.location,
			shape.body.position
		)
		verts.append(n)
	return verts

def DifTup(*a):
	x = [0,0]
	for i in a:
		x[0] -= i[0]
		x[1] -= i[1]
	return x
# this is going to happen thousands of times a frame and needs to be quick

left = lambda rect: rect[0][0]
right = lambda rect: rect[0][0] + rect[1][0]
top = lambda rect: rect[0][1]
bottom = lambda rect: rect[0][1] + rect[1][1]
def overlap(rect1, rect2):
	return (
		left(rect1) < right(rect2) and
		right(rect1) > left(rect2) and
		top(rect1) < bottom(rect2) and
		bottom(rect1) > top(rect2)
	)

def draw_polygon(shape, screen):
	verts = []
	for v in shape.get_vertices():
		n = SumTup(
			v.rotated(shape.body.angle),
			screen.location,
			shape.body.position
		)
		verts.append(n)
		return verts

# AABB Collision.
def CollideWorldRect(rect1: WorldRect, rect2: WorldRect):
	# Determine if a collision is happening
	if (
		rect1.left() < rect2.right() and
		rect1.right() > rect2.left() and
		rect1.top() < rect2.bottom() and
		rect1.bottom() > rect2.top()
	):
		# OK. collision is happening, which side is closest?
		side = {
			"left": abs(rect1.right() - rect2.left()), # left
			"top": abs(rect1.bottom() - rect2.top()), # top
			"right": abs(rect1.left() - rect2.right()), # right
			"bottom": abs(rect1.top() - rect2.bottom()) # bottom
		}

		# Determine which is closest just by comparing
		closest = "top"
		for i in side.keys():
			if side[i] < side[closest]:
				closest = i
		return closest, rect2

	return None, None
