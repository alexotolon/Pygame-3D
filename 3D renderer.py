import pygame
from pygame.math import Vector2 as vec2
from pygame.math import Vector3 as vec3
import math
import sys
import numpy as np
import random

# Initialize Pygame
pygame.init()
SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN.get_size()
pygame.display.set_caption("3D")

pygame.mixer.init() # no sound for now

CLOCK = pygame.time.Clock()
FPS = 60

class Camera:
    def __init__(self, pos, horizAngle, vertAngle):
        self.pos = pos
        self.horizAngle = horizAngle
        self.vertAngle = vertAngle
        self.horizFOV = 1
        self.vertFOV = self.horizFOV * SCREEN_HEIGHT / SCREEN_WIDTH # to avoid distortion
    def projectPoint(self, point):
        intermediary = (point - self.pos)
        angle = math.atan2(intermediary[0], intermediary[1]) + self.horizAngle
        relative = vec3(intermediary.length() * math.cos(angle), intermediary.length() * math.sin(angle), intermediary.length() * math.cos(math.atan2(vec2(intermediary[0], intermediary[1]).length(), intermediary[2]) + self.vertAngle))
        return vec2(math.atan2(relative[1], relative[0]) * SCREEN_WIDTH / self.horizFOV  + SCREEN_WIDTH / 2, math.atan2(relative[2], relative[0]) * SCREEN_HEIGHT / self.vertFOV  + SCREEN_HEIGHT / 2 + math.sin(self.vertAngle))



class Triangle:
    def __init__(self, point1, point2, point3, color = "undefined", region = ""): # Please put a color, undefined is only for triangles constructed on the fly
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.centerPoint = ((self.point1) + (self.point2) + (self.point3)) / 3
        self.area = (vec3.cross((self.point1 - self.point2), (self.point1 - self.point3))).length() / 2
        self.color = color
        self.region = region
        self.horizslope = math.atan2((max(self.point1[0], self.point2[0], self.point3[0]) - min(self.point1[0], self.point2[0], self.point3[0])), (max(self.point1[1], self.point2[1], self.point3[1]) - min(self.point1[1], self.point2[1], self.point3[1])))
        self.vertslope = 1#math.atan2((self.centerPoint - self.point1[2]), (max(self.point1[1], self.point2[1], self.point3[1]) - min(self.point1[1], self.point2[1], self.point3[1])))
    def calcColision(self, cam):
        feet = vec3(cam.pos[0], cam.pos[1], cam.pos[2] + playerHeight) # a larger z value is lower
        if (not noclip) and feet[2] > max(self.point1[2], self.point2[2], self.point3[2]):
            if abs(self.area / (Triangle(feet, self.point2, self.point3, self.color).area + Triangle(self.point1, feet, self.point3, self.color).area + Triangle(self.point1, self.point2, feet, self.color).area)) < 1: # To avoid floating point imprecision
                return True
    def drawAndHitscan(self, cam): 
        drawList = [cam.projectPoint(self.point1),  cam.projectPoint(self.point2), cam.projectPoint(self.point3), cam.projectPoint(self.centerPoint)]
        intermediary = []
        for p in range(3):
            intermediary.append(vec3(drawList[p][0], drawList[p][1], 0))

        if abs(Triangle(intermediary[0], intermediary[1], intermediary[2]).area / (Triangle(vec3(0, 0, 0), intermediary[1], intermediary[2]).area + Triangle(intermediary[0], vec3(0, 0, 0), intermediary[2]).area + Triangle(intermediary[0], intermediary[0], vec3(0, 0, 0)).area)) < .00001:
           return self
        
        seen = False
        for p in drawList:
            if 0 < p[0] < SCREEN_WIDTH and 0 < p[1] < SCREEN_HEIGHT:
                seen = True
        if seen:
            drawList.pop()
            pygame.draw.polygon(SCREEN,self.color,drawList)

def LoadTeapot():
    global Triangles
    with open("C:/programming/Pygame-3D/teapot-mesh.txt", 'r') as file:
        lines = file.readlines()
    
    # start index at 1 not 0 so as to skip the first line which contains the # of triangles
    index = 1
    while index < len(lines):
        try:
            v1 = list(map(float, lines[index].strip().split()))
            v2 = list(map(float, lines[index + 1].strip().split()))
            v3 = list(map(float, lines[index + 2].strip().split()))
            
            vertex1 = vec3(v1) + vec3(0, 0, -50)
            vertex2 = vec3(v2) + vec3(0, 0, -50)
            vertex3 = vec3(v3) + vec3(0, 0, -50)
            
            Triangles.append(Triangle(vertex1, vertex2, vertex3, (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))))
            
            index += 4  # 4 because there's a blank line after each triple
        except (ValueError, IndexError):
            print("Something went wrong.")
            break

