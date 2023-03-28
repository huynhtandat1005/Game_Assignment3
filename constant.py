import pygame
from pygame import mixer

mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 24
MAX_LEVELS = 2
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
play_bg = 1
about = False
option = False
play_s = True
play_m = True

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
boss_exist = False
gold = 0
silver = 0

#load music and sounds
#pygame.mixer.music.load('audio/music2.mp3')
#pygame.mixer.music.set_volume(0.3)
#pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(1)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(1)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(1)


#load images
#button images
new_game = pygame.image.load('img/new_game.png').convert_alpha()
about_img = pygame.image.load('img/about_btn.png').convert_alpha()
info_img = pygame.image.load('img/info.png').convert_alpha()
option_img = pygame.image.load('img/option_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
return_img = pygame.image.load('img/return_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
back_img = pygame.image.load('img/back_btn.png').convert_alpha()
musicANDsound_img = pygame.image.load('img/option_edit.png').convert_alpha()
off_img = pygame.image.load('img/off_btn.png').convert_alpha()
on_img = pygame.image.load('img/on_btn.png').convert_alpha()


#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
background = pygame.image.load('img/background/single_background.png').convert_alpha()
background = pygame.transform.scale(background, (background.get_width()*2, SCREEN_HEIGHT))


#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}

gold_img = pygame.image.load('img/coins/Gold/0.png')
silver_img = pygame.image.load('img/coins/Silver/0.png')


#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

