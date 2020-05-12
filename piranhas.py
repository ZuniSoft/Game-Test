# coding: utf-8
"""
Game that uses the Nimbus game controller.
"""

from scene import *
import sound
from random import uniform, choice
import math

A = Action

PLAYER_MAX_SPEED = 10
SWARM_SIZE = 30
SWARM_MAX_SPEED = 6

standing_texture = Texture('plf:AlienGreen_front')
swim_textures = [
	Texture('plf:AlienGreen_swim1'), Texture('plf:AlienGreen_swim2')
]
hit_texture = Texture('plf:AlienGreen_hit')


class Piranha(SpriteNode):
	def __init__(self, max_x, max_y, *args, **kwargs):
		img = choice(['plf:Enemy_FishGreen', 'plf:Enemy_FishPink'])
		SpriteNode.__init__(self, img, *args, **kwargs)
		self.scale = 0.6
		self.max_x = max_x
		self.max_y = max_y
		a = uniform(0, math.pi * 2)
		self.position = (uniform(0, max_x), uniform(0, max_y))
		self.v = Vector2(math.cos(a), math.sin(a))
		self.startled = False
		self.destroyed = False

	def update(self, neighbors):
		self.rule1(neighbors)
		self.rule2(neighbors)
		self.rule3(neighbors)
		self.rule4(neighbors)
		if abs(self.v) > SWARM_MAX_SPEED:
			self.v *= (SWARM_MAX_SPEED / abs(self.v))

	def rule1(self, neighbors):
		# Move to 'center of mass' of neighbors
		if not neighbors:
			return Vector2(0, 0)
		p = Point()
		for n in neighbors:
			p += n.position
		m = p / len(neighbors)
		if self.startled:
			self.v -= (m - self.position) * 0.007
		else:
			self.v += (m - self.position) * 0.001

	def rule2(self, neighbors):
		# Don't crowd neighbors
		if not neighbors:
			return Vector2(0, 0)
		c = Vector2()
		for n in neighbors:
			if abs(n.position - self.position) < 30:
				c += (self.position - n.position)
		self.v += c * 0.01

	def rule3(self, neighbors):
		# Match velocity of neighbors
		if not neighbors:
			return Vector2(0, 0)
		v = Vector2()
		for n in neighbors:
			v += n.v
		m = v / len(neighbors)
		self.v += m * 0.01

	def rule4(self, neighbors):
		# Stay within screen bounds
		v = Vector2()
		if self.position.x < 0:
			v.x = 1
		if self.position.x > self.max_x:
			v.x = -1
		if self.position.y < 0:
			v.y = 1
		if self.position.y > self.max_y:
			v.y = -1
		self.v += v * 0.3


