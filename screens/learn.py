import pygame

class LearnPage:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 25)

        # Back button (top-left corner)
        self.back_button = pygame.Rect(20, 20, 100, 40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.collidepoint(event.pos):
                from screens.landing import LandingPage
                self.set_screen(LandingPage(self.screen, self.set_screen))

    def update(self):
        pass

    def draw(self):
        self.screen.fill((180, 220, 255))  # light blue background

        text = self.font.render("📘 Explore Mode (Work in Progress)", True, (0, 0, 128))
        self.screen.blit(text, (150, 250))

        # Draw back button
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_button, border_radius=5)
        back_text = self.small_font.render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 20, self.back_button.y + 8))