def leppard():
    pass

playerCamera = Camera(vec3(0, 0, 0), 0, 0)
playerWidth = 5
playerHeight = 10
playerRegion = ""

noclip = True
jumpVelocity = 0
onGround = False
Triangles = []
LoadTeapot()
Triangles.append(Triangle(vec3(30, 15, 0), vec3(40, 15, -20), vec3(40, -5, 0), (255, 0, 0)))
Triangles.append(Triangle(vec3(20, 0, 10), vec3(20, -math.sqrt(200/3), -math.sqrt(100/3)), vec3(20, math.sqrt(200/3), -math.sqrt(100/3)), (0, 0, 0)))
Triangles.append(Triangle(vec3(0, 30, 5), vec3(-15, 30, -8), vec3(10, 30, -15), (0, 255, 0)))
Triangles.append(Triangle(vec3(0, -30, 5), vec3(-15, -30, -8), vec3(10, -30, -15), (0, 0, 255)))
Triangles.append(Triangle(vec3(10, 10, 30), vec3(0, -10, 30), vec3(-10, 0, 30), (255, 255, 0)))



running = True
pygame.mouse.set_visible(False)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            playerCamera.horizAngle -= (pygame.mouse.get_pos()[0] - SCREEN_WIDTH / 2) * math.pi / 4 * playerCamera.horizFOV / SCREEN_WIDTH
            playerCamera.vertAngle += (pygame.mouse.get_pos()[1] - SCREEN_HEIGHT / 2) * math.pi / 4 * playerCamera.vertFOV / SCREEN_HEIGHT
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                noclip = not noclip

    pygame.mouse.set_pos(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    SCREEN.fill((255, 255, 255))
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        playerCamera.pos[0] += math.cos(playerCamera.horizAngle + math.pi / 2) * math.cos(playerCamera.vertAngle)
        playerCamera.pos[1] += math.sin(playerCamera.horizAngle + math.pi / 2) * math.cos(playerCamera.vertAngle)
        if noclip:
            playerCamera.pos[2] += math.sin(playerCamera.vertAngle)
    if keys[pygame.K_s]:
        playerCamera.pos[0] -= math.cos(playerCamera.horizAngle + math.pi / 2) * math.cos(playerCamera.vertAngle)
        playerCamera.pos[1] -= math.sin(playerCamera.horizAngle + math.pi / 2) * math.cos(playerCamera.vertAngle)
        if noclip:
            playerCamera.pos[2] -= math.sin(playerCamera.vertAngle)
    if keys[pygame.K_a]:
        playerCamera.pos[0] -= math.cos(playerCamera.horizAngle)
        playerCamera.pos[1] -= math.sin(playerCamera.horizAngle)
    if keys[pygame.K_d]:
        playerCamera.pos[0] += math.cos(playerCamera.horizAngle)
        playerCamera.pos[1] += math.sin(playerCamera.horizAngle)
    if noclip:
        if keys[pygame.K_q]: # a smaller z value is higher
            playerCamera.pos[0] += math.cos(playerCamera.horizAngle + math.pi / 2) * math.sin(playerCamera.vertAngle)
            playerCamera.pos[1] -= math.sin(playerCamera.horizAngle + math.pi / 2) * math.sin(playerCamera.vertAngle)
            playerCamera.pos[2] -= math.cos(playerCamera.vertAngle)
        if keys[pygame.K_e]: # a larger z value is lower
            playerCamera.pos[0] -= math.cos(playerCamera.horizAngle + math.pi / 2) * math.sin(playerCamera.vertAngle)
            playerCamera.pos[1] += math.sin(playerCamera.horizAngle + math.pi / 2) * math.sin(playerCamera.vertAngle)
            playerCamera.pos[2] += math.cos(playerCamera.vertAngle)
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
        playerCamera.pos[2] -= jumpVelocity # a smaller z value is higher

    Triangles.sort(key = lambda Triangle: (Triangle.centerPoint - playerCamera.pos).length(), reverse = True)
    hitTriangle =  None
    for t in Triangles:
        hitTriangle = t.drawAndHitscan(playerCamera)

        hasCollided = False
        if t.calcColision(playerCamera):
            onGround =  True
            hasCollided = True
        if not hasCollided:
            onGround = False

    pygame.display.flip()
    CLOCK.tick(FPS)
    if hitTriangle != None:
        print(hitTriangle.color)
    
pygame.quit()
sys.exit()