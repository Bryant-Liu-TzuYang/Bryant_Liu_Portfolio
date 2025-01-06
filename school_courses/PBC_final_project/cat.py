import pygame
import random

'''
每隻貓咪和敵兵有自己的屬性，
包含生產間隔時間、生產價格、血量、攻擊力、防禦力(扣多少血會被擊退)、攻擊距離、跑動速度、範圍攻擊、漂浮.....。
'''

class Cat(pygame.sprite.Sprite):
	def __init__(self, image, health = 200, atk = 30, x = 1120, y = random.randrange(380,420), speed = 3, \
		attack_distance = 10, attack_delay = 35, scale = 0.5, max_recoil=15, \
		surrender=2, group_attack=False, floating=False):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.speed = speed
		self.atk = atk
		self.attack_distance = attack_distance
		self.attack_delay = attack_delay
		self.delay_time_count = self.attack_delay  # 如果數到0就撞一下
		self.health = health
		self.defence = health / surrender
		self.surrender_judging_point = health
		self.surrender = False
		self.count_surrendering = 0
		
		self.action = 0  #0: walk, 1: attack, 2: death

		# 圖片處理
		self.image = pygame.image.load(image).convert_alpha()
		width = self.image.get_width() * scale
		height = self.image.get_height() * scale
		self.image = pygame.transform.scale(self.image,(width, height))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.charging = False
		self.max_recoil = max_recoil
		self.recoil = 0
		self.vibrate_flag = 0  # 0, 1, 2, 3
		self.group_attack = group_attack  # 否
		self.isfloating = floating
		self.speed_control = None
		self.direction_flag = 0  # 0往上1往下
		self.direction_change_delay_time = 0  # 60
		self.update_time = pygame.time.get_ticks()


	def update(self, surface, castle, enemy_group, our_group, dead_group):
		if self.alive:
			if self.rect.left <= castle.rect.right + self.attack_distance:  # 碰到城堡
				self.update_action(1)
			elif any(self.rect.left <= enemy.rect.right + self.attack_distance \
				for enemy in enemy_group):  # 碰到敵人
				self.update_action(1)
			elif self.action != 2 and self.charging == False:
				self.update_action(0)

			# 被擊退
			if self.surrender_judging_point - self.health >= self.defence:
				self.surrender_judging_point = self.health
				self.surrender = True
				self.count_surrendering = 20
				self.rect.y -= 100
			if self.surrender == True:
				if self.count_surrendering >= 0: self.count_surrendering -= 1
				if self.count_surrendering < 0:
					self.surrender = False
					self.delay_time_count = self.attack_delay
					self.charging = False
					self.update_action(0)
				else:
					self.rect.x += 10
					self.rect.y += 5

			# 死掉了
			if self.health <= 0:
				self.update_action(2)
				self.alive = False
				our_group.remove(self)
				dead_group.add(self)

		self.move(castle, enemy_group)

		#draw image on screen
		self.display_animation(surface)

	def display_animation(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

	def wait_to_attack_animation(self):
		if self.recoil < self.max_recoil:
			self.recoil += 1
			self.rect.x += 1
		else:
			self.vibrate()

	def attack_animation(self):
		for i in range(min(self.max_recoil, self.attack_delay)):  # 發動攻擊
			self.rect.x -= 1
		self.recoil = 0

	def vibrate(self):
		if self.vibrate_flag == 0:
			self.rect.centerx += 0
			self.rect.centery += 1
		if self.vibrate_flag == 1:
			self.rect.centerx += 1
			self.rect.centery -= 1
		if self.vibrate_flag == 2:
			self.rect.centerx -= 0
			self.rect.centery += 1
		if self.vibrate_flag == 3:
			self.rect.centerx -= 1
			self.rect.centery -= 1
		if self.vibrate_flag >= 3:
			self.vibrate_flag = 0
		else:
			self.vibrate_flag += 1

	def single_attack_damage(self, castle, enemy_group):
		smallest_dist = 5000
		for enemy in enemy_group:
			if (self.rect.left - enemy.rect.right) < smallest_dist:
				smallest_dist = (self.rect.left - enemy.rect.right)

		if (self.rect.left - castle.rect.right) <= smallest_dist \
			and (self.rect.left - castle.rect.right) <= self.attack_distance:
			castle.health -= self.atk
		else:
			for enemy in enemy_group:
				if (self.rect.left - enemy.rect.right) <= smallest_dist:
					enemy.health -= self.atk
					break  # 單體攻擊

	def group_attack_damage(self, castle, enemy_group):
		if (self.rect.left - castle.rect.right) <= self.attack_distance:
			castle.health -= self.atk
		for enemy in enemy_group:
			if (self.rect.left - enemy.rect.right) <= self.attack_distance:
				enemy.health -= self.atk  # 全體攻擊

	def get_back(self):
		pass

	def floating(self):
		self.direction_change_delay_time += 1
		if pygame.time.get_ticks() - self.update_time >= 100:
			if self.direction_flag == 0:
				self.rect.y -= 1
			elif self.direction_flag == 1:
				self.rect.y += 1
			self.update_time = pygame.time.get_ticks()
		if self.direction_change_delay_time >= 60:
			self.direction_change_delay_time = 0
			if self.direction_flag == 0: 
				self.direction_flag = 1
			else:
				self.direction_flag = 0

	def go_forward(self):
		if self.speed < 1:  # 當跑速小於1時
			if self.speed_control >= (1 // self.speed):
				self.rect.x -= 1
				self.speed_control = 0
			else:
				self.speed_control +=1
		else:
			self.rect.x -= self.speed

	def move(self, castle, enemy_group):
		self.get_back()
		if self.isfloating: self.floating()  # 控制漂浮
		if self.action == 0:
			self.go_forward()  # 用以控制前進

		# attack
		if self.action == 1:
			if self.delay_time_count > 0:
				self.charging = True
				self.wait_to_attack_animation()
				self.delay_time_count -= 1  # 集氣

			else:
				self.charging = False
				self.attack_animation()

				if self.group_attack == False: self.single_attack_damage(castle, enemy_group)  #單體攻擊
				if self.group_attack == True: self.group_attack_damage(castle, enemy_group)  #全體攻擊
				self.delay_time_count = self.attack_delay

		if self.action == 2:
			self.rect.y -= 20

	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
	

class Baby_cat(Cat):
	# static variables
	price = 50
	cooldown = 45
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/baby_cat.png", health=100, atk=25, \
		x=1120, y=random.randrange(410,420), speed=2, surrender=3, \
		attack_distance=0, attack_delay=25, scale=0.65)

class Tall_cat(Cat):
	price = 100
	cooldown = 70
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/tall_cat.png", health=400, atk=20, \
		x=1120, y=random.randrange(340,360), speed=1, surrender=1, \
		attack_distance=-40, attack_delay=60, scale=1, max_recoil=0,group_attack=True)

class Axe_cat(Cat):
	# static variables
	price = 200
	cooldown = 60
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/axe_cat.png", health=300, atk=60, \
		x=1120, y=random.randrange(410,420), speed=3, surrender=3, \
		attack_distance=0, attack_delay=22, scale=0.65)


class Gross_cat(Cat):
	# static variables
	price = 400
	cooldown = 120
	cooldown_count = 0
	clean_image = pygame.image.load("img/gross_cat.png")

	def __init__(self):
		super().__init__(image="img/gross_cat.png", health=150, atk=120, \
		x=1120, y=random.randrange(260,280), speed=1, surrender=10, \
		attack_distance=100, attack_delay=50, scale=0.9)
		self.angle = 0
		self.get_back_second_conut = 8
		self.should_get_back = False

	def wait_to_attack_animation(self):
		self.vibrate()

	def attack_animation(self):
		self.angle = 75
		self.image = pygame.transform.rotozoom(Gross_cat.clean_image, self.angle, 0.9)
		self.get_back_second_conut = 8
		self.should_get_back = True

	def get_back(self):
		if self.get_back_second_conut >= 0: self.get_back_second_conut -= 1
		if self.get_back_second_conut <= 0 and self.should_get_back == True:
			self.image = pygame.transform.rotozoom(Gross_cat.clean_image, 0, 0.9)
			self.should_get_back = False

	def display_animation(self, surface):
		if self.should_get_back == False: surface.blit(self.image, (self.rect.x, self.rect.y))
		if self.should_get_back == True: surface.blit(self.image, (self.rect.x-160, self.rect.y+80))

class Cow_cat(Cat):
	# static variables
	price = 500
	cooldown = 100
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/cow_cat.png", health=500, atk=25, \
		x=1120, y=random.randrange(350,360), speed=15, surrender=5, \
		attack_distance=-30, attack_delay=8, scale=1.2)

class Bird_cat(Cat):
	# static variables
	price = 650
	cooldown = 100
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/bird_cat.png", health=310, atk=85, \
		x=1120, y=random.randrange(260,280), speed=1, surrender=4, \
		attack_distance=100, attack_delay=40, scale=0.3, group_attack=True, floating=True)
		self.change_animation_count = 220
		self.animation_flag = 1  #1, 2 2拍翅
		self.animation_update_time = pygame.time.get_ticks()
		self.angle = 0
		self.get_back_second_conut = 8
		self.should_get_back = False
		self.image2 = pygame.image.load("img/bird_cat_2.png").convert_alpha()
		width = self.image2.get_width() * 0.3
		height = self.image2.get_height() * 0.3
		self.image2 = pygame.transform.scale(self.image2,(width, height))
		Bird_cat.clean_image = self.image2

	def go_forward(self):
		self.rect.x -= self.speed


	def attack_animation(self):
		for i in range(min(self.max_recoil, self.attack_delay)):  # 發動攻擊
			self.rect.x -= 1
		self.recoil = 0
		self.angle = 30
		self.image2 = pygame.transform.rotozoom(Bird_cat.clean_image, self.angle, 1)
		self.get_back_second_conut = 6
		self.should_get_back = True

	def get_back(self):
		if self.get_back_second_conut >= 0: self.get_back_second_conut -= 1
		if self.get_back_second_conut <= 0 and self.should_get_back == True:
			self.image2 = pygame.transform.rotozoom(Bird_cat.clean_image, 0, 1)
			self.should_get_back = False

	def display_animation(self, surface):
		if pygame.time.get_ticks() - self.animation_update_time >= self.change_animation_count:
			if self.animation_flag == 1:
				self.animation_flag = 2
			elif self.animation_flag == 2:
				self.animation_flag = 1
			self.animation_update_time = pygame.time.get_ticks()

		if self.should_get_back == False:
			if self.animation_flag == 1: surface.blit(self.image, (self.rect.x, self.rect.y))
			if self.animation_flag == 2: surface.blit(self.image2, (self.rect.x, self.rect.y))
		if self.should_get_back == True: surface.blit(self.image2, (self.rect.x-40, self.rect.y-40))

class Sniper_cat(Cat):
	# static variables
	price = 650
	cooldown = 800
	cooldown_count = 0

	def __init__(self):
		super().__init__(image="img/sniper_cat.png", health=100, atk=75, \
		x=1120, y=random.randrange(260,280), speed=1, surrender=1, \
		attack_distance=600, attack_delay=300, scale=0.3, group_attack=False, floating=True)
		self.change_animation_count = 220
		self.animation_flag = 1
		self.animation_update_time = pygame.time.get_ticks()
		self.angle = 0
		self.get_back_second_conut = 8
		self.should_get_back = False
		self.image2 = pygame.image.load("img/sniper_cat.png").convert_alpha()
		width = self.image2.get_width() * 0.3
		height = self.image2.get_height() * 0.3
		self.image2 = pygame.transform.scale(self.image2,(width, height))
		Sniper_cat.clean_image = self.image2

	def go_forward(self):
		self.rect.x -= self.speed


	def attack_animation(self):
		for i in range(min(self.max_recoil, self.attack_delay)):  # 發動攻擊
			self.rect.x -= 1
		self.recoil = 0
		self.angle = 30
		self.image2 = pygame.transform.rotozoom(Sniper_cat.clean_image, self.angle, 1)
		self.get_back_second_conut = 6
		self.should_get_back = True

	def get_back(self):
		if self.get_back_second_conut >= 0: self.get_back_second_conut -= 1
		if self.get_back_second_conut <= 0 and self.should_get_back == True:
			self.image2 = pygame.transform.rotozoom(Sniper_cat.clean_image, 0, 1)
			self.should_get_back = False

	def display_animation(self, surface):
		if pygame.time.get_ticks() - self.animation_update_time >= self.change_animation_count:
			if self.animation_flag == 1:
				self.animation_flag = 2
			elif self.animation_flag == 2:
				self.animation_flag = 1
			self.animation_update_time = pygame.time.get_ticks()

		if self.should_get_back == False:
			if self.animation_flag == 1: surface.blit(self.image, (self.rect.x, self.rect.y))
			if self.animation_flag == 2: surface.blit(self.image2, (self.rect.x, self.rect.y))
		if self.should_get_back == True: surface.blit(self.image2, (self.rect.x-40, self.rect.y-40))


class Lizard_cat(Cat):
	# static variables
	price = 1000
	cooldown = 120
	cooldown_count = 0
	clean_image = pygame.image.load("img/lizard_cat.png")

	def __init__(self):
		super().__init__(image="img/lizard_cat.png", health=400, atk=250, \
		x=1120, y=random.randrange(360,380), speed=1, surrender=3, \
		attack_distance=220, attack_delay=50, scale=0.35)
		self.change_animation_count = 350
		self.animation_flag = 1  #1, 2
		self.angle = 0
		self.get_back_second_conut = 8
		self.should_get_back = False
		self.image2 = pygame.image.load("img/lizard_cat_2.png").convert_alpha()
		width = self.image2.get_width() * 0.35
		height = self.image2.get_height() * 0.35
		self.image2 = pygame.transform.scale(self.image2,(width, height))

	def go_forward(self):
		self.rect.x -= self.speed

		if pygame.time.get_ticks() - self.update_time >= self.change_animation_count:
			if self.animation_flag == 1:
				self.animation_flag = 2
			elif self.animation_flag == 2:
				self.animation_flag = 1
			self.update_time = pygame.time.get_ticks()

	def wait_to_attack_animation(self):
		self.vibrate()

	def attack_animation(self):
		self.angle = 15
		self.image = pygame.transform.rotozoom(Lizard_cat.clean_image, self.angle, 0.35)
		self.get_back_second_conut = 6
		self.should_get_back = True

	def get_back(self):
		if self.get_back_second_conut >= 0: self.get_back_second_conut -= 1
		if self.get_back_second_conut <= 0 and self.should_get_back == True:
			self.image = pygame.transform.rotozoom(Lizard_cat.clean_image, 0, 0.35)
			self.should_get_back = False

	def display_animation(self, surface):
		if self.should_get_back == False:
			if self.animation_flag == 1: surface.blit(self.image, (self.rect.x, self.rect.y))
			if self.animation_flag == 2: surface.blit(self.image2, (self.rect.x, self.rect.y))
		if self.should_get_back == True: surface.blit(self.image, (self.rect.x-40, self.rect.y-40))



























'''敵人'''
class Enemy(pygame.sprite.Sprite):
	def __init__(self, image, health = 500, atk = 400, x=80, y=random.randrange(380,420), speed = 10, surrender=2, \
		attack_distance=-50, attack_delay = 30, scale = 0.6, max_recoil=8, group_attack=False, floating=False):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.speed = speed
		self.atk = atk
		self.attack_distance = attack_distance
		self.attack_delay = attack_delay
		self.delay_time_count = self.attack_delay  # 如果數到0就撞一下
		self.health = health
		self.defence = health / surrender
		self.surrender_judging_point = health
		self.surrender = False
		self.count_surrendering = 0
		self.action = 0  #0: walk, 1: attack, 2: death

		# 圖片處理
		self.image = pygame.image.load(image).convert_alpha()
		width = self.image.get_width() * scale
		height = self.image.get_height() * scale
		self.image = pygame.transform.scale(self.image,(width, height))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.charging = False
		self.max_recoil = max_recoil
		self.recoil = 0
		self.vibrate_flag = 0  # 0, 1, 2, 3
		self.group_attack = group_attack  # 否
		self.isfloating = floating
		self.speed_control = None
		self.direction_flag = 0  # 0往上1往下
		self.direction_change_delay_time = 0  # 60
		self.update_time = pygame.time.get_ticks()


			
	def update(self, surface, castle, enemy_group, our_group, dead_group):
		if self.alive:
			# 如果碰到貓
			if self.rect.right + self.attack_distance >= castle.rect.left:  # 碰到城堡
				self.update_action(1)
			elif any(self.rect.right + self.attack_distance >= enemy.rect.left \
				for enemy in enemy_group):  # 碰到貓
				self.update_action(1)
			elif self.action != 2 and self.charging == False:
				self.update_action(0)

			# 被擊退
			if self.surrender_judging_point - self.health >= self.defence:
				self.surrender_judging_point = self.health
				self.surrender = True
				self.count_surrendering = 20
				self.rect.y -= 100

			if self.surrender == True:
				if self.count_surrendering >= 0: self.count_surrendering -= 1
				if self.count_surrendering < 0:
					self.surrender = False
					self.delay_time_count = self.attack_delay
					self.charging = False
					self.update_action(0)
				else:
					self.rect.x -= 10
					self.rect.y += 5


			# 死掉了
			if self.health <= 0:
				self.update_action(2)
				self.alive = False
				our_group.remove(self)
				dead_group.add(self)
				if castle.money < castle.max_money:
					castle.money += self.reward_money

		self.move(castle, enemy_group)

		#draw image on screen
		self.display_animation(surface)

	def display_animation(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

	def wait_to_attack_animation(self):
		if self.recoil < self.max_recoil:
			self.recoil += 1
			self.rect.x -= 1
		else:
			self.vibrate()

	def attack_animation(self):
		for i in range(min(self.max_recoil, self.attack_delay)):  # 發動攻擊
			self.rect.x += 1
		self.recoil = 0

	def vibrate(self):
		if self.vibrate_flag == 0:
			self.rect.centerx += 0
			self.rect.centery += 1
		if self.vibrate_flag == 1:
			self.rect.centerx += 1
			self.rect.centery -= 1
		if self.vibrate_flag == 2:
			self.rect.centerx -= 0
			self.rect.centery += 1
		if self.vibrate_flag == 3:
			self.rect.centerx -= 1
			self.rect.centery -= 1

		if self.vibrate_flag >= 3:
			self.vibrate_flag = 0
		else:
			self.vibrate_flag += 1

	def single_attack_damage(self, castle, enemy_group):
		smallest_dist = 5000
		for enemy in enemy_group:
			if (enemy.rect.left - self.rect.right) < smallest_dist:
				smallest_dist = (enemy.rect.left - self.rect.right)

		if (castle.rect.left - self.rect.right) <= smallest_dist \
			and (castle.rect.left - self.rect.right) <= self.attack_distance:
			castle.health -= self.atk
		else:
			for enemy in enemy_group:
				if (enemy.rect.left - self.rect.right) <= smallest_dist:
					enemy.health -= self.atk
					break  # 單體攻擊

	def group_attack_damage(self, castle, enemy_group):
		if (castle.rect.left - self.rect.right) <= self.attack_distance:
			castle.health -= self.atk
		for enemy in enemy_group:
			if (enemy.rect.left - self.rect.right) <= self.attack_distance:
				enemy.health -= self.atk  # 全體攻擊

	def get_back(self):
		pass

	def floating(self):
		self.direction_change_delay_time += 1
		if pygame.time.get_ticks() - self.update_time >= 100:
			if self.direction_flag == 0:
				self.rect.y -= 1
			elif self.direction_flag == 1:
				self.rect.y += 1
			self.update_time = pygame.time.get_ticks()
		if self.direction_change_delay_time >= 60:
			self.direction_change_delay_time = 0
			if self.direction_flag == 0: 
				self.direction_flag = 1
			else:
				self.direction_flag = 0

	def go_forward(self):
		if self.speed < 1:  # 當跑速小於1時
			if self.speed_control >= (1 // self.speed):
				self.rect.x += 1
				self.speed_control = 0
			else:
				self.speed_control +=1
		else:
			self.rect.x += self.speed

	def move(self, castle, enemy_group):
		self.get_back()  # 攻擊後圖片切換
		if self.isfloating: self.floating()  # 控制漂浮

		if self.action == 0:
			self.go_forward()  # 用以控制前進

		# attack
		if self.action == 1:
			if self.delay_time_count > 0:
				self.charging = True
				self.wait_to_attack_animation()
				self.delay_time_count -= 1  # 集氣

			else:
				self.charging = False
				self.attack_animation()
				if self.group_attack == False: self.single_attack_damage(castle, enemy_group)  #單體攻擊
				if self.group_attack == True: self.group_attack_damage(castle, enemy_group)  #全體攻擊
				self.delay_time_count = self.attack_delay

		if self.action == 2:
			self.rect.y -= 20


	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action


class Police_dog(Enemy):
	reward_money = 50
	def __init__(self):
		super().__init__(image="img/police_dog.png", health = 300, atk = 400, \
			x=170, y=random.randrange(380,420), speed = 8, \
			attack_distance=0, attack_delay = 90, scale = 0.6)

class Wild_dog(Enemy):
	reward_money = 30
	def __init__(self):
		super().__init__(image="img/wild_dog.png", health = 100, atk = 30, surrender=1,\
			x=170, y=random.randrange(380,420), speed = 4, \
			attack_distance=-20, attack_delay = 20, scale = 1)

class Doggy(Enemy):
	reward_money = 25
	def __init__(self):
		super().__init__(image="img/doggy.png", health = 100, atk = 20, \
			x=170, y=random.randrange(380,420), speed = 2, \
			attack_distance=0, attack_delay = 30, scale = 1)

class Enemy_cat_god(Enemy):
	reward_money = 2000
	def __init__(self, enemy_group, animations):
		super().__init__(image="img/enemy_catgod.png", health = 2000, atk = 500, surrender=1,\
			x=-100, y=random.randrange(30,50), speed = 0.05, \
			attack_distance = 200, attack_delay = 600, scale = 1, group_attack=True, floating=True)
		self.max_recoil = 40
		self.recoil = 0
		self.speed_control = (1 // self.speed)
		self.explode_image = pygame.image.load("img/explode.png").convert_alpha()
		width = self.explode_image.get_width() * 0.65
		height = self.explode_image.get_height() * 0.65
		self.explode_image = pygame.transform.scale(self.explode_image,(width, height))
		self.animation_second_conut = 0

		#震飛
		for enemy in enemy_group:
			if (enemy.rect.left - self.rect.right) <= self.attack_distance+100:
				enemy.rect.x += 400
		

	def floating(self):
		self.direction_change_delay_time += 1
		if pygame.time.get_ticks() - self.update_time >= 8:
			if self.direction_flag == 0:
				self.rect.y -= 1
			elif self.direction_flag == 1:
				self.rect.y += 1
			self.update_time = pygame.time.get_ticks()
		if self.direction_change_delay_time >= 60:
			self.direction_change_delay_time = 0
			if self.direction_flag == 0: 
				self.direction_flag = 1
			else:
				self.direction_flag = 0

	def attack_animation(self):
		for i in range(min(self.max_recoil, self.attack_delay)):  # 發動攻擊
			self.rect.x += 1
		self.recoil = 0
		self.animation_second_conut = 60

	def display_animation(self, surface):
		self.animation_second_conut -= 1
		if self.animation_second_conut >= 0:
			self.explode_image.set_alpha(255-4*(60-self.animation_second_conut))
			surface.blit(self.explode_image, (self.rect.x+30, self.rect.y+80+self.animation_second_conut/3))
		surface.blit(self.image, (self.rect.x, self.rect.y))




class The_face(Enemy):
	reward_money = 1000
	def __init__(self, enemy_group, animations):
		super().__init__(image="img/the_face.png", health = 1000, atk = 350, surrender=1,\
			x=-60, y=random.randrange(230,250), speed = 0.5, \
			attack_distance = 50, attack_delay = 90, scale = 0.5, group_attack=True, floating=True)
		self.max_recoil = 20
		self.recoil = 0
		self.speed_control = (1 // self.speed)
		self.angry_image = pygame.image.load("img/the_face_angry.png").convert_alpha()
		width = self.angry_image.get_width() * 0.65
		height = self.angry_image.get_height() * 0.65
		self.angry_image = pygame.transform.scale(self.angry_image,(width, height))

		# 震飛
		for enemy in enemy_group:
			if (enemy.rect.left - self.rect.right) <= self.attack_distance+50:
				enemy.rect.x += 150

	def floating(self):
		self.direction_change_delay_time += 1
		if pygame.time.get_ticks() - self.update_time >= 100:
			if self.direction_flag == 0:
				self.rect.y -= 1
			elif self.direction_flag == 1:
				self.rect.y += 1
			self.update_time = pygame.time.get_ticks()
		if self.direction_change_delay_time >= 60:
			self.direction_change_delay_time = 0
			if self.direction_flag == 0: 
				self.direction_flag = 1
			else:
				self.direction_flag = 0

	def display_animation(self, surface):
		if self.charging == True and self.delay_time_count <= 30:
			surface.blit(self.angry_image, (self.rect.x, self.rect.y-20))
		else:
			surface.blit(self.image, (self.rect.x, self.rect.y))
			