import pygame
from random import randint
pygame.init()

Width = 1280
Height = 720
FPS = 60
SIZE = 50

fontBig = pygame.font.Font(None, 70)
fontUI = pygame.font.Font(None, 30)
fontTitle = pygame.font.Font(None, 140)

imgBg = pygame.image.load('img/bg.png')
imgTank = [
    pygame.image.load('img/PZII.png'),
    pygame.image.load('img/VK30.01H.png'),
    pygame.image.load('img/TIGER_P.png'),
    pygame.image.load('img/MAUS1.png')
]
imgArmor = pygame.image.load('img/block_armor.png')
imgBonuses = [
    pygame.image.load('img/bonus_star.png'),
    pygame.image.load('img/bonus_tank.png'),
]

sndShot = pygame.mixer.Sound('sounds/shot.mp3')
sndDead = pygame.mixer.Sound('sounds/dead.mp3')
sndLife = pygame.mixer.Sound('sounds/life.mp3')
sndStar = pygame.mixer.Sound('sounds/star.mp3')
sndEnd = pygame.mixer.Sound('sounds/end.mp3')
pygame.mixer.music.load('sounds/main.mp3')
pygame.mixer.music.play()

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

SPEED = [2, 2, 3, 1.5]
PROJECTILE_SPEED = [3, 3, 4, 7]
PROJECTILE_DAMAGE = [1, 2, 3, 4]
SHOT_DELAY = [40, 45, 50, 60]

pygame.display.set_caption('Танчики')
pygame.display.set_icon(pygame.image.load('img/MAUS1.png'))

window = pygame.display.set_mode((Width, Height))
clock = pygame.time.Clock()

class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'

        self.color = color
        self.rect = pygame.Rect(px, py, SIZE, SIZE)
        self.direct = direct
        self.speed = 2
        self.hp = 5

        self.shotTimer = 0
        self.shotDelay = 60
        self.projectileDamage = 1
        self.projectileSpeed = 5

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTank[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)
    def update(self):
        self.image = pygame.transform.rotate(imgTank[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 15, self.image.get_height() - 15))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.speed = SPEED[self.rank]
        self.projectileDamage = PROJECTILE_DAMAGE[self.rank]
        self.projectileSpeed = PROJECTILE_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]

        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT]:
            self.rect.x -= self.speed
            self.direct = 3
        elif keys[self.keyRIGHT]:
            self.rect.x += self.speed
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y -= self.speed
            self.direct = 0
        elif keys[self.keyDOWN]:
            self.rect.y += self.speed
            self.direct = 2
        if keys[self.keySHOT] and self.shotTimer == 0:
            dx = DIRECTS[self.direct][0] * self.projectileSpeed
            dy = DIRECTS[self.direct][1] * self.projectileSpeed
            Projectile(self, self.rect.centerx, self.rect.centery, dx, dy, self.projectileDamage)
            self.shotTimer = self.shotDelay

        if self.shotTimer > 0: self.shotTimer -= 1

        for obj in objects:
            if obj != self and obj.type == 'block':
                if self.rect.colliderect(obj):
                    self.rect.topleft = oldX, oldY
    def draw(self):
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            sndDead.play()
            sndEnd.play()
            objects.remove(self)
            print(self.color, ', you are dead')
class Projectile:
    def __init__(self, owner, px, py, dx, dy, damage):
        projectiles.append(self)
        self.owner = owner
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage

        sndShot.play()
    def update(self):
        self.px += self.dx
        self.py += self.dy

        if self.px < 0 or self.px > Width or self.py < 0 or self.py > Height:
            projectiles.remove(self)
        else:
            for obj in objects:
                if obj != self.owner and obj.type != 'bonus':
                    if obj.rect.collidepoint(self.px, self.py):
                        obj.damage(self.damage)
                        projectiles.remove(self)
                        break
    def draw(self):
        pygame.draw.circle(window, 'white', (self.px, self.py), 2)

class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 3
    def update(self):
        pass
    def draw(self):
        window.blit(imgArmor, self.rect)
    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            sndDead.play()


class Bonus:
    def __init__(self, px, py, bonusNum):
        objects.append(self)
        self.type = 'bonus'

        self.px, self.py = px, py
        self.bonusNum = bonusNum
        self.timer = 600

        self.image = imgBonuses[self.bonusNum]
        self.rect = self.image.get_rect(center=(self.px, self.py))

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTank) - 1:
                        obj.rank += 1
                        sndStar.play()
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    sndLife.play()
                    objects.remove(self)
                    break

    def draw(self):
        if self.timer % 30 < 15:
            window.blit(self.image, self.rect)

projectiles = []
objects = []

tank1 = Tank('blue', 50, 50, 1, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
tank2 = Tank('red', 700, 300, 3, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN))


for _ in range(100):
    while True:
        x = randint(0, Width // SIZE - 1) * SIZE
        y = randint(1, Height // SIZE - 1) * SIZE
        rect = pygame.Rect(x, y, SIZE, SIZE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect):
                fined = True
        if not fined:
            break
    Block(x, y, SIZE)

bonusTimer = 180
timer = 0
y = 0

play = True
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

    keys = pygame.key.get_pressed()
    timer += 1

    if bonusTimer > 0: bonusTimer -= 1
    else:
        Bonus(randint(50, Width - 50), randint(50, Height - 50), randint(0, len(imgBonuses) - 1))
        bonusTimer = randint(120, 240)

    for projectile in projectiles: projectile.update()
    for obj in objects: obj.update()

    window.blit(imgBg, (0, 0))
    for projectile in projectiles: projectile.draw()
    for obj in objects: obj.draw()

    i = 0
    for obj in objects:
        if obj.type == 'tank':
            pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))

            text = fontUI.render(str(obj.rank), 1, 'black')
            rect = text.get_rect(center=(5 + i * 70 + 11, 5 + 11))
            window.blit(text, rect)

            text = fontUI.render(str(obj.hp), 1, obj.color)
            rect = text.get_rect(center=(5 + i * 70 + SIZE, 5 + 11))
            window.blit(text, rect)
            i += 1

    t = 0
    for obj in objects:
        if obj.type == 'tank':
            t += 1
            tankWin = obj
    if timer < 260:
        y += 4
        pygame.draw.rect(window, 'black', (Width // 2 - 350, Height // 2 - 200 + y, 700, 250))
        pygame.draw.rect(window, 'purple', (Width // 2 - 350, Height // 2 - 200 + y, 703, 250), 3)
        text = fontTitle.render('Т А Н Ч И К И', 1, 'white')
        rect = text.get_rect(center=(Width // 2, Height // 2 - 100 + y))
        window.blit(text, rect)
        text = fontBig.render('ОДИН НА ОДИН', 1, 'white')
        rect = text.get_rect(center=(Width // 2, Height // 2 - 20 + y))
        window.blit(text, rect)

    if t == 1:
        text = fontBig.render('Переміг', 1, 'black')
        rect = text.get_rect(center=(Width // 2, Height // 2 - 100))
        window.blit(text, rect)
        pygame.mixer.music.stop()
        pygame.draw.rect(window, tankWin.color, (Width // 2 - 100, Height // 2, 200, 200))
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()