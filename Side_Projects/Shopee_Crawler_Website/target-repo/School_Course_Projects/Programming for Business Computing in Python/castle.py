import pygame
#castle class

class Castle():
	def __init__(self, image, x, y, max_health = 5000, max_money = 2000):
		self.max_health = max_health
		self.health = self.max_health
		self.money = 1000
		self.max_money = max_money
		self.money_increase = 2.5
		self.image = pygame.transform.scale(image, (120,240))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.upgrade_cooldown = 0
		self.upgrade_cost = 100


	def draw(self, screen):
		#check which image to use based on health
		screen.blit(self.image, self.rect)