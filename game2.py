from math import floor
from math import ceil
import re

import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()


reCommand = re.compile(r'/(\w+) (\w+)')


my_font = pygame.font.SysFont('Comic Sans MS', 16)


GRIDSIZE = 32
GRIDX = 12
GRIDY = 12
# screen height/width
GAMESTATE = "GAMEPLAY"  # either 'EDITOR' or 'GAMEPLAY', determines mode of game


CAMERAX = 0
CAMERAY = 0


GRID = [
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0,
   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
] # temp
# GRID DEFINES LEVEL LAYOUT:
# 0 = AIR
# 1 = BLOCK
# 2 = ENEMY (initial position)
# 3 = Player spawn


def handleCommand(var1,var2):
   print(f"Command {var1} with {var2}")
   var1 = var1.lower()
   global GAMESTATE
   if var1 == "state":
       GAMESTATE = str(var2.upper())
       print(f"state set to {var2.upper()}")
   if var1 == "print":
       print(var2)
   elif var1 == "respawn":
       P1.rect.center = P1.spawn
       P1.update()
       print("done")

def getPosStatComp(x, y):
   statCord = 0
   yer = y * GRIDX
   statCord = x + yer
   return GRID[statCord]




def getPosStatRaw(x, y):
   compX = floor(x / GRIDSIZE)
   compY = floor(y / GRIDSIZE)
   return getPosStatComp(compX, compY)




def getPosComp(x, y):
   yer = y * GRIDX
   statCord = x + yer
   return statCord


def getPosRaw(x, y):
   compX = floor(x / GRIDSIZE)
   compY = floor(y / GRIDSIZE)
   return getPosComp(compX, compY)


def ClampI(val,min,max):
   if(val > max):
       return max
   elif(val < min):
       return min
   else:
       return val


def isClampI(val,min,max):
   if (val > max):
       return True
   elif (val < min):
       return True
   else:
       return False


def handleButtons(id):
    global GAMESTATE
    print(f"button \"{id}\" was pushed!")
    if (id == 'ToggleMode'):
        if (GAMESTATE == 'EDITOR'):
            GAMESTATE = 'GAMEPLAY'
        elif (GAMESTATE == 'GAMEPLAY'):
            GAMESTATE = 'EDITOR'
    else:
        cHair.mode = id


#///// Groups
class worldGroup(pygame.sprite.Group):
   def __init__(self):
       super().__init__()
       self.display_surface = pygame.display.get_surface()


class uiGroup(pygame.sprite.Group):
   def __init__(self):
       super().__init__()
       self.display_surface = pygame.display.get_surface()




class Final(pygame.sprite.Sprite):
   def __init__(self, x, y):
       super().__init__()
       self.x = x
       self.y = y
       self.image = pygame.image.load("Gold.png")
       self.rect = self.image.get_rect()
       self.rect.center = (x, y)

   def draw(self, surface):
       surface.blit(self.image, self.rect)

def draw(self, surface):
   surface.blit(self.image, self.rect)
   self.frameUpdate()

class Player(pygame.sprite.Sprite):
   def __init__(self, x, y):
       super().__init__()

       self.imageSRC = pygame.image.load("Temp.png")
       self.image = self.imageSRC
       self.imageC = pygame.image.load("Blue.png")


       self.frameStart = 0
       self.frameEnd = 4
       self.frameMax = 4
       self.frameCurrent = 0


       self.fps = 15
       self.fpsCurrent = 0


       self.rect = self.imageC.get_rect()
       self.rect.center = (x, y)
       self.spawn = (x, y)
       self.velocityX = 0
       self.velocityY = 0
       self.terminalVelocityY = 15  # terminal falling velocity of Player
       self.on_floor = False  # is Player currently on floor? used to prevent air-jumping


   def setAnimation(self,StartFrame,EndFrame,FPS):
       pass


   def frameNext(self):
       if self.frameCurrent == self.frameEnd or self.frameCurrent == self.frameMax:
           self.frameCurrent = self.frameStart
       else:
           self.frameCurrent += 1


   def frameUpdate(self):
       imagePass1 = pygame.transform.chop(self.imageSRC, (0, 32, 32 * self.frameCurrent, 32))
       imagePass2 = pygame.transform.chop(imagePass1, (32, 32, 160, 32))
       self.image = imagePass2


   def colX(self):
       for block in BLOCKS:  # check collision x-direction
           if self.rect.colliderect(block):
               if self.velocityX > 0:  # moving right
                   self.rect.right = block.rect.left
               if self.velocityX < 0:  # moving left
                   self.rect.left = block.rect.right

   def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.frameUpdate()

   def colY(self):
       is_colliding = False
       for block in BLOCKS:  # check collision y-direction
           if self.rect.colliderect(block):
               is_colliding = True
               if self.velocityY > 0:  # moving down, on ground, has stopped jumping
                   self.rect.bottom = block.rect.top
                   self.on_floor = True
                   self.velocityY = 0
               if self.velocityY < 0:  # moving up, not on ground
                   self.rect.top = block.rect.bottom
                   self.velocityY = 0
                   self.on_floor = False
       if not is_colliding: self.on_floor = False  # if not colliding with anything, it can't be on the floor


   def move(self):
       self.rect.x += self.velocityX
       self.colX()
       self.rect.y += self.velocityY
       self.colY()
       if (self.rect.y > GRIDSIZE * GRIDY):
           self.rect.center = self.spawn

   def update(self):
       #Animation
       if self.fpsCurrent == self.fps:
           self.fpsCurrent = 0
           self.frameNext()
       else:
           self.fpsCurrent += 1
       pass




       #movement
       pressed_keys = pygame.key.get_pressed()  # gets list of currently pressed keys
       if pressed_keys[K_UP] and self.on_floor:
           self.velocityY = -12
           self.on_floor = False
       if self.rect.left > 0:
           if pressed_keys[K_LEFT]:
               self.velocityX = -4
       if self.rect.right < WIDTH:
           if pressed_keys[K_RIGHT]:
               self.velocityX = 4
       if not pressed_keys[K_LEFT] and not pressed_keys[K_RIGHT]:
           self.velocityX = 0


       if self.velocityY >= self.terminalVelocityY:
           self.velocityY = self.terminalVelocityY  # limit downward velocity to terminal velocity
       else:
           self.velocityY += 1


       self.move()




