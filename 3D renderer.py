import pygame
import math
import sys
import numpy as np

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screenWidth, screenHeight = screen.get_size()
pygame.display.set_caption("3D")

pygame.mixer.init() # no sound for now

clock = pygame.time.Clock()
FPS = 60

def drawPoint(point):
    intermediary = (point - playerPos)
    angle = math.atan2(intermediary[0], intermediary[1]) + horizAngle
    relative = pygame.math.Vector3(intermediary.length() * math.cos(angle), intermediary.length() * math.sin(angle), intermediary.length() * math.cos(math.atan2(pygame.math.Vector2(intermediary[0], intermediary[1]).length(), intermediary[2]) + vertAngle))
    return pygame.math.Vector2(math.atan2(relative[1], relative[0]) * screenWidth / horizFOV  + screenWidth / 2, math.atan2(relative[2], relative[0]) * screenHeight / vertFOV  + screenHeight / 2 + math.sin(vertAngle))
def leppard():
    pass



class Triangle:
    def __init__(self, point1, point2, point3, color, region = ""):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.color = color
        self.region = region
    def calcColision(self):
        feet = pygame.math.Vector3(playerPos[0], playerPos[1], playerPos[2] + playerHeight) # a larger z value is lower
        if (not noclip) and feet[2] > max(self.point1[2], self.point2[2], self.point3[2]):
            if abs(self.area() / (Triangle(feet, self.point2, self.point3, self.color).area() + Triangle(self.point1, feet, self.point3, self.color).area() + Triangle(self.point1, self.point2, feet, self.color).area())) < 1: # To avoid floating point imprecision
                return True
    def calcCenterPointLen(self):
        return ((self.point1 - playerPos).length() + (self.point2 - playerPos).length() + (self.point3 - playerPos).length()) / 3
    def area(self):
        return (pygame.math.Vector3.cross((self.point1 - self.point2), (self.point1 - self.point3))).length() / 2
    def draw(self, screen): 
        drawList = [drawPoint(self.point1),  drawPoint(self.point2), drawPoint(self.point3)]
        vertexSeen = False
        for p in drawList:
            if 0 < p[0] < screenWidth and 0 < p[1] < screenHeight:
                vertexSeen = True
        if vertexSeen or 0 < sum(drawList, pygame.math.Vector2(0, 0))[0] / 3 < screenWidth and 0 < sum(drawList, pygame.math.Vector2(0, 0))[1] / 3 < screenHeight:
            pygame.draw.polygon(screen,self.color,drawList)

horizFOV = 1
vertFOV = horizFOV * screenHeight / screenWidth # to avoid distortion

playerPos = pygame.math.Vector3(0, 0, 0)
playerWidth = 5
playerHeight = 10
playerRegion = ""

noclip = True
jumpVelocity = 0
onGround = False

horizAngle = 0
vertAngle = 0

Triangles = []
Triangles.append(Triangle(pygame.math.Vector3(30, 15, 0), pygame.math.Vector3(40, 15, -20), pygame.math.Vector3(40, -5, 0), (255, 0, 0)))
Triangles.append(Triangle(pygame.math.Vector3(20, 0, 10), pygame.math.Vector3(20, -math.sqrt(200/3), -math.sqrt(100/3)), pygame.math.Vector3(20, math.sqrt(200/3), -math.sqrt(100/3)), (0, 0, 0)))
Triangles.append(Triangle(pygame.math.Vector3(0, 30, 5), pygame.math.Vector3(-15, 30, -8), pygame.math.Vector3(10, 30, -15), (0, 255, 0)))
Triangles.append(Triangle(pygame.math.Vector3(0, -30, 5), pygame.math.Vector3(-15, -30, -8), pygame.math.Vector3(10, -30, -15), (0, 0, 255)))
Triangles.append(Triangle(pygame.math.Vector3(10, 10, 30),pygame.math.Vector3(0, -10, 30),pygame.math.Vector3(-10, 0, 30), (255, 255, 0)))

running = True
pygame.mouse.set_visible(False)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            horizAngle -= (pygame.mouse.get_pos()[0] - screenWidth / 2) * math.pi / 4 * horizFOV / screenWidth
            vertAngle += (pygame.mouse.get_pos()[1] - screenHeight / 2) * math.pi / 4 * vertFOV / screenHeight
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                noclip = not noclip


    screen.fill((255, 255, 255))
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        playerPos[0] += math.cos(horizAngle + math.pi / 2) * math.cos(vertAngle)
        playerPos[1] += math.sin(horizAngle + math.pi / 2) * math.cos(vertAngle)
        if noclip:
            playerPos[2] += math.sin(vertAngle)
    if keys[pygame.K_s]:
        playerPos[0] -= math.cos(horizAngle + math.pi / 2) * math.cos(vertAngle)
        playerPos[1] -= math.sin(horizAngle + math.pi / 2) * math.cos(vertAngle)
        if noclip:
            playerPos[2] -= math.sin(vertAngle)
    if keys[pygame.K_a]:
        playerPos[0] -= math.cos(horizAngle)
        playerPos[1] -= math.sin(horizAngle)
    if keys[pygame.K_d]:
        playerPos[0] += math.cos(horizAngle)
        playerPos[1] += math.sin(horizAngle)
    if noclip:
        if keys[pygame.K_q]: # a smaller z value is higher
            playerPos[0] += math.cos(horizAngle + math.pi / 2) * math.sin(vertAngle)
            playerPos[1] -= math.sin(horizAngle + math.pi / 2) * math.sin(vertAngle)
            playerPos[2] -= math.cos(vertAngle)
        if keys[pygame.K_e]: # a larger z value is lower
            playerPos[0] -= math.cos(horizAngle + math.pi / 2) * math.sin(vertAngle)
            playerPos[1] += math.sin(horizAngle + math.pi / 2) * math.sin(vertAngle)
            playerPos[2] += math.cos(vertAngle)
    else:
        if keys[pygame.K_SPACE]:
            jumpVelocity = 5
    if keys[pygame.K_ESCAPE]:
        running = False
    if not noclip:
        if not onGround:
            jumpVelocity -= 1
        else:
            jumpVelocity = 0
        playerPos[2] -= jumpVelocity # a smaller z value is higher

    Triangles.sort(key = lambda Triangle: Triangle.calcCenterPointLen(), reverse = True)
    for t in Triangles:
        t.draw(screen)
        hasCollided = False
        if t.calcColision():
            onGround =  True
            hasCollided = True
        if not hasCollided:
            onGround = False

    pygame.mouse.set_pos(screenWidth / 2, screenHeight / 2)

    pygame.display.flip()
    clock.tick(FPS)
    #print(onGround)
    
pygame.quit()
sys.exit()