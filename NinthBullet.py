#! usr/bin/env python
#    NinthBullet - a run and gun shooter
#    Copyright (C) 2011  Timothy Scott Hayden Dennison
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pygame
from sys import exit
import math
import random
import os
import pickle
import sys
pygame.init()
size=width, height=640, 480
if len(sys.argv) > 1:
	if sys.argv[1] == '-nofullscreen':
		screen = pygame.display.set_mode(size)
else:
	screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
if not 'NinthBulletscores.txt' in os.listdir(os.getcwd()):
	leveldata = {1:[0, 0, 0, 0], 2:[0, 0, 0, 0], 3:[0, 0, 0, 0], 4:[0, 0, 0, 0], 5:[0, 0, 0, 0], 6:[0, 0, 0, 0], 7:[0, 0, 0, 0], 8:[0, 0, 0, 0], 9:[0, 0, 0, 0]}
	scoresfile = open('NinthBulletscores.txt', 'w')
	scoresfile.close()
else:
	file = open('NinthBulletscores.txt', 'r+')
	leveldata = pickle.load(file)
	file.close()
try:
	musicfile = os.getcwd()+os.sep+'sounds'+os.sep+'hero.ogg'
	pygame.mixer.music.load(musicfile)
	pygame.mixer.music.play(-1)
	pygame.mixer.music.play(-1)
except pygame.error, e:
	print pygame.error
	print e
class Vector():
	def __init__(self, x=0.0, y=0.0):
		self.x = x
		self.y = y
	def get_mag(self):
		return math.sqrt(self.x**2 + self.y**2)
	def normalize(self):
		mag = self.get_mag()
		self.x /= mag
		self.y /= mag
	def __add__(self, vector):
		return Vector(self.x+vector.x, self.y+vector.y)
	def __sub__(self, vector):
		return Vector(self.x-vector.x, self.y-vector.y)
	def __div__(self, scalar):
		return Vector(self.x/scalar, self.y/scalar)
	def __mul__(self, scalar):
		return Vector(self.x*scalar, self.y*scalar)
	def __neg__(self):
		return Vector(-self.x, -self.y)
	@classmethod
	def from_points(klass, p1, p2):
		return klass(p1[0]-p2[0], p1[1]-p2[1])
	def __iter__(self):
		return iter([self.x, self.y])
class DummySound():
	def play(self):
		pass
def soundload(soundfile):
	truefile = os.getcwd()+os.sep+'sounds'+os.sep+soundfile
	sound = pygame.mixer.Sound(truefile)
	if sound == None:
		print "Couldn't load sound" + soundfile
		sound = DummySound()
	return sound
jump = soundload('jump.ogg')
shoot = soundload('gun_sound.ogg')
mimehurt = soundload('meanmimehurt.ogg')
playerhurt = soundload('player_hurt.ogg')
ammopacksound = soundload('ammopacksound.ogg')
def imgload(imgfile, colorkey=[255, 255, 255]):
	truefile = os.getcwd()+os.sep+'data'+os.sep+imgfile
	try:
		img = pygame.image.load(truefile)
	except pygame.error, e:
		print "Can't load game image: " + imgfile
		raise SystemExit, e
	if colorkey != None:
		img.set_colorkey(colorkey)
	img.convert()
	return img
class Tile(pygame.sprite.Sprite):
	def __init__(self, img, pos, harmful):
		pygame.sprite.Sprite.__init__(self)
		self.image = imgload(img)
		self.rect = pygame.Rect((pos), (32, 32))
		self.kill = harmful
	def update(self):
		screen.blit(self.image, self.rect)
		return