### list of blocks and enemies
BLOCKS = []
ENEMIES = []




###




class Block(pygame.sprite.Sprite):
   def __init__(self, x, y):
       super().__init__()
       self.x = x
       self.y = y
       self.image = pygame.image.load("Red.png")
       self.rect = self.image.get_rect()
       self.rect.center = (x, y)


   def draw(self, surface):
       if (getPosStatRaw(self.x, self.y) == 0):
           return
       surface.blit(self.image, self.rect)




class Crosshair(pygame.sprite.Sprite):  # cursor that places/destroys objects
   def __init__(self, x, y):
       super().__init__()
       self.image = pygame.image.load("Green.png")
       self.rect = self.image.get_rect()
       self.rect.center = (x, y)
       self.isOnGrid = True

       self.mode = "SelectWall"

   def draw(self, surface):
       surface.blit(self.image, self.rect)


   def update(self):


       MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
       MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
       self.x = ClampI(MouseX,16,GRIDX * GRIDSIZE - 16)
       self.y = ClampI(MouseY,16,GRIDY * GRIDSIZE - 16)


       self.rect.center = (self.x, self.y)
       if(isClampI(MouseX,16,GRIDX * GRIDSIZE - 16) or isClampI(MouseY,16,GRIDY * GRIDSIZE - 16)):
           self.isOnGrid = False
       else:
           self.isOnGrid = True


   def create(self):
       if(self.isOnGrid == False):
           return
       MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
       MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2

       if self.mode == 'SelectWall':
           GRID[getPosRaw(self.x, self.y)] = 1
           BLOCKS.append(Block(self.x, self.y))
           print("Created Block")
       elif self.mode == 'SelectEnemy':
           testRect = Rect((self.rect.left, self.rect.top + GRIDSIZE),
                           (GRIDSIZE, GRIDSIZE))  # testRect: enemies can only be placed directly on ground
           if testRect.collidelist(BLOCKS) == -1:
               return
           GRID[getPosRaw(self.x, self.y)] = 2
           ENEMIES.append(Enemy(self.x, self.y))
           print("Created Enemy")


   def remove(self):
       if (self.isOnGrid == False):
           return
       MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
       MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2


       for blockI in range(0, len(BLOCKS)):
           BLokcX = ceil(BLOCKS[blockI].rect.center[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
           BLokcY = ceil(BLOCKS[blockI].rect.center[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2


           if BLokcX == MouseX and BLokcY == MouseY:
               GRID[getPosRaw(MouseX, MouseY)] = 0
               BLOCKS.pop(blockI)
               print("Removed Block")
               break




class Enemy(pygame.sprite.Sprite):
   def __init__(self, x, y):
       super().__init__()
       self.image = pygame.image.load("Green.png")
       self.rect = self.image.get_rect()
       self.rect.center = (x, y)
       self.velocityX = -2
       self.velocityY = 0
       self.terminalVelocityY = 15




   def draw(self, surface):
       surface.blit(self.image, self.rect)


   def move(self):
       self.rect.x += self.velocityX
       if self.colX() or self.fallX():
           self.velocityX = -self.velocityX  # reverse direction if collides with wall or about to fall


   #   self.rect.y += self.velocityY
   #   self.colY()
   #   if self.velocityY >= self.terminalVelocityY:
   #       self.velocityY = self.terminalVelocityY  # limit downward velocity to terminal velocity
   #   else:
   #       self.velocityY += 1


   def colX(self):
       for block in BLOCKS:  # check collision x-direction
           if self.rect.colliderect(block):
               if self.velocityX > 0:  # moving right
                   self.rect.right = block.rect.left
                   return True
               if self.velocityX < 0:  # moving left
                   self.rect.left = block.rect.right
                   return True


   #   def colY(self):
   #     if self.rect.collidelist(BLOCKS) != -1:
   #       self.rect.bottom = block.rect.top


   def fallX(self):  # check if Enemy is about to fall
       leftRect = Rect((self.rect.left - GRIDSIZE, self.rect.top + GRIDSIZE), (GRIDSIZE, GRIDSIZE))
       rightRect = Rect((self.rect.left + GRIDSIZE, self.rect.top + GRIDSIZE), (GRIDSIZE, GRIDSIZE))
       if leftRect.collidelist(BLOCKS) == -1:
           return True
       if rightRect.collidelist(BLOCKS) == -1:
           return True



   def update(self):
        if GAMESTATE != "GAMEPLAY":
            return
        self.move()




class AnimatedSprite(pygame.sprite.Sprite):
   def __init__(self, x, y):
       super().__init__()
       self.Y = y
       self.X = x


       self.UVX = 0
       self.UVY = 0
       self.UVWidth = 32
       self.UVHeight = 32


       self.imageSRC = pygame.image.load("Blue.png")
       self.image = self.imageSRC
       self.rect = self.image.get_rect()
       self.rect.center = (x,y)


       self.frameMax = 4
       self.frameCurrent = 0
       self.fps = 15
       self.fpsCurrent = 0


   def draw(self, surface):
       self.frameUpdate()
       surface.blit(self.image, self.rect)


   def update(self):


       if self.fpsCurrent == self.fps:
           self.fpsCurrent = 0
           self.frameNext()
       else:
           self.fpsCurrent += 1
       pass


   def frameNext(self):
       if self.frameCurrent == self.frameMax:
           self.frameCurrent = 0
       else:
           self.frameCurrent += 1


   def frameUpdate(self):
       imagePass1 = pygame.transform.chop(self.imageSRC, (0, self.UVHeight, 32 * self.frameCurrent, self.UVHeight))
       imagePass2 = pygame.transform.chop(imagePass1, (32, self.UVHeight, 160, self.UVHeight))
       self.image = imagePass2




class Button(pygame.sprite.Sprite):
   def __init__(self, x, y, img, id):
       super().__init__()
       self.image = pygame.image.load(img)
       self.rect = self.image.get_rect()
       self.rect.center = (x, y)
       self.ID = id


   def draw(self, surface):
       surface.blit(self.image, self.rect)
   def update(self):
       MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
       MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2


       if(self.rect.collidepoint(MouseX,MouseY)):
           handleButtons(self.ID)




def drawGrid():
   for x in range(0, GRIDX + 1):
       pygame.draw.line(displaysurface, "#000000", (GRIDSIZE * x, 0), (GRIDSIZE * x, GRIDY * GRIDSIZE))
   for y in range(0, GRIDY + 1):
       pygame.draw.line(displaysurface, "#000000", (0, GRIDSIZE * y), (GRIDX * GRIDSIZE, GRIDSIZE * y))




def drawObjects():  # LOAD OBJECTS FROM GRID
    TempX = -1
    TempY = 0
    TempPlayer = None
    TempFinal = None
    for x in range(0, len(GRID)):
        TempX = TempX + 1
        if TempX == GRIDX:
            TempX = 0
            TempY = TempY + 1
        if GRID[x] == 1:  # block case
            print(f"{TempX},{TempY}")
            BLOCKS.append(Block(TempX * GRIDSIZE + 16, TempY * GRIDSIZE + 16))
        if GRID[x] == 2:  # enemy case
            print(f"{TempX},{TempY}")
            ENEMIES.append(Enemy(TempX * GRIDSIZE + 16, TempY * GRIDSIZE + 16))
        if GRID[x] == 3: # player case
            TempPlayer = Player(TempX * GRIDSIZE + 16, TempY * GRIDSIZE + 16)
        if GRID[x] == 4: # final pos "goal square"
            TempFinal = Final(TempX * GRIDSIZE + 16, TempY * GRIDSIZE + 16)

    return (TempPlayer or Player(16,16)), (TempFinal or Final(48,16))
# return Player and Final objects




### LEVEL LOADER

def loader(filename="./levels/1"):
    file = open(filename, 'r')
    gridy = 0  # iterate over each line of level file
    grid_temp = []
    gridx = 1
    for line in file:
        if len(line) > gridx:
            gridx = len(line)
    # determine the value of gridx. iterate through each line and find max line length.
    file.close()

    file2 = open(filename, 'r')  # reopen the file
    for line in file2:
        for char_idx in range(len(line)):
            if line[char_idx] == ' ':
                grid_temp.append(0)
            if line[char_idx] == '#':
                grid_temp.append(1)
            if line[char_idx] == 'E':
                grid_temp.append(2)
            if line[char_idx] == 'P':
                grid_temp.append(3)
            if line[char_idx] == 'F':
                grid_temp.append(4)
        grid_temp.extend([0] * (gridx - len(line) + 1))
        gridy += 1  # the amount of lines is the value of GRIDY

    return grid_temp, gridx, gridy
###


GRID, GRIDX, GRIDY = loader()
HEIGHT = GRIDSIZE * GRIDY + 64
WIDTH = GRIDSIZE * GRIDX + 64
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.RESIZABLE, vsync=1)
pygame.display.set_caption("Game Thing")

P1, final = drawObjects()
P1 = Player(16, 16)
AN = AnimatedSprite(128, 32)
BUTTONS = [Button(GRIDX * GRIDSIZE + 16, 16, "Red.png", "SelectWall"),
           Button(GRIDX * GRIDSIZE + 16, 16 + 32, "Green.png", "SelectEnemy"),
           Button(GRIDX * GRIDSIZE + 16, 16 + 32*2, "Blue.png", "ToggleMode")]
cHair = Crosshair(32, 32)
clock = pygame.time.Clock()  # cap fps to 60


is_running = True
while is_running:
   for event in pygame.event.get():
       if event.type == QUIT:
           pygame.quit()
           exit()
       if event.type == KEYDOWN and event.key == K_ESCAPE:
           pygame.quit()
           exit()
       if event.type == KEYDOWN and event.key == K_p:
           print(GRID)
       if event.type == KEYDOWN and event.key == K_COMMA:
           COMMANDINPUT = input("COMMAND INPUT > ")
           OUTPUT = reCommand.search(COMMANDINPUT)
           if OUTPUT:
               handleCommand(OUTPUT.group(1),OUTPUT.group(2))


   if pygame.mouse.get_pressed()[0]:
       if(GAMESTATE == "EDITOR"):
           Crosshair.create(cHair)
       for bot in BUTTONS:
           bot.update()
   if pygame.mouse.get_pressed()[2]:
       if(GAMESTATE == "EDITOR"):
           Crosshair.remove(cHair)


   clock.tick(60)
   P1.update()
   AN.update()
   if(GAMESTATE == "EDITOR"):
       cHair.update()
   for block in BLOCKS:
       block.update()
   for enemy in ENEMIES:
       enemy.update()


   displaysurface.fill((255, 255, 255))
   P1.draw(displaysurface)
   AN.draw(displaysurface)
   if (GAMESTATE == "EDITOR"):
       cHair.draw(displaysurface)
   for bot in BUTTONS:
       bot.draw(displaysurface)
   for block in BLOCKS:
       block.draw(displaysurface)
   for enemy in ENEMIES:
       enemy.draw(displaysurface)
   final.draw(displaysurface)


   text_surface = my_font.render(f'{P1.rect.center}({P1.velocityX},{P1.velocityY})', False, (0, 0, 0))
   displaysurface.blit(text_surface, (0, GRIDY * GRIDSIZE))

   if GAMESTATE == "EDITOR": drawGrid()

   if P1.rect.colliderect(final.rect):  # if player reaches goal position
       GRID, GRIDX, GRIDY = loader('./levels/2')
       print(GRIDX)

       HEIGHT = GRIDSIZE * GRIDY + 64
       WIDTH = GRIDSIZE * GRIDX + 32

       displaysurface = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.RESIZABLE, vsync=1)
       BLOCKS = []
       ENEMIES = []
       P1, final = drawObjects()
       BUTTONS = [Button(GRIDX * GRIDSIZE + 16, 16, "Red.png", "SelectWall"),
                  Button(GRIDX * GRIDSIZE + 16, 16 + 32, "Green.png", "SelectEnemy"),
                  Button(GRIDX * GRIDSIZE + 16, 16 + 32 * 2, "Blue.png", "ToggleMode")]

   if P1.rect.collidelist(ENEMIES) != -1:
       P1.rect.center = P1.spawn
       P1.update()

   pygame.display.update()

