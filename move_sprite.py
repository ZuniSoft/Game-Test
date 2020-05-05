# coding: utf-8

"""
Quick test to move a sprite using a Nimbus Steel Series controller.
"""

from scene import *
import math

MAX_SPEED = 10

player_texture = Texture('plf:AlienGreen_front')

class MoveSprite (Scene):
	def setup(self):
		self.background_color = '#004f82'
		
		self.player = SpriteNode(player_texture)
		self.player.anchor_point = (0, 0)
		self.add_child(self.player)
		
	def controller_changed(self, id, key, value):
		scrn_h = self.size.h
		scrn_w = self.size.w
		
		if key == "thumbstick_right":
			x = self.player.position.x
			y = self.player.position.y
			
			max_speed = MAX_SPEED
			
			if x > scrn_w - self.player.size.w:
				x = scrn_w - self.player.size.w
				max_speed = 0.05
				
			x = max(0, min(scrn_w, x + value.x * max_speed))
			
			max_speed = MAX_SPEED
				
			if y > scrn_h - self.player.size.h + 52:
				y = scrn_h - self.player.size.h + 52
				max_speed = 0.05
			
			y = max(0, min(scrn_h, y + value.y * max_speed))
			
			self.player.position = x, y

if __name__ == '__main__':
	run(MoveSprite(), LANDSCAPE, show_fps=True) 
