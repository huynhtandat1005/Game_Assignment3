import pygame
from pygame import mixer
import os
import random
import csv
import button
import constant

mixer.init()
pygame.init()

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	constant.screen.blit(img, (x, y))


def draw_bg():
	constant.screen.fill(constant.BG)
	width = constant.background.get_width()
	for x in range(5):
		# constant.screen.blit(constant.sky_img, ((x * width) - constant.bg_scroll * 0.5, 0))
		# constant.screen.blit(constant.mountain_img, ((x * width) - constant.bg_scroll * 0.6, constant.SCREEN_HEIGHT - constant.mountain_img.get_height() - 300))
		# constant.screen.blit(constant.pine1_img, ((x * width) - constant.bg_scroll * 0.7, constant.SCREEN_HEIGHT - constant.pine1_img.get_height() - 150))
		# constant.screen.blit(constant.pine2_img, ((x * width) - constant.bg_scroll * 0.8, constant.SCREEN_HEIGHT - constant.pine2_img.get_height()))
		constant.screen.blit(constant.background, ((x * width) - constant.bg_scroll * 0.5, 0))


#function to reset level
def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#create empty tile list
	data = []
	for row in range(constant.ROWS):
		r = [-1] * constant.COLS
		data.append(r)

	return data




class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		if char_type != 'boss':
			self.char_type = char_type
			self.health = 100
		else:
			self.char_type = 'enemy'
			self.health = 400

		self.name = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		#load all images for the players
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#reset movement variables
		screen_scroll = 0
		dx = 0
		dy = 0

		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#apply gravity
		self.vel_y += constant.GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if the ai has hit a wall then make it turn around
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		#check for collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		#check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		#check if fallen off the map
		if self.rect.bottom > constant.SCREEN_HEIGHT:
			self.health = 0


		#check if going off the edges of the screen
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > constant.SCREEN_WIDTH:
				dx = 0

		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		#update scroll based on player position
		if self.char_type == 'player':
			if (self.rect.right > constant.SCREEN_WIDTH - constant.SCROLL_THRESH and constant.bg_scroll < (world.level_length * constant.TILE_SIZE) - constant.SCREEN_WIDTH)\
				or (self.rect.left < constant.SCROLL_THRESH and constant.bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete



	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1
			constant.shot_fx.play()


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#check if the ai in near the player
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.update_action(0)#0: idle
				#shoot
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					#update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > constant.TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += constant.screen_scroll


	def update_animation(self):
		#update animation
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		constant.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = constant.img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * constant.TILE_SIZE
					img_rect.y = y * constant.TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = Soldier('player', x * constant.TILE_SIZE, y * constant.TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = Soldier('enemy', x * constant.TILE_SIZE, y * constant.TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:#create grenade box
						item_box = ItemBox('Grenade', x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(img, x * constant.TILE_SIZE, y * constant.TILE_SIZE)
						exit_group.add(exit)
					elif tile == 21:#create boss
						enemy = Soldier('boss', x * constant.TILE_SIZE, y * constant.TILE_SIZE, 1.65, 4, 40, 0)
						enemy_group.add(enemy)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += constant.screen_scroll
			constant.screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + constant.TILE_SIZE // 2, y + (constant.TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += constant.screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + constant.TILE_SIZE // 2, y + (constant.TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += constant.screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + constant.TILE_SIZE // 2, y + (constant.TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += constant.screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = constant.item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + constant.TILE_SIZE // 2, y + (constant.TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += constant.screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			#delete the item box
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(constant.screen, constant.BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(constant.screen, constant.RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(constant.screen, constant.GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = constant.bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + constant.screen_scroll
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > constant.SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = constant.grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += constant.GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for collision with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		#update grenade position
		self.rect.x += dx + constant.screen_scroll
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			constant.grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#do damage to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < constant.TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < constant.TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < constant.TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < constant.TILE_SIZE * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		#scroll
		self.rect.x += constant.screen_scroll

		EXPLOSION_SPEED = 4
		#update explosion amimation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#if the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(constant.screen, self.colour, (0 - self.fade_counter, 0, constant.SCREEN_WIDTH // 2, constant.SCREEN_HEIGHT))
			pygame.draw.rect(constant.screen, self.colour, (constant.SCREEN_WIDTH // 2 + self.fade_counter, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT))
			pygame.draw.rect(constant.screen, self.colour, (0, 0 - self.fade_counter, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT // 2))
			pygame.draw.rect(constant.screen, self.colour, (0, constant.SCREEN_HEIGHT // 2 +self.fade_counter, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(constant.screen, self.colour, (0, 0, constant.SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= constant.SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


#create screen fades
intro_fade = ScreenFade(1, constant.BLACK, 4)
death_fade = ScreenFade(2, constant.PINK, 4)
victory_fade = ScreenFade(2, constant.GREEN, 4)


#create buttons
start_button = button.Button(constant.SCREEN_WIDTH // 2 - 130, constant.SCREEN_HEIGHT // 2 - 150, constant.start_img, 1)
exit_button = button.Button(constant.SCREEN_WIDTH // 2 - 110, constant.SCREEN_HEIGHT // 2 + 50, constant.exit_img, 1)
restart_button = button.Button(constant.SCREEN_WIDTH // 2 - 100, constant.SCREEN_HEIGHT // 2 - 150, constant.restart_img, 2)
return_button = button.Button(constant.SCREEN_WIDTH // 2 - 100, constant.SCREEN_HEIGHT // 2 + 50, constant.exit_img, 1)

#create sprite groups
enemy_group = pygame.sprite.Group()
bosses = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(constant.ROWS):
	r = [-1] * constant.COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{constant.level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:

	constant.clock.tick(constant.FPS)

	if constant.start_game == False:
		#draw menu
		constant.screen.fill(constant.BG)
		#add buttons
		if start_button.draw(constant.screen):
			constant.start_game = True
			start_intro = True
		if exit_button.draw(constant.screen):
			run = False
	else:
		#update background
		draw_bg()
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		#show ammo
		draw_text('AMMO: ', font, constant.WHITE, 10, 35)
		for x in range(player.ammo):
			constant.screen.blit(constant.bullet_img, (90 + (x * 10), 40))
		#show grenades
		draw_text('GRENADES: ', font, constant.WHITE, 10, 60)
		for x in range(player.grenades):
			constant.screen.blit(constant.grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()
			if enemy.name == 'boss':
				constant.boss_exist = True
				bosses.add(enemy)

		#update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(constant.screen)
		grenade_group.draw(constant.screen)
		explosion_group.draw(constant.screen)
		item_box_group.draw(constant.screen)
		decoration_group.draw(constant.screen)
		water_group.draw(constant.screen)
		exit_group.draw(constant.screen)

		#show intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		#update player actions
		if player.alive:
			#shoot bullets
			if constant.shoot:
				player.shoot()
			#throw grenades
			elif constant.grenade and constant.grenade_thrown == False and player.grenades > 0:
				constant.grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(constant.grenade)
				#reduce grenades
				player.grenades -= 1
				constant.grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif constant.moving_left or constant.moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			constant.screen_scroll, level_complete = player.move(constant.moving_left, constant.moving_right)
			constant.bg_scroll -= constant.screen_scroll

			for boss in bosses:
				if boss.alive:
					constant.boss_exist = True
				else:
					constant.boss_exist = False
			#check if player has completed the level
			if level_complete:
				if constant.level == 1:
					start_intro = True
					constant.level += 1
					bg_scroll = 0
					world_data = reset_level()
					if constant.level <= constant.MAX_LEVELS:
						#load in level data and create world
						with open(f'level{constant.level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)
				elif constant.boss_exist == False:
					if victory_fade.fade():
						if restart_button.draw(constant.screen):
							constant.level = 1
							victory_fade.fade_counter = 0
							start_intro = True
							constant.bg_scroll = 0
							world_data = reset_level()
							#load in level data and create world
							with open(f'level{constant.level}_data.csv', newline='') as csvfile:
								reader = csv.reader(csvfile, delimiter=',')
								for x, row in enumerate(reader):
									for y, tile in enumerate(row):
										world_data[x][y] = int(tile)
							world = World()
							player, health_bar = world.process_data(world_data)

						if return_button.draw(constant.screen):
							constant.start_game = False
				
		else:
			constant.screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(constant.screen):
					death_fade.fade_counter = 0
					start_intro = True
					constant.bg_scroll = 0
					world_data = reset_level()
					#load in level data and create world
					with open(f'level{constant.level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)



	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				constant.moving_left = True
			if event.key == pygame.K_d:
				constant.moving_right = True
			if event.key == pygame.K_SPACE:
				constant.shoot = True
			if event.key == pygame.K_q:
				constant.grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				constant.jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				constant.moving_left = False
			if event.key == pygame.K_d:
				constant.moving_right = False
			if event.key == pygame.K_SPACE:
				constant.shoot = False
			if event.key == pygame.K_q:
				constant.grenade = False
				constant.grenade_thrown = False


	pygame.display.update()

pygame.quit()