import pygame
#castle class

class Button():
	def __init__(self, image, x, y, scale = 0.3):
		width = image.get_width() * scale
		height = image.get_height() * scale
		self.image = pygame.transform.scale(image, (width, height))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False
		self.update_time = pygame.time.get_ticks()
		self.twinkle = 0


	def draw(self, screen): 
		screen.blit(self.image, self.rect)

	def pressed(self): 
		# 按按鈕功能
		self.clicked = False
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		return action