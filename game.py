import pygame
import sys
from screens.landing import LandingPage
from screens.learn import LearnPage
from screens.challenge import ChallengePage

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🌱 KrishiPatha")

# Clock
clock = pygame.time.Clock()

# Screen manager
def set_screen(new_screen):
    global current_screen
    current_screen = new_screen

# Start with landing page
current_screen = LandingPage(screen, set_screen)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Pass events to current screen
        current_screen.handle_event(event)

    # Update and draw
    current_screen.update()
    current_screen.draw()

    pygame.display.flip()
    clock.tick(30)   # 30 FPS for smooth playback
