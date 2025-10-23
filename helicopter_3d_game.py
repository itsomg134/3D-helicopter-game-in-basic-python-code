import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

class Helicopter:
    def __init__(self):
        self.x = 0
        self.y = 5
        self.z = -20
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0
        self.velocity_y = 0
        self.velocity_x = 0
        self.velocity_z = 0
        self.rotor_angle = 0
        self.health = 100
        
    def update(self, keys):
        # Rotor rotation
        self.rotor_angle += 20
        if self.rotor_angle >= 360:
            self.rotor_angle = 0
        
        # Gravity
        self.velocity_y -= 0.02
        
        # Controls
        if keys[K_SPACE]:  # Ascend
            self.velocity_y += 0.08
        if keys[K_w]:  # Forward
            self.velocity_z += 0.05
            self.rot_x = max(-15, self.rot_x - 1)
        else:
            if self.rot_x < 0:
                self.rot_x += 0.5
        if keys[K_s]:  # Backward
            self.velocity_z -= 0.05
            self.rot_x = min(15, self.rot_x + 1)
        else:
            if self.rot_x > 0:
                self.rot_x -= 0.5
        if keys[K_a]:  # Left
            self.velocity_x += 0.05
            self.rot_z = min(15, self.rot_z + 1)
        else:
            if self.rot_z > 0:
                self.rot_z -= 0.5
        if keys[K_d]:  # Right
            self.velocity_x -= 0.05
            self.rot_z = max(-15, self.rot_z - 1)
        else:
            if self.rot_z < 0:
                self.rot_z += 0.5
        
        # Apply drag
        self.velocity_x *= 0.95
        self.velocity_z *= 0.95
        self.velocity_y *= 0.98
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.z += self.velocity_z
        
        # Keep helicopter above ground
        if self.y < 1:
            self.y = 1
            self.velocity_y = 0
            self.health -= 1
        
        # Boundaries
        if abs(self.x) > 50:
            self.x = 50 * (1 if self.x > 0 else -1)
            self.velocity_x = 0
        if self.z > 10:
            self.z = 10
            self.velocity_z = 0
        if self.z < -100:
            self.z = -100
            self.velocity_z = 0
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rot_y, 0, 1, 0)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_z, 0, 0, 1)
        
        # Body
        glColor3f(0.2, 0.6, 0.3)
        glPushMatrix()
        glScalef(2, 0.8, 1)
        draw_cube()
        glPopMatrix()
        
        # Cockpit
        glColor3f(0.3, 0.7, 0.9)
        glPushMatrix()
        glTranslatef(0.8, 0.3, 0)
        glScalef(0.8, 0.6, 0.8)
        draw_cube()
        glPopMatrix()
        
        # Tail
        glColor3f(0.2, 0.6, 0.3)
        glPushMatrix()
        glTranslatef(-2, 0.3, 0)
        glScalef(1.5, 0.3, 0.3)
        draw_cube()
        glPopMatrix()
        
        # Main rotor
        glColor3f(0.4, 0.4, 0.4)
        glPushMatrix()
        glTranslatef(0, 1, 0)
        glRotatef(self.rotor_angle, 0, 1, 0)
        glScalef(4, 0.05, 0.2)
        draw_cube()
        glPopMatrix()
        
        # Tail rotor
        glPushMatrix()
        glTranslatef(-3.2, 0.3, 0)
        glRotatef(self.rotor_angle * 2, 1, 0, 0)
        glScalef(0.05, 0.8, 0.15)
        draw_cube()
        glPopMatrix()
        
        # Skids
        glColor3f(0.3, 0.3, 0.3)
        for side in [-0.5, 0.5]:
            glPushMatrix()
            glTranslatef(0, -0.7, side)
            glScalef(2, 0.1, 0.1)
            draw_cube()
            glPopMatrix()
        
        glPopMatrix()

