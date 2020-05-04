# coding: utf-8

from scene import *
import sound
import random

class Controller (Scene):
	def setup(self):
		self.background_color = '#004f82'

if __name__ == '__main__':
	run(Controller(), PORTRAIT, show_fps=True)
