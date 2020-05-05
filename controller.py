# coding: utf-8

"""
Quick test to retrieve telemetry data from a Nimbus Steel Series controller.
"""

from scene import *

class ControllerTest (Scene):
	def setup(self):
		self.background_color = '#004f82'
		
	def controller_changed(self, id, key, value):
		print("ID: " + str(id))
		print("Key: " + key)
		print("Value: " + str(value))
		
		c = get_controllers()
		print("Controllers: " + str(c))

if __name__ == '__main__':
	run(ControllerTest(), PORTRAIT, show_fps=True) 
