import pygame
import os
import time
import random
import pdb

WINDOW_WIDTH, WINDOW_HEIGHT = 500, 800
pygame.font.init()

BIRD_IMAGES = []
for bird_index in range(1, 4):
    BIRD_IMAGES.append(pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird" + str(bird_index) + ".png"))))

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.img_count = 0
        self.img = BIRD_IMAGES[0]
        self.tilt = 0
        self.height = y
        self.max_rotation = 25
        self.rotation_vel = 20
        self.animation_time = 5

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d >= 16: d = 16
        if d < 0: d -= 2
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rotation_vel

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.animation_time:
            self.img = BIRD_IMAGES[0]
        elif self.img_count < self.animation_time * 2:
            self.img = BIRD_IMAGES[1]
        elif self.img_count < self.animation_time * 3:
            self.img = BIRD_IMAGES[2]
        elif self.img_count < self.animation_time * 4:
            self.img = BIRD_IMAGES[1]
        elif self.img_count == self.animation_time * 4 + 1:
            self.img = BIRD_IMAGES[0]
            self.img_count =  0

        if self.tilt <= -80:
            self.img = BIRD_IMAGES[1]
            self.img_count = self.animation_time * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    def __init__(self, x):
        self.gap = 400
        self.vel = 5
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x = self.x - self.vel

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        return t_point or b_point

class Base:
    def __init__(self, y):
        self.vel = 5
        self.width = BASE_IMAGE.get_width()
        self.img = BASE_IMAGE
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 = self.x1 - self.vel
        self.x2 = self.x2 - self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BACKGROUND_IMAGE, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes =  [Pipe(600)]

    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    bird.jump()
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        rem, add_pipe = [], False
        for pipe in pipes:
            if pipe.collide(bird, win):
                run = False
                break

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            run = False

        base.move()
        draw_window(win, bird, pipes, base, score)
    pygame.quit()
    quit()

main()