class AmmoPack(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = imgload('ammopack.png')
		self.rect = self.image.get_bounding_rect()
		self.rect.topleft = pos
	def update(self):
		global screen
		screen.blit(self.image, self.rect)
		return

class Level():
	def __init__(self, tilegroup, psposition, goalpos, baddies, spikes):
		self.tiles = tilegroup
		self.tilerects = []
		for tile in self.tiles:
			self.tilerects.append(tile.rect)
		self.player_start_pos = psposition
		self.goal = Goal(goalpos)
		self.baddies = baddies
		self.ammopacks = pygame.sprite.Group()
		self.poofs = pygame.sprite.Group()
		self.spikes = spikes
		self.psposition = psposition
		self.goalpos = goalpos
		self.finished = False
	def collidewith(self, thing, delete):
		collide = pygame.sprite.spritecollide(thing, self.tiles, delete)
		return collide
	def rectcollidewith(self, rect):
		collide = rect.collidelist(self.tilerects)
		return collide, self.tilerects
	def collidespikes(self, thing):
		collide = pygame.sprite.spritecollideany(thing, self.spikes)
		return collide
	def update(self, player, e):
		global screen
		self.clear(self.baddies)
		self.clear(self.poofs)
		self.clear(self.ammopacks)
		self.clear(pygame.sprite.Group(player))
		player.kill()
		if player.dead == False:
			player.update(self, e)
		self.baddies.update(self, player)
		self.poofs.update()
		self.ammopacks.update()
		self.spikes.update()
		if len(self.baddies) == 0:
			self.goal.rect.topleft = self.goalpos
			self.goal.update()
		else:
			self.goal.rect.center = [10000, 10000]
		self.checkFinished(player)
	def clear(self, group):
		global screen
		for thing in group:
			surface = pygame.Surface((40, 40))
			surface.fill([100, 100, 100])
			screen.blit(surface, pygame.Rect((thing.rect.left-10, thing.rect.top-10), (1, 1)))
	def checkFinished(self, player):
		if player.dead == True:
			if len(self.poofs) == 0:
				self.finished = True
			else:
				self.finished = False
		else:
			self.finished = False
	def won(self, rect):
		return self.goal.rect.colliderect(rect)
	def ammoPack(self, pos):
		self.ammopacks.add(AmmoPack(pos))
	def collideAmmoPack(self, thing):
		collide = pygame.sprite.spritecollide(thing, self.ammopacks, True)
		if len(collide) > 0:
			return True
		else:
			return False
	def collideBaddies(self, thing):
		global playerhurt
		collide = pygame.sprite.spritecollide(thing, self.baddies, False)
		for baddie in self.baddies:
			if pygame.sprite.spritecollide(thing, baddie.group, True):
				thing.hp -= 2
				playerhurt.play()
		if collide:
			for baddie in collide:
				self.poof(baddie.rect.topleft)
			sprite = collide[0]
			self.baddies.remove(collide)
			return True, sprite.playerhit, sprite
		else:
			return False, None, None
	def poof(self, pos):
		Explosion(pos, self.poofs)
		return
class Goal(pygame.sprite.Sprite):
	def __init__(self, pos):
		self.img = imgload('goal.png')
		self.rect = self.img.get_rect()
		self.rect.topleft = pos
	def update(self):
		global screen
		screen.blit(self.img, self.rect)
		return
class Spike(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect((pos), (26, 26))
		self.image = imgload('spikes.png')
		self.rect.top += 11
	def update(self):
		pygame.draw.rect(screen, [255, 255, 255], self.rect, 2)
		screen.blit(self.image, [self.rect.left-2, self.rect.top-4])
		return

def loadLevel(levelmap):
	curpos = [0, 0]
	tiles = pygame.sprite.Group()
	playerpos = [0, 0]
	goalpos = [0, 0]
	baddies = pygame.sprite.Group()
	spikes = pygame.sprite.Group()
	for row in levelmap:
		for tile in row:
			if tile == '_':
				tile = Tile('tile_top.png', curpos, False)
				tiles.add(tile)
			elif tile == '#':
				tile = Tile('tile_mid.png', curpos, False)
				tiles.add(tile)
			elif tile == '|':
				tile = Tile('tile_rightmid.png', curpos, False)
				tiles.add(tile)
			elif tile == '/':
				tile = Tile('tile_leftmid.png', curpos, False)
				tiles.add(tile)
			elif tile == '(':
				tiles.add(Tile('tile_bottomleft.png', curpos, False))
			elif tile == ')':
				tiles.add(Tile('tile_bottomright.png', curpos, False))
			elif tile == 'G':
				goalpos = curpos[:]
			elif tile == 'P':
				playerpos = curpos[:]
			elif tile == '%':
				baddies.add(MeanMime(curpos))
			elif tile == '!':
				baddies.add(MeanSniper(curpos))
			elif tile == '*':
				baddies.add(MeanKnight(curpos))
			elif tile == '^':
				spikes.add(Spike(curpos))
			else:
				pass
			curpos[0] += 32
		curpos[0] = 0
		curpos[1] += 32
	level = Level(tiles, playerpos, goalpos, baddies, spikes)
	return level
class Explosion(pygame.sprite.Sprite):
	def __init__(self, pos, group):
		pygame.sprite.Sprite.__init__(self)
		self.imglist = [imgload('poof1.png'), imgload('poof2.png'), imgload('poof3.png')]
		self.rect = pygame.Rect((pos), (1, 1))
		self.timer = 0
		self.group = group
		self.add(group)
	def update(self):
		global screen
		
		self.timer += 1
		if self.timer < 4:
			screen.blit(self.imglist[0], self.rect)
		elif self.timer > 4 and self.timer < 8:
			screen.blit(self.imglist[1], self.rect)
		elif self.timer > 8 and self.timer < 12:
			screen.blit(self.imglist[2], self.rect)
		elif self.timer > 12:
			pygame.draw.rect(screen, [100, 100, 100], self.rect.inflate(30, 30))
			self.group.remove(self)
		return

class Player(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.imgdict = {'running':[imgload('agent_running2.png'), imgload('agent_running3.png'), imgload('agent_running3.png'), imgload('agent_running4.png')], 'jumping':imgload('agent_running1.png'), 'crouching':imgload('agent_crouch.png')}
		self.rect = pygame.Rect((pos), (30, 30))
		self.xdif = -8
		self.ydif = -5
		self.rect = self.rect.inflate(self.xdif, self.ydif)
		self.vector = Vector()
		self.yaccel = 4
		self.xaccel = 5
		self.moving = [False, False]
		self.grounded = False
		self.jumping = False
		self.bullethandler = BulletHandler(self)
		self.dead = False
		self.jump_timer = 0
		self.facing='right'
		self.animationtimer = 0
		self.hp = 9
	def update(self, level, lastevent):
		global screen
		pygame.draw.rect(screen, [100, 100, 100], self.rect.inflate(-self.xdif+8, -self.ydif+8))
		self.updateMovement()
		self.updateCollision(level)
		self.checkBaddiesandAmmo(level)
		self.move()
		self.updateBullets(lastevent, level)
		self.updatePowerups()
		self.draw()
		return
	def updateMovement(self):
		global screen, jump
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			if self.vector.x < 13:
				self.vector.x += self.xaccel
			self.facing = 'right'
		elif keys[pygame.K_LEFT]:
			if self.vector.x > -13:
				self.vector.x -= self.xaccel
			self.facing = 'left'
		else:
			self.vector.x /= 1.5
		if int(self.vector.x) in list(xrange(-2, 2)):
			self.vector.x = 0
		if keys[pygame.K_z]:
			if self.jumping == True:
				self.vector.y -= self.yaccel
			else:
				if self.grounded == True:
					self.vector.y -= self.yaccel*2
					self.jumping = True
					self.jump_timer = 6
					jump.play()
		if self.vector.x != 0:
			self.moving[0] = True
		else:
			self.moving[0] = False
		if self.vector.y != 0:
			self.moving[1] = True
		else:
			self.moving[1] = False
		if self.jumping == True:
			self.jump_timer -= 1
		if self.jump_timer < 1:
			self.jumping = False
			self.grounded = False
		if self.grounded==False and self.jumping==False:
			if self.vector.y < 14:
				self.vector.y += self.yaccel*1.5
		if self.vector.y in list(xrange(-2, 2)):
			self.vector.y = 0
		if keys[pygame.K_DOWN]:
			self.crouch = True
			self.vector = Vector(0, 1)
		else:
			self.crouch = False
			self.rect.width, self.rect.height = 30+self.xdif, 30+self.ydif
		if self.crouch == True:
			self.rect.width = 20
			self.height = 20
			self.vector.y = 10
		return
	def checkBaddiesandAmmo(self, level):
		global ammopacksound, jump, playerhurt
		if level.collideAmmoPack(self) == True:
			self.bullethandler.ammoPack()
			ammopacksound.play()
		collide, lifegone, baddie = level.collideBaddies(self)
		if collide == True:
			self.hp -= lifegone
			playerhurt.play()
		sprite = level.collidespikes(self)
		if sprite != None: 
			if self.rect.centerx in list(xrange(sprite.rect.left, sprite.rect.right)):
				playerhurt.play()
				self.dead = True
				self.hp = 0
			else:
				pass
		if self.hp <= 0:
			self.dead = True
			level.poof(self.rect.topleft)
	def updateCollision(self, level):
		global height, width, ammopacksound, jump
		if False == self.moving[0] and False == self.moving[1]:
			return
		collide = level.collidewith(self, False)
		if len(collide) != 0 and self.rect.bottom != height:
			self.grounded = True
			if collide[0].kill == True:
				self.hp = 0
				self.dead = True
		if self.moving[0]:
			xmove = self.rect.move([self.vector.x, 0])
			collide, rectlist = level.rectcollidewith(xmove)
			if collide != -1:
				collidedrect = rectlist[collide]
				if self.rect.centerx >= collidedrect.centerx:
					self.vector.x = -(self.rect.left - collidedrect.right)
					self.grounded = True
				else:
					self.vector.x = (collidedrect.left - self.rect.right)
					self.grounded = True
		if self.moving[1]:
			ymove = self.rect.move([0, self.vector.y])
			collide, rectlist = level.rectcollidewith(ymove)
			if collide != -1:
				collidedrect = rectlist[collide]
				if self.rect.centery >= collidedrect.centery:
					self.rect.top = collidedrect.bottom-1
					self.vector.y = 1

				else:
					self.rect.bottom = collidedrect.top+1
					self.vector.y = -1
					self.moving[1] = False
					self.grounded = True
			else:
				self.grounded = False
		if self.rect.bottom > height:
			self.dead = True
			self.hp = 0
			self.rect.bottom = height
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.right > width:
			self.rect.right = width
			self.vector.x = -self.vector.x
		if self.rect.left < 0:
			self.vector.x = -self.vector.x
			self.rect.left = 0
		return
	def move(self):
		self.rect = self.rect.move(list(self.vector))
		return
	def updateBullets(self, lastevent, level):
		self.bullethandler.update(lastevent, level)
		return
	def updatePowerups(self):
		pass
	def draw(self):
		global screen, font
		self.animationtimer += 1
		
		if self.facing == 'right':
			if self.moving[0]:
				screen.blit(self.imgdict['running'][self.animationtimer%len(self.imgdict['running'])], [self.rect.left+self.xdif/2, self.rect.top+self.ydif])
			elif self.moving[1]:
				screen.blit(self.imgdict['jumping'], [self.rect.left+self.xdif/2, self.rect.top+self.ydif])
			elif self.crouch == True:
				screen.blit(self.imgdict['crouching'], [self.rect.left+self.xdif/2, self.rect.top+self.ydif])
			else:
				screen.blit(self.imgdict['running'][3], [self.rect.left+self.xdif/2, self.rect.top+self.ydif])
		elif self.facing == 'left':
			if self.moving[0]:
				screen.blit(pygame.transform.flip(self.imgdict['running'][self.animationtimer%len(self.imgdict['running'])], 1, 0), [self.rect.left+self.xdif, self.rect.top+self.ydif])
			elif self.moving[1]:
				screen.blit(pygame.transform.flip(self.imgdict['jumping'], 1, 0), [self.rect.left+self.xdif, self.rect.top+self.ydif])
			elif self.crouch == True:
				screen.blit(pygame.transform.flip(self.imgdict['crouching'], 1, 0), [self.rect.left+self.xdif, self.rect.top+self.ydif])
			else:
				screen.blit(pygame.transform.flip(self.imgdict['running'][3], 1, 0), [self.rect.left+self.xdif, self.rect.top+self.ydif])
		return
class Bullet(pygame.sprite.Sprite):
	def __init__(self, group, pos, speed):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect((pos), (5, 2))
		self.speed = speed
		self.group = group
		self.add(group)
	def update(self, level):
		global screen, size
		pygame.draw.rect(screen, [100, 100, 100], self.rect)
		if len(level.collidewith(self, False)) == 0:
			self.rect = self.rect.move(self.speed)
			pygame.draw.rect(screen, [0, 100, 100], self.rect)
		else:
			self.group.remove(self)
		if self.rect.centerx > size[0] or self.rect.centerx < 0:
			pygame.draw.rect(screen, [100, 100, 100], self.rect)
			self.group.remove(self)
		return
class MeanSniper(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.imglist = [imgload('meansniper2.png'), imgload('meansniper1.png'), imgload('meansniperhurt.png')]
		self.rect = pygame.Rect((pos), (30, 20))
		self.rect.top += 15
		self.animationtimer = 0
		self.group = pygame.sprite.Group()
		self.hp = 6
		self.bullet_timer = 30
		self.hurtframe = False
		self.image = None
		self.playerhit = 6
	def update(self, level, player):
		if player.rect.centerx >= self.rect.centerx:
			self.facing = 'right'
		else:
			self.facing = 'left'
		self.group.update(level)
		if self.bullet_timer > 0:
			self.bullet_timer -= 1
		if player.rect.centery in list(xrange(self.rect.top-10, self.rect.bottom)):
			if self.facing == 'right' and self.bullet_timer == 0:
				self.group.add(Bullet(self.group, self.rect.midright, [15, 0]))
				self.bullet_timer = 50
			elif self.facing == 'left' and self.bullet_timer == 0:
				self.group.add(Bullet(self.group, self.rect.midleft, [-15, 0]))
				self.bullet_timer = 50
			self.image = self.imglist[0]
			self.ydif = -5
		else:
			self.image = self.imglist[1]
			self.ydif = 0
		if self.hurtframe == True:
			self.image = self.imglist[2]
			self.hurtframe = False
		if self.facing == 'left':
			screen.blit(pygame.transform.flip(self.image, 1, 0), [self.rect.left, self.rect.top + self.ydif])
		else:
			screen.blit(self.image, [self.rect.left, self.rect.top + self.ydif])
		if pygame.sprite.spritecollide(self, player.bullethandler.group, True):
			self.hp -= 1
			if self.hp < 0:
				level.poof(self.rect.center)
				level.ammoPack(self.rect.topleft)
				player.bullethandler.upgrade()
				pygame.draw.rect(screen, [100, 100, 100], self.rect.inflate(10, 10))
				level.baddies.remove(self)

			self.hurtframe = True
		return
class BulletHandler():
	def __init__(self, player, maxammo=9):
		self.group = pygame.sprite.Group()
		self.player = player
		self.ammo = maxammo
		self.maxammo = self.ammo
	def update(self, lastevent, level):
		global screen, font, shoot
		
		self.group.update(level)
		if lastevent.type == pygame.KEYDOWN and lastevent.key == pygame.K_x:
			if self.player.facing == 'right' and self.ammo > 0:
				if self.player.crouch == False:
					self.createBullet([self.player.rect.right, self.player.rect.centery-9], [20, 0])
				else:
					self.createBullet(self.player.rect.midright, [20, 0])
				shoot.play()
			elif self.player.facing == 'left' and self.ammo > 0:
				if self.player.crouch == False:
					self.createBullet([self.player.rect.left, self.player.rect.centery-9], [-20, 0])
				else:
					self.createBullet(self.player.rect.midleft, [-20, 0])
				shoot.play()
	def createBullet(self, place, speed):
		Bullet(self.group, place, speed)
		self.ammo -= 1
	def ammoPack(self):
		if self.ammo == self.maxammo:
			self.upgrade()
		self.ammo = self.maxammo
	def upgrade(self):
		self.maxammo += 9
		self.ammo = self.maxammo
class MeanKnight(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.imgdict = {'attack':[imgload('meanknightattack3.png'), imgload('meanknightattack1.png'), imgload('meanknightattack2.png')]}
		self.rect = pygame.Rect((pos), (32, 32))
		self.xdif = -10
		self.ydif = -5
		self.rect.top += 3
		self.rect = self.rect.inflate(self.xdif, self.ydif)
		self.facing = 'right'
		self.group = pygame.sprite.Group()
		self.hp = 6
		self.vector = Vector(0, 0)
		self.animationtimer = 0
		self.playerhit = 10
	def update(self, level, player):
		global screen, mimehurt
		self.animationtimer += 1
		if player.rect.centery in list(xrange(self.rect.top, self.rect.bottom)):
			if abs(self.rect.centerx-player.rect.centerx) < 200:
				self.attack = True
			else:
				self.attack = False
		else:
			self.attack = False
		if player.rect.centerx >= self.rect.centerx:
			self.facing = 'right'
		else:
			self.facing='left'
		collide = pygame.sprite.spritecollide(self, player.bullethandler.group, False)
		if self.attack == True:
			if collide:
				self.hp -= len(collide)
				player.bullethandler.group.remove(collide)
				if self.hp < 0:
					level.poof(self.rect.topleft)
					level.ammoPack(self.rect.topleft)
					player.bullethandler.upgrade()
					mimehurt.play()
					pygame.draw.rect(screen, [100, 100, 100], self.rect.inflate(5, 5))
					level.baddies.remove(self)
		else:
			if collide:
				Bullet(self.group, self.rect.center, [-collide[0].speed[0], 0])
				player.bullethandler.group.remove(collide)
		self.group.update(level)
		if self.attack == True:
			if self.facing == 'right':
				self.vector.x = 6
			elif self.facing == 'left':
				self.vector.x = -6
		else:
			self.vector.x = 0
		collide = level.collidewith(self, False)
		if collide:
			sprite = collide[0]
			if self.rect.centery in list(xrange(sprite.rect.top+3, sprite.rect.bottom-3)):
				self.vector.x = -self.vector.x
			else:
				self.rect.bottom = sprite.rect.top
		self.rect = self.rect.move(list(self.vector))
		if self.facing == 'right':
			if self.attack == True:
				self.image = self.imgdict['attack'][self.animationtimer%len(self.imgdict['attack'])]
			else:
				self.image = self.imgdict['attack'][0]
			screen.blit(self.image, [self.rect.left+5, self.rect.top-3])
		else:
			if self.attack == True:
				self.image = self.imgdict['attack'][self.animationtimer%len(self.imgdict['attack'])]
			else:
				self.image = self.imgdict['attack'][0]
			screen.blit(pygame.transform.flip(self.image, 1, 0), [self.rect.left, self.rect.top-3])
		return
class MeanMime(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.imgdict = {'walk':[imgload('meanmime1.png'), imgload('meanmime2.png'), imgload('meanmime2.png'), imgload('meanmime3.png'), imgload('meanmime3.png'), imgload('meanmime3.png')]}
		self.rect = pygame.Rect((pos), (30, 30))
		self.rect.top += 1
		self.xdif = -5
		self.ydif = -5
		self.rect = self.rect.inflate(self.xdif, self.ydif)
		self.speed = [5, 0]
		self.facing = 'right'
		self.animationtimer = 0
		self.hp = 5
		self.group = pygame.sprite.Group()
		self.playerhit = 4
	def update(self, level, player):
		global screen, width, height, mimehurt
		self.hurtframe = False
		if pygame.sprite.spritecollide(self, player.bullethandler.group, True) != []:
			self.hp -= 1
			if self.hp < 0:
				level.ammoPack(self.rect.topleft)
				level.poof(self.rect.topleft)
				pygame.draw.rect(screen, [100, 100, 100], self.rect.inflate(-self.xdif*2+1, -self.ydif*2+1))
				level.baddies.remove(self)
			self.hurtframe = True
			mimehurt.play()
		else:
			self.hurtframe = False
		self.rect = self.rect.move(self.speed)
		collide = level.collidewith(self, False)
		if len(collide) > 0:
			sprite = collide[0]
			self.speed[1] = 0
			if self.rect.centery in list(xrange(sprite.rect.top+4, sprite.rect.bottom-4)):
				self.speed[0] = -self.speed[0]
				self.rect.centerx += self.speed[0]
			else:
				self.rect.bottom = sprite.rect.top
		else:
			self.speed[1] = 5
		if self.rect.right > width or self.rect.left < 0:
			self.speed[0] = -self.speed[0]
		if self.speed[0] > 0:
			self.facing = 'right'
		else:
			self.facing = 'left'
		if self.rect.bottom > height:
			self.rect.bottom = height
			self.speed[1] = 0
		self.animationtimer += 1
		if self.facing == 'right':
			if self.hurtframe == True:
				image = pygame.transform.flip(self.imgdict['walk'][self.animationtimer%6], 0, 0)
				image.fill([255, 0, 0])
				screen.blit(image, [self.rect.left+self.xdif/2, self.rect.top+self.ydif/2])
				del image
			else:
				screen.blit(self.imgdict['walk'][self.animationtimer%6], [self.rect.left+self.xdif, self.rect.top+self.ydif])
		else:
			if self.hurtframe == True:
				image = pygame.transform.flip(self.imgdict['walk'][self.animationtimer%6], 1, 0)
				image.fill([255, 0, 0])
				screen.blit(image, [self.rect.left+self.xdif/2, self.rect.top+self.ydif/2])
				del image
			else:
				screen.blit(pygame.transform.flip(self.imgdict['walk'][self.animationtimer%6], 1, 0), [self.rect.left+self.xdif, self.rect.top+self.ydif])
		return

		
def mainloop(player, level):
	global clock, screen, size, width, height, font
	screen.fill([100, 100, 100])
	hp = 0
	bullets = 0
	maxbullets = 0
	time = 0
	while level.won(player.rect) == False and level.finished == False:
		e = pygame.event.poll()
		if e.type == pygame.QUIT:
			pygame.quit()
			exit()
		elif e.type == pygame.KEYDOWN:
			if e.key == pygame.K_ESCAPE:
				pygame.quit()
				exit()
			elif e.key == pygame.K_q or e.key == pygame.K_r:
				screen.unlock()
				return None, None, None, None
			elif e.key == pygame.K_p:
				while True:
					e = pygame.event.wait()
					if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
						break
		screen.unlock()
		hp = player.hp
		bullets = player.bullethandler.ammo
		maxbullets = player.bullethandler.maxammo
		time += 1
		level.update(player, e)
		level.tiles.update()
		screen.blit(font.render((str(player.bullethandler.ammo) + '/' + str(player.bullethandler.maxammo) + '  '), True, [255, 255, 255], [100, 100, 100]), [0, 0])
		screen.blit(font.render(('HP: '+str(player.hp) + '  '), True, [255, 255, 255], [100, 100, 100]), [0, 32])
		pygame.display.flip()
		screen.lock()
		clock.tick(30)
	screen.unlock()
	screen.fill([100, 100, 100])
	if player.dead == False:
		return bullets, maxbullets, hp, time
	else:
		return None, None, None, None
def menu(options, position):
	global screen, clock
	splashscreen = imgload('splashscreen.png', None)
	cursorpos = 0
	pos = position[:]
	screen.blit(splashscreen, [0, 0])
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					exit()
				elif event.key == pygame.K_DOWN:
					if cursorpos < len(options)-1:
						cursorpos += 1
				elif event.key == pygame.K_UP:
					if cursorpos > 0:
						cursorpos -= 1
				elif event.key == pygame.K_RETURN:
					return options[cursorpos]
		for option in options:
			if options.index(option) == cursorpos:
				screen.blit(font.render(str(option), True, [255, 255, 0], [0, 0, 255]), pos)
			else:
				screen.blit(font.render(str(option), True, [0, 255, 0], [0, 0, 255]), pos)
			pos[1] += 32
		pos = position[:]
		pygame.display.flip()
		clock.tick(30)
testlevelmap = ['                    ',
	        '       P      __    ',
		'      _  __ %   |___',
		'_____()  (____  ####',
		'                    ',
		'   G           %    ',
		'_________   ________',
		'     )       (      ',
		'     _________      ']
level1 = ['P                   ',
	  '      _ %       _   ',
	  '______#_________#   ',
	  '                    ',
	  '                %   ',
	  '      %%%       _   ',
	  '________________#   ',
	  '                    ',
	  '  __________________',
	  '                    ',
	  '                 _  ',
	  '_________________#  ',
	  'G      %            ',
	  '____________________']
level2 = ['                 (G ',
	  '                 _ _',
	  '                 # #',
	  'P                # #',
	  '____             # #',
	  '                 # #',
	  '                 # #',
	  '         ___     # #',
	  '          !   %    (',
	  '____________________']
level4 = ['                    ',
	  'P                   ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                   _',
	  '             *     G',
	  '____________________']
level3 = ['P                   ',
	      '_                   ',
	      '#_                  ',
	      '##_                 ',
	      '###_              __',
	      '####_             (G',
	      '#####_              ',
	      '#####|      ^_    ! ',
	      '#####)__%____#______']
level5 = ['                    ',
	  ' G                  ',
	  '__________________  ',
	  '                 |  ',
	  '__ _____ %       )  ',
	  '|      /________ |  ',
	  '|_     /       ! |  ',
	  '()_    /   ______)  ',
	  '       (P  |     )  ',
	  '   _   )___         ',
	  '              *     ',
	  '___________________ ',
	  '                    ',
	  '  %%%              _',
	  '___________________)']

blanklevel = ['                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ',
	  '                    ']
level6 = ['G                  /',
	  '                   /',
	  '     %      _      /',
	  '____________)      /',
	  '                   /',
	  '           !       /',
	  '______ ____________)',
	  '                   /',
	  '                   /',
	  '_____ _______  %   /',
	  '             ______)',
	  '    _          *    ',
	  '____#___ ___________',
	  'P        |          ',
	  '_________)          ']
level7 = ['P                   ',
	  '______________      ',
	  '            G|      ',
	  '             )      ',
	  '       %%%%%        ',
	  '_ __________________',
	  '                    ',
	  '           !        ',
	  '______________ _____',
	  '                  * ',
	  ' ___________________',
	  '                    ',
	  '  ^    ^     ^     G',
	  '____________________',
	  '                    ']
level8 = ['                    ',
	  'P                   ',
	  '__    _    __    _  ',
	  '  ^^^^ ^^^^  ^^^^   ',
	  '  ____              ',
	  '     %%%            ',
	  '_ __________________',
	  '   ^             !  ',
	  '  ^ ____ ___________',
	  '    ^               ',
	  '^    ^  ______      ',
	  ' ^    ^             ',
	  '  ^   ^        ^__  ',
	  '         ^   G      ',
	  '  __________________']
level9 = ['P                   ',
	  '                    ',
	  '_________)    ^____ ',
	  '          ^^^^^     ',
	  '    ^^              ',
	  '  (_________________',
	  '  /                 ',
	  '  /    __^          ',
	  '  /   |          *  ',
	  '  /   |  ___________',
	  '  /   |             ',
	  '  /   |    %%%      ',
	  '  /   |___________ _',
	  '      |G            ',
	  '______)_____________']
def savescore(bullets, maxbullets, hp, time, levelnum):
	global leveldata
	if bullets == None:
		return
	for entry in leveldata:
		if entry == levelnum:
			if leveldata[entry][0] >= bullets or leveldata[entry][0]== 0:
				leveldata[entry][0] = bullets
			if leveldata[entry][1] >= maxbullets or leveldata[entry][1] == 0:
				leveldata[entry][1] = maxbullets
			if leveldata[entry][2] >= hp or leveldata[entry][2] == 0:
				leveldata[entry][2] = hp
			if leveldata[entry][3] <= time or leveldata[entry][3] == 0:
				leveldata[entry][3] = time
	scoresfile = open('NinthBulletscores.txt', 'r+')
	pickle.dump(leveldata, scoresfile)
	scoresfile.close()
	return

def main():
	global leveldata, level1, level2, level3, level4, level5, level6, level7, level8
	while True:
		while True:
			options = ['Exit', 'Play Game', 'Erase Progress']
			option = menu(options, [400, 200])
			if option == 'Exit':
				pygame.quit()
				exit()
			elif option == 'Play Game':
				break
			elif option == 'Erase Progress':
				leveldata = {1:[0, 0, 0, 0], 2:[0, 0, 0, 0], 3:[0, 0, 0, 0], 4:[0, 0, 0, 0], 5:[0, 0, 0, 0], 6:[0, 0, 0, 0], 7:[0, 0, 0, 0], 8:[0, 0, 0, 0], 9:[0, 0, 0, 0]}
		while True:
			options = ['Back', 'Stats', 'Help']
			for i in range(1, len(leveldata)+1):
				options.append('Level ' + str(i))
			option = menu(options, [300, 100])
			option = option[:7]
			if option == 'Back':
				main()
			elif option == 'Stats':
				while True:
					options = ['Back']
					for i in range(1, len(leveldata)+1):
						options.append((str(i) + ' Clip: '+str(leveldata[i][0]) + ' Mag: ' + str(leveldata[i][1]) + ' HP: ' + str(leveldata[i][2]) + ' Time: ' + str(leveldata[i][3])))
					option = menu(options, [200, 130])
					if option == 'Back':
						break
			elif option == 'Help':
				while True:
					options = ['Back']
					options.append('X: Shoot your gun. Z: Jump. Hold down for a higher jump.')
					options.append('Arrow keys: Move your character. Press down to crouch.')
					options.append('Press Escape to quit. Press Q and R to go back to the menu.')
					options.append('Press against a wall and press Z to wall-jump.')
					options.append('Press P to pause')
					options.append('You can also pass the flag -nofullscreen to disable fullscreen')
					option = menu(options, [1, 130])
					if option == 'Back':
						break
			elif option == 'Level 1':
				level = loadLevel(level1)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 1)
				
			elif option == 'Level 2':
				level = loadLevel(level2)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 2)
			elif option == 'Level 3':
				level = loadLevel(level3)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 3)
			elif option == 'Level 4':
				level = loadLevel(level4)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 4)
			elif option == 'Level 5':
				level = loadLevel(level5)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 5)
			elif option == 'Level 6':
				level = loadLevel(level6)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 6)
			elif option == 'Level 7':
				level = loadLevel(level7)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 7)
			elif option == 'Level 8':
				level = loadLevel(level8)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 8)
			elif option == 'Level 9':
				level = loadLevel(level9)
				player = Player(level.player_start_pos)
				bullets, maxbullets, hp, time = mainloop(player, level)
				savescore(bullets, maxbullets, hp, time, 9)
if __name__ == '__main__':
	main()