class Obstacle:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.size = random.uniform(2, 4)
        self.color = (random.uniform(0.5, 0.9), random.uniform(0.3, 0.5), random.uniform(0.2, 0.4))
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(*self.color)
        glScalef(self.size, self.size * 2, self.size)
        draw_cube()
        glPopMatrix()
    
    def check_collision(self, heli):
        dist = math.sqrt((self.x - heli.x)**2 + (self.y - heli.y)**2 + (self.z - heli.z)**2)
        return dist < (self.size + 1.5)

class Collectible:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.angle = 0
        self.collected = False
        
    def update(self):
        self.angle += 3
        if self.angle >= 360:
            self.angle = 0
    
    def draw(self):
        if not self.collected:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            glRotatef(self.angle, 0, 1, 0)
            glColor3f(1.0, 0.85, 0.0)
            glScalef(0.5, 0.5, 0.5)
            draw_cube()
            glPopMatrix()
    
    def check_collection(self, heli):
        if not self.collected:
            dist = math.sqrt((self.x - heli.x)**2 + (self.y - heli.y)**2 + (self.z - heli.z)**2)
            if dist < 2:
                self.collected = True
                return True
        return False

def draw_cube():
    vertices = [
        [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
        [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]
    ]
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
        [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]
    ]
    
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_ground():
    glColor3f(0.3, 0.5, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-100, 0, -100)
    glVertex3f(100, 0, -100)
    glVertex3f(100, 0, 100)
    glVertex3f(-100, 0, 100)
    glEnd()
    
    # Grid lines
    glColor3f(0.2, 0.4, 0.2)
    glBegin(GL_LINES)
    for i in range(-100, 101, 10):
        glVertex3f(i, 0.01, -100)
        glVertex3f(i, 0.01, 100)
        glVertex3f(-100, 0.01, i)
        glVertex3f(100, 0.01, i)
    glEnd()

def draw_text(x, y, text):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Helicopter Game")
    clock = pygame.time.Clock()
    
    # OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Game objects
    helicopter = Helicopter()
    obstacles = [Obstacle(random.uniform(-40, 40), random.uniform(2, 15), random.uniform(-80, -20)) for _ in range(15)]
    collectibles = [Collectible(random.uniform(-40, 40), random.uniform(3, 15), random.uniform(-80, -20)) for _ in range(10)]
    
    score = 0
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            if game_over and event.type == KEYDOWN and event.key == K_r:
                # Restart
                helicopter = Helicopter()
                obstacles = [Obstacle(random.uniform(-40, 40), random.uniform(2, 15), random.uniform(-80, -20)) for _ in range(15)]
                collectibles = [Collectible(random.uniform(-40, 40), random.uniform(3, 15), random.uniform(-80, -20)) for _ in range(10)]
                score = 0
                game_over = False
        
        keys = pygame.key.get_pressed()
        
        if not game_over:
            helicopter.update(keys)
            
            # Update collectibles
            for col in collectibles:
                col.update()
                if col.check_collection(helicopter):
                    score += 10
            
            # Check collisions
            for obs in obstacles:
                if obs.check_collision(helicopter):
                    helicopter.health -= 2
            
            if helicopter.health <= 0:
                game_over = True
        
        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera follows helicopter
        gluLookAt(
            helicopter.x - 8, helicopter.y + 5, helicopter.z + 12,
            helicopter.x, helicopter.y, helicopter.z,
            0, 1, 0
        )
        
        draw_ground()
        helicopter.draw()
        
        for obs in obstacles:
            obs.draw()
        
        for col in collectibles:
            col.draw()
        
        # Switch to 2D for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        # Draw HUD
        draw_text(10, SCREEN_HEIGHT - 40, f"Score: {score}")
        draw_text(10, SCREEN_HEIGHT - 80, f"Health: {int(helicopter.health)}")
        draw_text(10, 40, "SPACE: Up | W/S: Forward/Back | A/D: Left/Right")
        
        if game_over:
            draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, "GAME OVER!")
            draw_text(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 40, "Press R to Restart")
        
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
