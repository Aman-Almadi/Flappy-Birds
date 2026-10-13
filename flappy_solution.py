import random
import sys

import pygame

pygame.init()

# ---------------------------------------------------------------
# WINDOW
# ---------------------------------------------------------------
WIDTH = 400
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Studio - Build v1.0")
clock = pygame.time.Clock()
big_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 24, bold=True)

GRAVITY = 0.5           # extra downward speed added every frame
FLAP_STRENGTH = -8      
PIPE_SPEED = 3          # pixels each pipe moves left per frame
PIPE_GAP = 160          
PIPE_WIDTH = 60
PIPE_SPACING = 220      # distance between two pipes

BIRD_X = 90
BIRD_RADIUS = 16
GROUND_HEIGHT = 60

SKY = (112, 197, 206)
GREEN = (84, 170, 60)
DARK_GREEN = (50, 120, 40)
YELLOW = (250, 220, 40)
ORANGE = (240, 140, 30)
BROWN = (222, 184, 135)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ---------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------

def make_pipe(x):
    lowest_gap_top = max(60, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 60)
    gap_top = random.randint(60, lowest_gap_top)    # a random height for the gap
    return {"x": x, "gap_top": gap_top, "scored": False}


def new_game():
    bird_y = HEIGHT // 2
    bird_speed = 0
    pipes = [make_pipe(WIDTH + 100)]
    score = 0
    return bird_y, bird_speed, pipes, score


def hits_pipe(bird_y, pipes):
    for pipe in pipes:
        in_pipe_columns = (BIRD_X + BIRD_RADIUS > pipe["x"] and
                           BIRD_X - BIRD_RADIUS < pipe["x"] + PIPE_WIDTH)
        if in_pipe_columns:
            above_gap = bird_y - BIRD_RADIUS < pipe["gap_top"]
            below_gap = bird_y + BIRD_RADIUS > pipe["gap_top"] + PIPE_GAP
            if above_gap or below_gap:
                return True
    return False


def hits_ground_or_ceiling(bird_y):
    ground_top = HEIGHT - GROUND_HEIGHT
    return bird_y + BIRD_RADIUS >= ground_top or bird_y - BIRD_RADIUS <= 0


def draw_text(text, font, colour, centre_x, centre_y):
    shadow = font.render(text, True, BLACK)
    words = font.render(text, True, colour)
    screen.blit(shadow, shadow.get_rect(center=(centre_x + 2, centre_y + 2)))
    screen.blit(words, words.get_rect(center=(centre_x, centre_y)))


def draw_game(bird_y, pipes, score, state, high_score):
    screen.fill(SKY)

    for pipe in pipes:
        top_height = pipe["gap_top"]
        bottom_y = pipe["gap_top"] + PIPE_GAP
        bottom_height = HEIGHT - GROUND_HEIGHT - bottom_y
        pygame.draw.rect(screen, GREEN, (pipe["x"], 0, PIPE_WIDTH, top_height))
        pygame.draw.rect(screen, GREEN, (pipe["x"], bottom_y, PIPE_WIDTH, bottom_height))
        pygame.draw.rect(screen, DARK_GREEN, (pipe["x"], 0, PIPE_WIDTH, top_height), 3)
        pygame.draw.rect(screen, DARK_GREEN, (pipe["x"], bottom_y, PIPE_WIDTH, bottom_height), 3)

    pygame.draw.rect(screen, BROWN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    pygame.draw.line(screen, DARK_GREEN, (0, HEIGHT - GROUND_HEIGHT), (WIDTH, HEIGHT - GROUND_HEIGHT), 4)

    # The bird: a yellow circle, an eye and an orange beak
    pygame.draw.circle(screen, YELLOW, (BIRD_X, int(bird_y)), BIRD_RADIUS)
    pygame.draw.circle(screen, WHITE, (BIRD_X + 6, int(bird_y) - 5), 6)
    pygame.draw.circle(screen, BLACK, (BIRD_X + 8, int(bird_y) - 5), 3)
    beak = [(BIRD_X + 12, int(bird_y)), (BIRD_X + 24, int(bird_y) + 3), (BIRD_X + 12, int(bird_y) + 8)]
    pygame.draw.polygon(screen, ORANGE, beak)

    # Which message we show depends on the game STATE
    if state == "start":
        draw_text("Flappy Studio", big_font, WHITE, WIDTH // 2, 170)
        draw_text("Press SPACE to start", small_font, WHITE, WIDTH // 2, 240)
    elif state == "playing":
        draw_text(str(score), big_font, WHITE, WIDTH // 2, 60)
    elif state == "game_over":
        draw_text("Game Over", big_font, WHITE, WIDTH // 2, 170)
        draw_text("Score: " + str(score), small_font, WHITE, WIDTH // 2, 230)
        draw_text("Best: " + str(high_score), small_font, WHITE, WIDTH // 2, 265)
        draw_text("Press SPACE to play again", small_font, WHITE, WIDTH // 2, 320)


# ---------------------------------------------------------------
# GAME STATE
# ---------------------------------------------------------------
bird_y, bird_speed, pipes, score = new_game()
high_score = 0
state = "start"         # always ONE of: "start", "playing", "game_over"

# ---------------------------------------------------------------
# THE GAME LOOP
# ---------------------------------------------------------------
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        pressed_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        clicked = event.type == pygame.MOUSEBUTTONDOWN
        if pressed_space or clicked:
            if state == "start":
                state = "playing"
                bird_speed = FLAP_STRENGTH
            elif state == "playing":
                bird_speed = FLAP_STRENGTH                      # flap!
            elif state == "game_over":
                bird_y, bird_speed, pipes, score = new_game()   # unpack the tuple
                state = "start"

    if state == "playing":

        # Gravity: the speed changes first, then the position changes
        bird_speed = bird_speed + GRAVITY
        bird_y = bird_y + bird_speed

        for pipe in pipes:
            pipe["x"] = pipe["x"] - PIPE_SPEED          # move every pipe left

        # Add a new pipe once the last one has moved far enough
        if pipes[-1]["x"] < WIDTH - PIPE_SPACING:
            pipes.append(make_pipe(WIDTH))

        # Keep only the pipes that are still on the screen
        still_on_screen = []
        for pipe in pipes:
            if pipe["x"] + PIPE_WIDTH > 0:
                still_on_screen.append(pipe)
        pipes = still_on_screen

        for pipe in pipes:
            passed = pipe["x"] + PIPE_WIDTH < BIRD_X - BIRD_RADIUS
            if passed and not pipe["scored"]:
                pipe["scored"] = True                   # so it is counted only ONCE
                score = score + 1

        if hits_pipe(bird_y, pipes) or hits_ground_or_ceiling(bird_y):
            state = "game_over"

        if score > high_score:
            high_score = score

    draw_game(bird_y, pipes, score, state, high_score)
    pygame.display.flip()
    clock.tick(FPS)