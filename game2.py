from math import floor
from math import ceil
import re

import pygame
from pygame.locals import *

pygame.init()

GRIDSIZE = 32
GRIDX = 12
GRIDY = 12
# screen height/width
GAMESTATE = "EDITOR" # either 'EDITOR' or 'GAMEPLAY', determines mode of game

GRID = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,
    0, 0, 0, 3, 0, 0, 0, 0, 2, 0, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]


# GRID DEFINES LEVEL LAYOUT:
# 0 = AIR
# 1 = BLOCK
# 2 = ENEMY (initial position)
# 3 = Player spawn


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


def ClampI(val, min, max):
    if (val > max):
        return max
    elif (val < min):
        return min
    else:
        return val


def isClampI(val, min, max):
    if (val > max):
        return True
    elif (val < min):
        return True
    else:
        return False


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Blue.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.spawn = (x,y)
        self.velocityX = 0
        self.velocityY = 0
        self.terminalVelocityY = 15  # terminal falling velocity of Player
        self.on_floor = False  # is Player currently on floor? used to prevent air-jumping

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def colX(self):
        for block in BLOCKS:  # check collision x-direction
            if self.rect.colliderect(block):
                if self.velocityX > 0:  # moving right
                    self.rect.right = block.rect.left
                if self.velocityX < 0:  # moving left
                    self.rect.left = block.rect.right

    def colY(self):
        is_colliding = False
        for block in BLOCKS:  # check collision y-direction
            if self.rect.colliderect(block):
                is_colliding = True
                if self.velocityY > 0:  # moving down, on ground, has stopped jumping
                    self.rect.bottom = block.rect.top
                    self.velocityY = 0
                    self.on_floor = True
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
        self.x = ClampI(MouseX, 16, GRIDX * GRIDSIZE - 16)
        self.y = ClampI(MouseY, 16, GRIDY * GRIDSIZE - 16)

        self.rect.center = (self.x, self.y)
        if (isClampI(MouseX, 16, GRIDX * GRIDSIZE - 16) or isClampI(MouseY, 16, GRIDY * GRIDSIZE - 16)):
            self.isOnGrid = False
        else:
            self.isOnGrid = True

    def create(self):
        if not self.isOnGrid:
            return
        MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
        MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2

        posit = getPosStatRaw(self.x, self.y)
        if posit != 0: return

        if self.mode == 'SelectWall':
            GRID[getPosRaw(self.x, self.y)] = 1
            BLOCKS.append(Block(self.x, self.y))
            print("Created Block")
        elif self.mode == 'SelectEnemy':
            GRID[getPosRaw(self.x, self.y)] = 2
            ENEMIES.append(Enemy(self.x,self.y))
            print("Created Enemy")


    def remove(self):
            if (self.isOnGrid == False):
                return
            MouseX = ceil(pygame.mouse.get_pos()[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
            MouseY = ceil(pygame.mouse.get_pos()[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2

            if self.mode == 'SelectWall': # in wall building mode
                for blockI in range(0, len(BLOCKS)):
                    BLokcX = ceil(BLOCKS[blockI].rect.center[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
                    BLokcY = ceil(BLOCKS[blockI].rect.center[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2

                    if BLokcX == MouseX and BLokcY == MouseY:
                        GRID[getPosRaw(MouseX, MouseY)] = 0
                        BLOCKS.pop(blockI)
                        print("Removed Block")
                        break

            elif self.mode == 'SelectEnemy': # in enemy building mode
                for blockI in range(len(ENEMIES)):
                    BLokcX = ceil(ENEMIES[blockI].rect.center[0] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2
                    BLokcY = ceil(ENEMIES[blockI].rect.center[1] / GRIDSIZE) * GRIDSIZE - GRIDSIZE / 2

                    if BLokcX == MouseX and BLokcY == MouseY:
                        GRID[getPosRaw(MouseX, MouseY)] = 0
                        ENEMIES.pop(blockI)
                        print("Removed Enemy")
                        break



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Green.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.spawn = (x, y)
        self.velocityX = -2
        self.velocityY = 0
        self.terminalVelocityY = 15

    def draw(self, surface):
        if GAMESTATE == 'EDITOR':
            self.rect.center = self.spawn
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

        if (self.rect.collidepoint(MouseX, MouseY)):
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

### command line tools
def handleCommand(var1,var2):
   global GAMESTATE
   print(f"Command {var1} with {var2}")
   var1 = var1.lower()
   if var1 == "state":
       GAMESTATE = str(var2.upper())
       print(f"state set to {var2.upper()}")
   elif var1 == "print":
       print(var2)
   elif var1 == "respawn":
       P1.rect.center = P1.spawn
       P1.update()
       print("done")
reCommand = re.compile(r'/(\w+) (\w*)') # regex object to handle commands `/command [args]`
###

GRID, GRIDX, GRIDY = loader()
print(GRIDX)

HEIGHT = GRIDSIZE * GRIDY + 64
WIDTH = GRIDSIZE * GRIDX + 32

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.RESIZABLE, vsync=1)
pygame.display.set_caption("Game Thing")

P1, final = drawObjects()

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
        if event.type == MOUSEBUTTONUP and event.button == 1: # left click
            for button in BUTTONS:
                button.update()
        if event.type == KEYDOWN and event.key == K_COMMA:
            COMMANDINPUT = input("COMMAND INPUT > ")
            OUTPUT = reCommand.search(COMMANDINPUT)
            if OUTPUT:
                handleCommand(OUTPUT.group(1), OUTPUT.group(2) or "")

    if pygame.mouse.get_pressed()[2]: # right mouse down
        cHair.remove()
    if pygame.mouse.get_pressed()[0]: # left mouse down
        cHair.create()

    clock.tick(60)
    P1.update()
    cHair.update()
    for block in BLOCKS:
        block.update()
    for enemy in ENEMIES:
         enemy.update()

    displaysurface.fill((255, 255, 255))
    P1.draw(displaysurface)
    cHair.draw(displaysurface)
    final.draw(displaysurface)
    for button in BUTTONS:
        button.draw(displaysurface)
    for block in BLOCKS:
        block.draw(displaysurface)
    for enemy in ENEMIES:
        enemy.draw(displaysurface)

    drawGrid()
    pygame.display.update()

