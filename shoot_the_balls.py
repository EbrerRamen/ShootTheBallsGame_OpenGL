from OpenGL.GL import *
from OpenGL.GLUT import *
import random

w_height = 800
w_width = 600

# Game variables
playing = True
game_over = False
score = 0
shooter_x = w_width / 2
shooter_y = 25
shooter_r = 20
bullet_r = 9
bullet_speed = 5
bullets = []
balls = []
ball_speed = 1
lives = 3
miss_fire = 0
frame_count = 0
ball_spawn_delay = 100

def findzone(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) >= abs(dy):  # zones 0, 3, 4, 7
        if dx >= 0:
            if dy >= 0:
                zone = 0
            else:
                zone = 7
        else:
            if dy >= 0:
                zone = 3
            else:
                zone = 4
    else:  # zones 1, 2, 5, 6
        if dx >= 0:
            if dy >= 0:
                zone = 1
            else:
                zone = 6
        else:
            if dy >= 0:
                zone = 2
            else:
                zone = 5
    return zone

def convertToZone0(zone, x, y):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def originalZone(zone, x, y):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def draw_line_raw(zone, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    dNE = 2 * (dy - dx)
    dE = 2 * dy

    x, y = x1, y1

    while x <= x2:
        cx, cy = originalZone(zone, x, y)
        glVertex2f(cx, cy)
        if x == x2 and y == y2:
            break
        x += 1
        if d > 0:
            y += 1
            d += dNE
        else:
            d += dE

def draw_line_8way(x1, y1, x2, y2):
    zone = findzone(x1, y1, x2, y2)
    x1, y1 = convertToZone0(zone, x1, y1)
    x2, y2 = convertToZone0(zone, x2, y2)
    draw_line_raw(zone, x1, y1, x2, y2)

def draw_left_arrow():
    glBegin(GL_POINTS)
    draw_line_8way(40, 790, 10, 770)
    draw_line_8way(10, 770, 40, 750)
    draw_line_8way(10, 770, 50, 770)
    glEnd()

def draw_play_pause_icon():
    glBegin(GL_POINTS)
    if playing:
        draw_line_8way(290, 750, 290, 790)
        draw_line_8way(310, 750, 310, 790)
    else:
        draw_line_8way(290, 750, 290, 790)
        draw_line_8way(290, 750, 310, 770)
        draw_line_8way(290, 790, 310, 770)
    glEnd()

def draw_cross():
    glBegin(GL_POINTS)
    draw_line_8way(550, 750, 590, 790)
    draw_line_8way(550, 790, 590, 750)
    glEnd()

def circlePoints(x, y, x0, y0):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x + x0, y + y0)
    glVertex2f(y + x0, x + y0)
    glVertex2f(y + x0, -x + y0)
    glVertex2f(x + x0, -y + y0)
    glVertex2f(-x + x0, -y + y0)
    glVertex2f(-y + x0, -x + y0)
    glVertex2f(-y + x0, x + y0)
    glVertex2f(-x + x0, y + y0)
    glEnd()


def midpointCircle(radius, x0, y0):
    d = 1 - radius
    x = 0
    y = radius

    circlePoints(x, y, x0, y0)

    while x < y:
        if d < 0:
            # E
            d = d + 2*x + 3
            x += 1
        else:
            # SE
            d = d + 2*x -2*y + 5
            x += 1
            y = y - 1

        circlePoints(x, y, x0, y0)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255, 255, 0)

class Ball:
    def __init__(self):
        self.radius = random.randint(20, 30)
        self.x = random.randint(self.radius, w_width - self.radius)
        self.y = (w_height - 50) - self.radius
        self.color = (random.random(), random.random(), random.random())

def draw_shooter(radius, x0, y0):
    midpointCircle(radius, x0, y0)

def draw_bullet(radius, x0, y0):
    midpointCircle(radius, x0, y0)

def draw_balls():
    for ball in balls:
        glColor3f(*ball.color)
        midpointCircle(ball.radius, ball.x, ball.y)

def iterate():
    glViewport(0, 0, 1000, 1000)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000, 0.0, 1000, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def update(value):
    global score, playing, game_over, lives, miss_fire, frame_count
    if playing and not game_over:
        frame_count += 1
        for ball in balls:
            ball.y -= ball_speed
            if ball.y < -ball.radius:
                if lives <= 1:
                    balls.clear()
                    bullets.clear()
                    print(f"Game Over! Score: {score}")
                    game_over = True
                else:
                    lives -= 1
                    balls.remove(ball)
                    print(f"Missed a circle, lives remaining {lives}/3")
            elif (shooter_x - ball.x) ** 2 + (shooter_y - ball.y) ** 2 <= (ball.radius + shooter_r) ** 2:
                game_over = True
                balls.clear()
                bullets.clear()
                print(f"Game Over! Score: {score}")
                break

        for bullet in bullets:
            bullet.y += bullet_speed
            if bullet.y > 750:
                if miss_fire >= 2:
                    balls.clear()
                    bullets.clear()
                    print(f"Game Over! Score: {score}")
                    game_over = True
                else:
                    miss_fire += 1
                    bullets.remove(bullet)
                    print(f"{miss_fire} miss fire!")


            for ball in balls:
                if (bullet.x - ball.x) ** 2 + (bullet.y - ball.y) ** 2 <= (ball.radius + bullet_r) ** 2:
                    bullets.remove(bullet)
                    balls.remove(ball)
                    score += 1
                    print(f"Score: {score}")
                    break

        if frame_count >= ball_spawn_delay:
            balls.append(Ball())
            frame_count = 0

    glutPostRedisplay()
    glutTimerFunc(10, update, 0)

def keyboard(key, x, y):
    global shooter_x
    if not game_over and playing:
        if key==b'a' and shooter_x > 20:
            shooter_x -= 20
        elif key==b'd' and shooter_x < 580:
            shooter_x += 20
        if key==b' ':
            bullets.append(Bullet(shooter_x,shooter_y))
def mouse(button, state, x, y):
    global playing, score, game_over, shooter_x, lives, miss_fire, frame_count
    if state == GLUT_DOWN:
        y = 800 - y

        if 10 <= x <= 50 and 750 <= y <= 790:
            print("Starting Over!")
            score = 0
            balls.clear()
            bullets.clear()
            lives = 3
            game_over = False
            playing = True
            miss_fire = 0
            frame_count = 0
            shooter_x = w_width / 2

        elif 290 <= x <= 310 and 750 <= y <= 790:
            playing = not playing

        elif 550 <= x <= 590 and 750 <= y <= 790:
            print(f"Goodbye! Score: {score}")
            glutLeaveMainLoop()
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    draw_balls()
    for bullet in bullets:
        if bullet.y < 750:
            glColor3f(*bullet.color)
            draw_bullet(bullet_r, bullet.x, bullet.y)

    glColor3f(0, 1, 1)
    draw_left_arrow()
    glColor3f(1, 0.5, 0)
    draw_play_pause_icon()
    glColor3f(1, 0, 0)
    draw_cross()
    if game_over:
        glColor3f(1, 0, 0)
    else:
        glColor3f(1, 1, 1)
    draw_shooter(shooter_r, shooter_x, shooter_y)
    glFlush()
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(w_width, w_height)
glutInitWindowPosition(500, 0)
wind = glutCreateWindow(b"Shoot the Balls!")
glutDisplayFunc(showScreen)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutTimerFunc(10, update, 0)

glutMainLoop()