class Piranhas(Scene):
	def setup(self):
		self.background_color = '#004f82'
		self.player = SpriteNode(standing_texture)
		self.player.anchor_point = (0, 0)
		self.add_child(self.player)
		score_font = ('Futura', 40)
		self.score_label = LabelNode('0', score_font, parent=self)
		self.score_label.position = (self.size.w / 2, self.size.h - 70)
		self.score_label.z_position = 1
		self.piranhas = [
			Piranha(self.size.w, self.size.h, parent=self) for i in range(SWARM_SIZE)
		]
		self.lasers = []
		self.new_game()

	def new_game(self):
		self.score = 0
		self.score_label.text = '0'
		self.stroke_step = -1
		self.player.position = (self.size.w / 2, 64)
		self.player.texture = standing_texture
		self.speed = 1.0
		self.game_over = False

	def did_change_size(self):
		for b in self.piranhas:
			b.max_x = self.size.w
			b.max_y = self.size.h

	def controller_changed(self, id, key, value):
		return

	def update(self):
		self.update_player()
		self.check_piranah_collisions()
		self.check_laser_collisions()
		for p in self.piranhas:
			neighbor_distance = min(self.size) / 3
			neighbors = [
				b for b in self.piranhas
				if b != p and abs(b.position - p.position) < neighbor_distance
			]
			p.update(neighbors)
		for p in self.piranhas:
			p.position += p.v
			p.rotation = math.atan2(*reversed(p.v)) + math.pi

	def update_player(self):
		if not self.view:
			return
		scrn_h = self.size.h
		scrn_w = self.size.w
		c = get_controllers()
		if c[0]['thumb_stick_right'] != Point(0.00, 0.00):
			x = self.player.position.x
			y = self.player.position.y
			# Flip the player sprite depending direction of travel
			if c[0]['thumb_stick_right'].x < 0:
				self.player.x_scale = -1.0
				self.player.anchor_point = (32, 0)
			else:
				self.player.x_scale = 1.0
				self.player.anchor_point = (-32, 0)
			max_speed = PLAYER_MAX_SPEED
			if x > scrn_w - self.player.size.w:
				x = scrn_w - self.player.size.w
				max_speed = 0.05
			x = max(0, min(scrn_w, x + c[0]['thumb_stick_right'].x * max_speed))
			max_speed = PLAYER_MAX_SPEED
			if y > scrn_h - self.player.size.h + 52:
				y = scrn_h - self.player.size.h + 52
				max_speed = 0.05
			y = max(0, min(scrn_h, y + c[0]['thumb_stick_right'].y * max_speed))
			self.player.position = x, y
			stroke = int(self.player.position.x / 40) % 2
			self.player.texture = swim_textures[stroke]
			self.swim_step = stroke
		elif c[0]['dpad'] != (0, 0):
			self.shoot_laser(c[0]['dpad'])

	def player_hit(self):
		self.game_over = True
		sound.play_effect('arcade:Explosion_1')
		self.player.texture = hit_texture
		self.player.run_action(
			A.move_by(0, -(self.size.h + self.player.position.y), 2)
		)
		self.run_action(A.sequence(A.wait(2 * self.speed), A.call(self.new_game)))

	def panic(self, pos):
		sound.play_effect('drums:Drums_06')
		for p in self.piranhas:
			p.startled = True
		s = SpriteNode('shp:wavering', position=pos, scale=0, parent=self)
		s.run_action(A.sequence(A.group(A.scale_to(2), A.fade_to(0)), A.remove()))
		self.run_action(A.sequence(A.wait(1), A.call(self.end_panic)))

	def end_panic(self):
		for p in self.piranhas:
			p.startled = False

	def destroy_piranha(self, piranha):
		self.score += 100
		self.score_label.text = str(self.score)
		sound.play_effect('arcade:Explosion_2', 0.2)
		piranha.destroyed = True

	def check_piranah_collisions(self):
		player_hitbox = Rect(
			self.player.position.x - 20, self.player.position.y, 40, 65
		)
		for p in list(self.piranhas):
			if p.frame.intersects(player_hitbox):
				if isinstance(p, Piranha):
					self.player_hit()

	def check_laser_collisions(self):
		for laser in list(self.lasers):
			if not laser.parent:
				self.lasers.remove(laser)
				continue
			for p in self.piranhas:
				if not isinstance(p, Piranha):
					continue
				if p.destroyed:
					p.remove_from_parent()
				if laser.position in p.frame:
					self.destroy_piranha(p)
					self.lasers.remove(laser)
					self.panic(laser.position)
					laser.remove_from_parent()
					break

	def shoot_laser(self, direction):
		if len(self.lasers) >= 3:
			return
		laser = SpriteNode('spc:LaserGreen12', parent=self)
		if direction.x > 0:
			laser.position = self.player.position + (60, 30)
			laser.rotation = 1.57
			actions = [A.move_by(self.size.w, 0, 1.2 * self.speed), A.remove()]
		elif direction.x < 0:
			laser.position = self.player.position + (0, 30)
			laser.rotation = 4.71239
			actions = [A.move_by(-self.size.w, 0, 1.2 * self.speed), A.remove()]
		elif direction.y > 0:
			laser.position = self.player.position + (30, 60)
			laser.rotation = 6.28319
			actions = [A.move_by(0, self.size.h, 1.2 * self.speed), A.remove()]
		elif direction.y < 0:
			laser.position = self.player.position + (30, 0)
			laser.rotation = 3.14159
			actions = [A.move_by(0, -self.size.h, 1.2 * self.speed), A.remove()]
		if direction.x != 0 or direction.y != 0:
			laser.z_position = -1
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)
			sound.play_effect('digital:Laser4')


if __name__ == '__main__':
	run(Piranhas(), LANDSCAPE, show_fps=True)

