# screens/levels/level1.py
import pygame, os, sys, time

class Level1:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Paths
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))

        # Fonts
        self.font = pygame.font.Font(None, 34)
        self.big_font = pygame.font.Font(None, 72)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 150, 0)
        self.LIGHT_GREEN = (144, 238, 144)
        self.GRAY = (200, 200, 200)
        self.RED = (220, 50, 50)

        # Game states
        self.STATE_CROP_SELECT = "crop_select"
        self.STATE_IRRIGATION = "irrigation"
        self.STATE_HARVEST = "harvest"
        self.STATE_QUIZ_COUNTDOWN = "quiz_countdown"
        self.STATE_QUIZ = "quiz"
        self.STATE_RESULT = "result"

        self.state = self.STATE_CROP_SELECT
        self.selected_crop = None
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False
        self.feedback_time = 0
        self.quiz_countdown_start = 0
        self.quiz_countdown_length = 3

        # Load images
        self.farm_bg = self.load_image("farm_bg.jpg", (self.W, self.H))
        self.wheat_img = self.load_image("wheat.png", (120, 120))
        self.rice_img = self.load_image("rice.png", (120, 120))
        self.cotton_img = self.load_image("cotton.png", (120, 120))
        self.harvest_img = self.load_image("sack.png", (150, 150))
        self.canal_img = self.load_image("canal.png", (120, 120))
        self.sprinkler_img = self.load_image("sprinkler.png", (120, 120))
        self.drip_img = self.load_image("drip.png", (120, 120))

        # Quiz data
        self.questions = [
            {"q": "Which farming method helps conserve water during drought?",
             "options": ["Drip irrigation", "Canal irrigation", "Sprinkler irrigation"],
             "answer": "Drip irrigation"},
            {"q": "Which crop can survive with less water?",
             "options": ["Millet", "Rice", "Sugarcane"],
             "answer": "Millet"},
            {"q": "What should farmers do to maintain soil moisture in drought?",
             "options": ["Use mulching", "Flood the field", "Remove vegetation"],
             "answer": "Use mulching"}
        ]

    def load_image(self, name, size):
        try:
            path = os.path.join(self.assets, name)
            img = pygame.image.load(path)
            return pygame.transform.scale(img, size)
        except Exception as e:
            print(f"⚠️ Failed to load image: {name}", e)
            surf = pygame.Surface(size)
            surf.fill((150, 150, 150))
            return surf

    def draw_text(self, text, x, y, color=None, font=None):
        if font is None:
            font = self.font
        if color is None:
            color = self.BLACK
        txt = font.render(text, True, color)
        self.screen.blit(txt, (x, y))

    def draw_button(self, text, x, y, w, h, color):
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        self.draw_text(text, x + 10, y + 10)

    def restart_game(self):
        self.state = self.STATE_CROP_SELECT
        self.selected_crop = None
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.state == self.STATE_CROP_SELECT:
                if 120 <= x <= 270 and 420 <= y <= 470:
                    self.selected_crop = "Wheat"
                    self.state = self.STATE_IRRIGATION
                elif 320 <= x <= 470 and 420 <= y <= 470:
                    self.selected_crop = "Rice"
                    self.state = self.STATE_IRRIGATION
                elif 520 <= x <= 670 and 420 <= y <= 470:
                    self.selected_crop = "Cotton"
                    self.state = self.STATE_IRRIGATION

            elif self.state == self.STATE_IRRIGATION:
                if 180 <= x <= 330 and 420 <= y <= 470:
                    self.state = self.STATE_HARVEST
                elif 340 <= x <= 490 and 420 <= y <= 470:
                    self.state = self.STATE_HARVEST
                elif 500 <= x <= 650 and 420 <= y <= 470:
                    self.state = self.STATE_HARVEST

            elif self.state == self.STATE_HARVEST:
                if 300 <= x <= 500 and 450 <= y <= 530:
                    self.state = self.STATE_QUIZ_COUNTDOWN
                    self.quiz_countdown_start = pygame.time.get_ticks()

            elif self.state == self.STATE_RESULT:
                if 340 <= x <= 460 and 400 <= y <= 450:
                    self.restart_game()
                elif 480 <= x <= 680 and 400 <= y <= 450:
                    print("➡️ Future: Challenges page")

    def update(self):
        if self.state == self.STATE_QUIZ_COUNTDOWN:
            elapsed = (pygame.time.get_ticks() - self.quiz_countdown_start) / 1000
            if elapsed >= self.quiz_countdown_length:
                self.state = self.STATE_QUIZ
                self.current_question = 0
                self.score = 0
                self.feedback_text = ""
                self.feedback_pending = False

    def draw(self):
        if self.state == self.STATE_CROP_SELECT:
            self.screen.blit(self.farm_bg, (0, 0))
            self.draw_text("Choose a crop to plant:", 250, 80)
            self.draw_button("Wheat", 120, 420, 150, 50, self.LIGHT_GREEN)
            self.draw_button("Rice", 320, 420, 150, 50, self.LIGHT_GREEN)
            self.draw_button("Cotton", 520, 420, 150, 50, self.LIGHT_GREEN)

        elif self.state == self.STATE_IRRIGATION:
            self.screen.blit(self.farm_bg, (0, 0))
            self.draw_text(f"Crop: {self.selected_crop}", 350, 80)
            self.draw_text("Choose irrigation method:", 250, 130)
            self.draw_button("Canal", 180, 420, 150, 50, self.GRAY)
            self.draw_button("Sprinkler", 340, 420, 150, 50, self.GRAY)
            self.draw_button("Drip", 500, 420, 150, 50, self.GRAY)

        elif self.state == self.STATE_HARVEST:
            self.screen.blit(self.farm_bg, (0, 0))
            self.draw_text("Crop is ready to harvest!", 270, 80)
            self.screen.blit(self.harvest_img, (325, 150))
            self.draw_button("Harvest", 300, 450, 200, 50, self.GRAY)

        elif self.state == self.STATE_QUIZ_COUNTDOWN:
            self.screen.fill(self.WHITE)
            elapsed = (pygame.time.get_ticks() - self.quiz_countdown_start) / 1000
            remaining = max(0, self.quiz_countdown_length - int(elapsed))
            self.draw_text(f"Quiz starting in: {remaining}", 250, self.H // 2 - 50, self.BLACK, self.big_font)

        elif self.state == self.STATE_RESULT:
            self.screen.blit(self.farm_bg, (0, 0))
            self.draw_text("Quiz Completed!", 320, 150)
            self.draw_text(f"Your Score: {self.score}/3", 330, 200)
            self.draw_button("Restart", 340, 400, 120, 50, self.GRAY)
            self.draw_button("Go to Challenges", 480, 400, 200, 50, self.LIGHT_GREEN)
