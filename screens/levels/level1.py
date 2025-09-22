# screens/levels/level1.py
import pygame, os, time

# --------- WELCOME SCREEN ---------
class Level1Welcome:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 24)

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
            "The river will shrink over time.",
            "Use the farmer to manage resources smartly!"
        ]
        y = 120
        for line in instructions:
            self.draw_text_with_bg(line, self.text_font, (50, 50, 50), 50, y)
            y += 50

        pygame.draw.rect(self.screen, (34, 139, 230), self.continue_button, border_radius=8)
        cont_text = self.text_font.render("Start Level", True, (255, 255, 255))
        self.screen.blit(cont_text, (self.continue_button.centerx - cont_text.get_width()//2,
                                     self.continue_button.centery - cont_text.get_height()//2))


# --------- DROUGHT SCREEN ---------
class Level1Drought:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)

        # Assets folder
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))

        # Background
        self.bg_img = self.load_image("drought_bg.jpg", (self.W, self.H), fill=(210, 180, 140))

        # River
        self.river_width = self.W // 4
        self.river_img = self.load_image("river.png", (self.river_width, self.H), fill=(0, 100, 255))
        self.river_y = 0

        # Sun
        self.sun_img_orig = self.load_image("sun.png", (120, 120), fill=(255, 255, 0))
        self.sun_angle = 0

        # Field
        self.field_img = self.load_image("field.jpg", (280, 220), fill=(139, 69, 19))
        self.field_rect = self.field_img.get_rect(bottomright=(self.W, self.H))

        # Farmer
        self.farmer_img = self.load_image("farmer.png", (120, 180), fill=(0, 200, 0))
        self.farmer_img_flipped = pygame.transform.flip(self.farmer_img, True, False)
        self.farmer_rect = self.farmer_img.get_rect(center=(self.W // 2, self.H // 2))
        self.farmer_y_offset = 0
        self.bob_direction = 1
        self.farmer_speed = 5
        self.facing_left = False

        # Timer
        self.total_time = 300
        self.start_time = time.time()

        # Water system
        self.max_water = 100
        self.current_water = self.max_water

        # Scores
        self.scores = {"sustainability": 0, "yield": 0, "water_efficiency": 0}

        # Popup state
        self.show_choice_popup = False
        self.choice_buttons = [
            ("High-Value Crops 🌽", pygame.Rect(self.W//2 - 150, self.H//2 - 80, 300, 50)),
            ("Drought-Resistant 🌱", pygame.Rect(self.W//2 - 150, self.H//2 - 10, 300, 50)),
            ("Balanced ⚖️", pygame.Rect(self.W//2 - 150, self.H//2 + 60, 300, 50)),
        ]
        self.feedback_msg = ""
        self.feedback_timer = 0

    def load_image(self, filename, size=None, fill=None):
        path = os.path.join(self.assets, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except:
            surf = pygame.Surface(size if size else (50, 50))
            if fill: surf.fill(fill)
            else: surf.fill((200, 200, 200))
            return surf

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.show_choice_popup:
            for label, rect in self.choice_buttons:
                if rect.collidepoint(event.pos):
                    self.apply_choice(label)

    def apply_choice(self, label):
        if label.startswith("High-Value"):
            self.current_water = max(0, self.current_water - 20)
            self.scores["yield"] += 15
            self.scores["sustainability"] -= 5
            self.feedback_msg = "High-value crops boosted, but others wilt."
        elif label.startswith("Drought-Resistant"):
            self.current_water = max(0, self.current_water - 10)
            self.scores["sustainability"] += 10
            self.scores["water_efficiency"] += 5
            self.feedback_msg = "Resistant crops survive, safer for long droughts."
        elif label.startswith("Balanced"):
            self.current_water = max(0, self.current_water - 15)
            self.scores["yield"] += 8
            self.scores["sustainability"] += 5
            self.scores["water_efficiency"] += 3
            self.feedback_msg = "Balanced allocation across all crops."

        self.show_choice_popup = False
        self.feedback_timer = time.time()

    def update(self):
        elapsed = time.time() - self.start_time
        remaining = self.total_time - elapsed
        if remaining <= 0:
            print("Level Over - Timer ended!")

        # River animation
        self.river_y = (self.river_y - 0.2) % self.H

        # Sun rotation
        self.sun_angle = (self.sun_angle + 0.3) % 360

        # Farmer idle bobbing
        self.farmer_y_offset += self.bob_direction * 0.2
        if abs(self.farmer_y_offset) > 5:
            self.bob_direction *= -1

        # Farmer movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.farmer_rect.x -= self.farmer_speed
            self.facing_left = True
        if keys[pygame.K_RIGHT]:
            self.farmer_rect.x += self.farmer_speed
            self.facing_left = False
        if keys[pygame.K_UP]:
            self.farmer_rect.y -= self.farmer_speed
        if keys[pygame.K_DOWN]:
            self.farmer_rect.y += self.farmer_speed

        # Boundaries
        if self.farmer_rect.left < self.river_width:
            self.farmer_rect.left = self.river_width
        if self.farmer_rect.right > self.W - 280:
            self.farmer_rect.right = self.W - 280
        if self.farmer_rect.top < 150:
            self.farmer_rect.top = 150
        if self.farmer_rect.bottom > self.H - 50:
            self.farmer_rect.bottom = self.H - 50

        # Water depletion
        self.current_water = max(0, self.current_water - 0.02)

        # Trigger popup when farmer reaches field
        if self.farmer_rect.colliderect(self.field_rect):
            self.show_choice_popup = True

    def draw(self):
        # Background
        self.screen.blit(self.bg_img, (0, 0))

        # River
        self.screen.blit(self.river_img, (0, self.river_y - self.H))
        self.screen.blit(self.river_img, (0, self.river_y))

        # Sun
        rotated_sun = pygame.transform.rotate(self.sun_img_orig, self.sun_angle)
        sun_rect = rotated_sun.get_rect(topright=(self.W - 20, 20))
        self.screen.blit(rotated_sun, sun_rect)

        # Field
        self.screen.blit(self.field_img, self.field_rect)

        # Farmer
        farmer_draw_img = self.farmer_img_flipped if self.facing_left else self.farmer_img
        farmer_draw_rect = farmer_draw_img.get_rect(
            center=(self.farmer_rect.centerx, self.farmer_rect.centery + self.farmer_y_offset))
        self.screen.blit(farmer_draw_img, farmer_draw_rect)

        # Timer
        elapsed = time.time() - self.start_time
        remaining = max(0, int(self.total_time - elapsed))
        mins, secs = divmod(remaining, 60)
        timer_text = self.title_font.render(f"Time Left: {mins:02}:{secs:02}", True, (255, 255, 255))
        self.screen.blit(timer_text, (self.W//2 - timer_text.get_width()//2, 20))

        # Water bar
        bar_w, bar_h = 200, 25
        bar_x, bar_y = 20, 20
        pygame.draw.rect(self.screen, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        water_width = int((self.current_water / self.max_water) * bar_w)
        pygame.draw.rect(self.screen, (0, 120, 255), (bar_x, bar_y, water_width, bar_h), border_radius=6)
        txt = self.title_font.render("Water", True, (0, 0, 0))
        self.screen.blit(txt, (bar_x, bar_y + bar_h + 5))

        # Popup
        if self.show_choice_popup:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            for label, rect in self.choice_buttons:
                pygame.draw.rect(self.screen, (34, 139, 230), rect, border_radius=8)
                txt = self.title_font.render(label, True, (255, 255, 255))
                self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        # Feedback
        if self.feedback_msg and time.time() - self.feedback_timer < 3:
            fb = self.title_font.render(self.feedback_msg, True, (255, 255, 0))
            self.screen.blit(fb, (self.W//2 - fb.get_width()//2, self.H - 100))
