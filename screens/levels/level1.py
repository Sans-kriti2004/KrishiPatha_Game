# screens/levels/level1.py
import pygame, os, time

class Level1Welcome:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)

        # Load background
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))
        bg_path = os.path.join(self.assets, "welcome_bg.jpg")
        try:
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (self.W, self.H))
        except:
            self.bg_img = pygame.Surface((self.W, self.H))
            self.bg_img.fill((200, 200, 200))

        # Continue button
        self.continue_button = pygame.Rect(self.W//2 - 100, self.H - 100, 200, 50)

    def draw_text_with_bg(self, text, font, color, x, y, padding=6):
        txt_surf = font.render(text, True, color)
        rect = txt_surf.get_rect(topleft=(x, y))
        bg_rect = pygame.Rect(rect.x - padding, rect.y - padding,
                              rect.width + 2*padding, rect.height + 2*padding)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=6)
        self.screen.blit(txt_surf, rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                # Go to drought screen
                self.set_screen(Level1Drought(self.screen, self.set_screen))

    def update(self): pass

    def draw(self):
        self.screen.blit(self.bg_img, (0, 0))
        self.draw_text_with_bg("WELCOME", self.title_font, (30, 30, 30), 30, 30)

        instructions = [
            "Scenario: Severe drought has hit your village.",
            "Your goal: Manage limited water wisely.",
            "Make decisions cycle by cycle.",
            "Every choice impacts sustainability, yield, and efficiency."
        ]
        y = 120
        for line in instructions:
            self.draw_text_with_bg(line, self.text_font, (50, 50, 50), 50, y)
            y += 50

        pygame.draw.rect(self.screen, (34, 139, 230), self.continue_button, border_radius=8)
        cont_text = self.text_font.render("Start Level", True, (255, 255, 255))
        self.screen.blit(cont_text, (self.continue_button.centerx - cont_text.get_width()//2,
                                     self.continue_button.centery - cont_text.get_height()//2))


# --------- NEW DROUGHT SCREEN ---------
class Level1Drought:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 22)

        # Assets folder
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))

        # Load drought background
        drought_path = os.path.join(self.assets, "drought_bg.jpg")
        try:
            self.bg_img = pygame.image.load(drought_path).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (self.W, self.H))
        except:
            self.bg_img = pygame.Surface((self.W, self.H))
            self.bg_img.fill((210, 180, 140))  # fallback

        # Load river image
        river_path = os.path.join(self.assets, "river.jpg")
        try:
            self.river_img = pygame.image.load(river_path).convert_alpha()
            self.river_img = pygame.transform.smoothscale(self.river_img, (self.W // 4, self.H))
        except:
            self.river_img = pygame.Surface((self.W // 4, self.H))
            self.river_img.fill((0, 100, 255))  # fallback: blue rectangle

        # For animation (river scrolling vertically)
        self.river_y = 0

        # Timer setup (5 mins = 300 sec)
        self.total_time = 300
        self.start_time = time.time()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass  # later: handle interactions

    def update(self):
        elapsed = time.time() - self.start_time
        remaining = self.total_time - elapsed
        if remaining <= 0:
            print("Level Over - Timer ended!")

        # Animate river movement (scroll upwards)
        #self.river_y = (self.river_y - 1) % self.H  # speed = 1px per frame

    def draw(self):
        # Draw drought background
        self.screen.blit(self.bg_img, (0, 0))

        # Draw scrolling river on left side
        self.screen.blit(self.river_img, (0, self.river_y - self.H))
        self.screen.blit(self.river_img, (0, self.river_y))

        # Timer at top
        elapsed = time.time() - self.start_time
        remaining = max(0, int(self.total_time - elapsed))
        mins, secs = divmod(remaining, 60)
        timer_text = self.title_font.render(f"Time Left: {mins:02}:{secs:02}", True, (255, 0, 0))
        timer_box = pygame.Rect(self.W//2 - 120, 20, 240, 50)
        pygame.draw.rect(self.screen, (255,255,255), timer_box, border_radius=8)
        self.screen.blit(timer_text, (timer_box.centerx - timer_text.get_width()//2,
                                      timer_box.centery - timer_text.get_height()//2))
