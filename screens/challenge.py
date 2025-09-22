import pygame, os, re

class ChallengePage:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        
        # Build relative folder path for challenge background frames
        base_path = os.path.dirname(__file__)  
        folder = os.path.join(base_path, "..", "assets", "challenge_bg")
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

        print("Loaded challenge frames:", len(self.frames))

        self.current_frame = 0
        self.frame_delay = 3
        self.counter = 0

        # Back button
        self.back_button = pygame.Rect(20, 20, 90, 40)

        # Level buttons
        self.level_buttons = []
        for i in range(5):
            rect = pygame.Rect(300, 150 + i*70, 300, 50)
            self.level_buttons.append((i+1, rect))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Back to Landing Page
            if self.back_button.collidepoint(event.pos):
                from screens.landing import LandingPage
                self.set_screen(LandingPage(self.screen, self.set_screen))

            # Level select
            for level, rect in self.level_buttons:
                if rect.collidepoint(event.pos):
                    if level == 1:
                        from .levels.level1 import Level1Welcome
                        self.set_screen(Level1Welcome(self.screen, self.set_screen))
                    elif level == 2:
                        from screens.levels.level2 import Level2
                        self.set_screen(Level2(self.screen, self.set_screen))
                    elif level == 3:
                        from screens.levels.level3 import Level3
                        self.set_screen(Level3(self.screen, self.set_screen))
                    elif level == 4:
                        from screens.levels.level4 import Level4
                        self.set_screen(Level4(self.screen, self.set_screen))
                    elif level == 5:
                        from screens.levels.level5 import Level5
                        self.set_screen(Level5(self.screen, self.set_screen))

    def update(self):
        if self.frames:
            self.counter += 1
            if self.counter >= self.frame_delay:
                self.counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self):
        # Background video
        if self.frames:
            self.screen.blit(self.frames[self.current_frame], (0, 0))
        else:
            self.screen.fill((255, 228, 181))  # fallback

        # Title with semi-transparent background
        title_text = "🌾 Challenge Mode - Select a Level"
        title_surface = self.font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(450, 80))

        overlay = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # semi-transparent dark
        overlay_rect = overlay.get_rect(center=title_rect.center)

        self.screen.blit(overlay, overlay_rect)
        self.screen.blit(title_surface, title_rect)

        # Back button
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_button, border_radius=8)
        back_text = self.font.render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 15, self.back_button.y + 5))

        # Level buttons with semi-transparent overlay for readability
        for level, rect in self.level_buttons:
            btn_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            btn_overlay.fill((0, 0, 0, 120))  # dark translucent background
            self.screen.blit(btn_overlay, rect.topleft)

            pygame.draw.rect(self.screen, (34, 139, 230), rect, 2, border_radius=8)  # border
            text = self.font.render(f"Level {level}", True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 100, rect.y + 10))
