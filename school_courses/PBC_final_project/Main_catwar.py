#coding = utf-8
import pygame
from cat import *
from castle import Castle 
from button import Button
import time
import random

#function for outputting text onto the screen
def draw_text(text, font, text_colour, x, y):
	img = font.render(text, True, text_colour)
	screen.blit(img, (x, y))
	
#function for displaying status
def show_castle_info(castle, screen_width, screen_height):
	draw_text( "HP: " + str(castle.health) + " / " + str(castle.max_health),\
		font, WHITE, castle.rect.x - 20, castle.rect.y - 30)

def summon_cat_and_display_cooldown_bar(cat, button, surface):  # 寫成function 這樣之後不同按鍵放不同貓也能用
	if cat.cooldown_count > 0: cat.cooldown_count -= 1
	if pygame.time.get_ticks() >= button.update_time + 350:
		if button.twinkle == 1: button.twinkle = 0
		elif button.twinkle == 0: button.twinkle = 1
		button.update_time = pygame.time.get_ticks()
	if len(our_sprites) <= 30:
		if button.pressed() == True and cat.cooldown_count <= 0 \
			and castle1.money >= cat.price: # 按鈕被按下
			castle1.money -= cat.price
			cat.cooldown_count = cat.cooldown
			our_sprites.add(cat())

	# 底條
	pygame.draw.rect(surface, WHITE, (button.rect.left+3, button.rect.bottom+6, 114, 8))
	if cat.cooldown_count > 0:
		pygame.draw.rect(surface, BLUE, (button.rect.left+5, button.rect.bottom+8, 110 * (1 - cat.cooldown_count/cat.cooldown), 4))
	elif cat.cooldown_count <= 0:
		if button.twinkle == 1:
			pygame.draw.rect(surface, pygame.Color('yellow'), (button.rect.left+5, button.rect.bottom+8, 110, 4))

# 召喚貓咪
def summon_all_cats_and_display_cooldown_bar(surface):
	summon_cat_and_display_cooldown_bar(Baby_cat, button1, surface)
	summon_cat_and_display_cooldown_bar(Tall_cat, button2, surface)
	summon_cat_and_display_cooldown_bar(Axe_cat, button3, surface)
	summon_cat_and_display_cooldown_bar(Gross_cat, button4, surface)
	summon_cat_and_display_cooldown_bar(Cow_cat, button5, surface)
	summon_cat_and_display_cooldown_bar(Bird_cat, button6, surface)
	summon_cat_and_display_cooldown_bar(Sniper_cat, button7, surface)
	summon_cat_and_display_cooldown_bar(Lizard_cat, button8, surface)

# 召喚敵人
def summon_enemies():
	event_list = (0,1,2,3,4,5,6,7,8,9,10)  # 十種敵人，0代表不動作
	random.seed(time.time())
	event = random.choices(event_list, weights=(95000,1500,700,600,500,400,400,300,270,40,20), k=1)[0]
	if (event == 0): pass
	if (event == 1): enemy_sprites.add(Doggy())
	if (event == 3): enemy_sprites.add(Wild_dog())
	if (event == 6): enemy_sprites.add(Police_dog())
	if (event == 9): enemy_sprites.add(The_face(our_sprites, animations))
	if (event == 10): enemy_sprites.add(Enemy_cat_god(our_sprites, animations))

# 升級錢包
def upgrade_wallet(castle1):
	if castle1.upgrade_cooldown > 0: castle1.upgrade_cooldown -= 1
	if upgrade_button.pressed() == True and castle1.upgrade_cooldown <= 0 \
		and castle1.money >= castle1.upgrade_cost: # 按鈕被按下
		castle1.money -= castle1.upgrade_cost
		castle1.upgrade_cost += 50
		castle1.upgrade_cooldown = 20
		castle1.max_money += 200
		castle1.money_increase += 0.3

