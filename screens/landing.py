import pygame, os, re
from screens.learn import LearnPage
from screens.challenge import ChallengePage

class LandingPage:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback

        # Build relative folder path
        base_path = os.path.dirname(__file__)  
        folder = os.path.join(base_path, "..", "assets", "background", "landing_bg")
        folder = os.path.abspath(folder)

        # Sort frames numerically
        def numerical_sort(value):
            numbers = re.findall(r'\d+', value)
            return int(numbers[0]) if numbers else -1

        # Load frames
        self.frames = []
        if os.path.exists(folder):
            for f in sorted(os.listdir(folder), key=numerical_sort):
                if f.endswith(".png") or f.endswith(".jpg"):
                    img = pygame.image.load(os.path.join(folder, f))
                    img = pygame.transform.scale(img, (900, 600))  
                    self.frames.append(img)

        print("Loaded frames:", len(self.frames))

        self.current_frame = 0
        self.frame_delay = 3
        self.counter = 0

        # Fonts
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)

        # Buttons
        self.learn_button = pygame.Rect(350, 250, 200, 60)
        self.challenge_button = pygame.Rect(350, 350, 200, 60)

        # Fade-in alpha
        self.alpha = 0
        self.fade_speed = 5  # adjust for faster/slower fade

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.learn_button.collidepoint(event.pos):
                self.set_screen(LearnPage(self.screen, self.set_screen))
            elif self.challenge_button.collidepoint(event.pos):
                self.set_screen(ChallengePage(self.screen, self.set_screen))

    def update(self):
        # Animate background
        if self.frames:
            self.counter += 1
            if self.counter >= self.frame_delay:
                self.counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Fade-in animation
        if self.alpha < 255:
            self.alpha += self.fade_speed

    def draw(self):
        # Background
        if self.frames:
            self.screen.blit(self.frames[self.current_frame], (0, 0))
        else:
            self.screen.fill((200, 255, 200))

        # Semi-transparent overlay
        overlay = pygame.Surface((900, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))  
        self.screen.blit(overlay, (0, 0))

        # Center title
        title = self.title_font.render("KrishiPatha", True, (255, 255, 255))
        title.set_alpha(self.alpha)
        title_rect = title.get_rect(center=(450, 150))   # center horizontally
        self.screen.blit(title, title_rect)

        # Hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Learn button
        learn_color = (34, 197, 94) if not self.learn_button.collidepoint(mouse_pos) else (20, 150, 70)
        pygame.draw.rect(self.screen, learn_color, self.learn_button, border_radius=15)
        learn_text = self.font.render("Explore", True, (255, 255, 255))
        learn_rect = learn_text.get_rect(center=self.learn_button.center)
        self.screen.blit(learn_text, learn_rect)

        # Challenge button
        challenge_color = (234, 179, 8) if not self.challenge_button.collidepoint(mouse_pos) else (200, 140, 0)
        pygame.draw.rect(self.screen, challenge_color, self.challenge_button, border_radius=15)
        challenge_text = self.font.render("Challenge", True, (0, 0, 0))
        challenge_rect = challenge_text.get_rect(center=self.challenge_button.center)
        self.screen.blit(challenge_text, challenge_rect)