# 遊戲進行中迴圈
def run():
	game_over = False
	running = True

	while running:
		clock.tick(FPS) 
		if game_over == False:
			# 顯示背景
			screen.blit(bg_image,(0,0))

			# 顯示城堡
			castle1.draw(screen)
			castle2.draw(screen)

			# 顯示資訊面板
			show_castle_info(castle1, screen_width, screen_height)
			draw_text( str(castle2.health) + " / " + str(castle2.max_health),\
				font, WHITE, castle2.rect.x-10, castle2.rect.y - 30)
			draw_text( 'x ' + str(int(castle1.money)) + ' / ' + str(int(castle1.max_money)), \
				font_45, WHITE, 220, 45)  # 錢錢

			screen.blit(money_image, (160, 30))

			# 遊戲結束
			if castle1.health <= 0:
				show_castle_info(castle1, screen_width, screen_height)
				draw_text( str(castle2.health) + " / " + str(castle2.max_health),\
					font, WHITE, castle2.rect.x-10, castle2.rect.y - 30)
				draw_text( 'x ' + str(int(castle1.money)) + ' / ' + str(int(castle1.max_money)), \
					font_45, WHITE, 220, 45)  # 錢錢
				game_over = True
				lose_img = font_200.render('GAME OVER!', True, WHITE)
				lose_img_base = font_200.render('GAME OVER!', True, BLACK)
				for i in range(236, 245):
					screen.blit(lose_img_base, (203, i))
					screen.blit(lose_img_base, (197, i))
				screen.blit(lose_img, (200, 240))

			if castle2.health <= 0:
				show_castle_info(castle1, screen_width, screen_height)
				draw_text( str(castle2.health) + " / " + str(castle2.max_health),\
					font, WHITE, castle2.rect.x-10, castle2.rect.y - 30)
				draw_text( 'x ' + str(int(castle1.money)) + ' / ' + str(int(castle1.max_money)), \
					font_45, WHITE, 220, 45)  # 錢錢
				game_over = True
				win_img = font_200.render("Win!", True, WHITE)
				win_img_base = font_200.render("Win!", True, BLACK)
				for i in range(231, 240):
					screen.blit(win_img_base, (478, i))
					screen.blit(win_img_base, (472, i))
				screen.blit(win_img, (475, 235))

			# 判斷貓咪召喚+顯示冷卻條
			summon_all_cats_and_display_cooldown_bar(screen)
			# 召喚狗狗
			summon_enemies()
			# 錢包升級
			upgrade_wallet(castle1)

			# 顯示貓咪
			our_sprites.update(screen, castle2, enemy_sprites, our_sprites, dead_sprites)
			# 顯示敵人
			enemy_sprites.update(screen, castle1, our_sprites, enemy_sprites, dead_sprites)
			dead_sprites.update(screen, castle1, our_sprites, enemy_sprites, dead_sprites)

			# 顯示貓咪的按鈕
			upgrade_button.draw(screen)
			button1.draw(screen)
			button2.draw(screen)
			button3.draw(screen)
			button4.draw(screen)
			button5.draw(screen)
			button6.draw(screen)
			button7.draw(screen)
			button8.draw(screen)
			button9.draw(screen)
			button10.draw(screen)

			# 加錢
			if castle1.money < castle1.max_money: castle1.money += castle1.money_increase

		# 取得輸入
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:
				running = False
		pygame.display.update()

	pygame.quit()





'''程式從這裡開始一行一行跑'''
# pygame初始化
pygame.init() 

# 基本資訊設定
FPS = 30
screen_width = 1280
screen_height = 680

# 視窗
screen = pygame.display.set_mode((screen_width,screen_height)) 
pygame.display.set_caption("貓咪大戰爭")
clock = pygame.time.Clock()

# 讀圖片(順序要在視窗建立之後)
castle1_image = pygame.image.load("img/castle1.jpg").convert_alpha()
castle2_image = pygame.image.load("img/castle2.jpg").convert_alpha()
bg_image = pygame.image.load("img/grassland.png").convert_alpha()
babycat_button_image = pygame.image.load("img/baby_cat_button.png").convert_alpha()
tall_cat_button_image = pygame.image.load("img/tall_cat_button.png").convert_alpha()
axe_cat_button_image = pygame.image.load("img/axe_cat_button.png").convert_alpha()
gross_cat_button_image = pygame.image.load("img/gross_cat_button.png").convert_alpha()
cow_cat_button_image = pygame.image.load("img/cow_cat_button.png").convert_alpha()
bird_cat_button_image = pygame.image.load("img/bird_cat_button.png").convert_alpha()
sniper_cat_button_image = pygame.image.load("img/sniper_cat_button.png").convert_alpha()
lizard_cat_button_image = pygame.image.load("img/lizard_cat_button.png").convert_alpha()

greybutton_image = pygame.image.load("img/greybutton.png").convert_alpha()
upgrade_image = pygame.image.load("img/upgrade.png").convert_alpha()
money_image = pygame.image.load("img/money2.png").convert_alpha()
money_image = pygame.transform.scale(money_image, (money_image.get_width(), money_image.get_height()))


# 顏色
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
ORANGE = (255, 97, 0)
BLUE = (170,220,255)


# font
font = pygame.font.SysFont('Lazord Sans Serif', 30, bold=False)
font_45 = pygame.font.SysFont('Lazord Sans Serif', 45, bold=False)
font_47 = pygame.font.SysFont('Lazord Sans Serif', 47, bold=False)
font_200 = pygame.font.SysFont('Lazord Sans Serif', 200, bold=False)
font_210 = pygame.font.SysFont('Lazord Sans Serif', 210, bold=False)

# 建立城堡
castle1 = Castle(castle1_image, 1100, 180, max_health = 5000)
castle2 = Castle(castle2_image, 50, 180, max_health = 10000)

# 建立下方按鈕
upgrade_button = Button(upgrade_image, 20, 15, scale=0.25)
button1 = Button(babycat_button_image, 40, 540)
button2 = Button(tall_cat_button_image, 160, 540)
button3 = Button(axe_cat_button_image, 280, 540)
button4 = Button(gross_cat_button_image, 400, 540)
button5 = Button(cow_cat_button_image, 520, 540)
button6 = Button(bird_cat_button_image, 640, 540)
button7 = Button(sniper_cat_button_image, 760, 540)
button8 = Button(lizard_cat_button_image, 880, 540)
button9 = Button(greybutton_image, 1000, 540)
button10 = Button(greybutton_image, 1120, 540)

# 建立貓咪和敵人
global our_sprites
our_sprites = pygame.sprite.Group()
global enemy_sprites
enemy_sprites = pygame.sprite.Group()
global dead_sprites
dead_sprites = pygame.sprite.Group()
global animations
animations = pygame.sprite.Group()


#劇本
enemy_sprites.add(The_face(our_sprites, animations))
enemy_sprites.add(Enemy_cat_god(our_sprites, animations))


run()