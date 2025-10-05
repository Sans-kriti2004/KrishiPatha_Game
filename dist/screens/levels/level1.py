import pygame
import os
import webbrowser

class Level1:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = screen.get_size()

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 150, 0)
        self.LIGHT_GREEN = (144, 238, 144)
        self.GRAY = (200, 200, 200)
        self.RED = (220, 50, 50)
        self.DARK_BLUE = (10, 30, 80)
        self.BUTTON_BG = (0, 0, 0, 100)  # translucent black

        # Fonts
        self.font = pygame.font.Font(None, 34)
        self.big_font = pygame.font.Font(None, 72)

        # States
        self.STATE_CROP_SELECT = "crop_select"
        self.STATE_IRRIGATION = "irrigation"
        self.STATE_HARVEST = "harvest"
        self.STATE_QUIZ_COUNTDOWN = "quiz_countdown"
        self.STATE_QUIZ = "quiz"
        self.STATE_RESULT = "result"

        self.state = self.STATE_CROP_SELECT
        self.selected_crop = None
        self.selected_irrigation = None
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False
        self.feedback_time = 0
        self.quiz_countdown_start = 0
        self.quiz_countdown_length = 3

        # Asset loading
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))

        def load_image(name, size):
            try:
                img = pygame.image.load(os.path.join(self.assets, name))
                return pygame.transform.scale(img, size)
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                surf = pygame.Surface(size)
                surf.fill((150, 150, 150))
                return surf

        self.farm_bg = load_image("farm_bg.jpg", (self.W, self.H))
        self.quiz_bg = load_image("quiz_bg.jpg", (self.W, self.H))
        self.wheat_img = load_image("wheat.png", (120, 120))
        self.rice_img = load_image("rice.png", (120, 120))
        self.cotton_img = load_image("cotton.png", (120, 120))
        self.harvest_img = load_image("sack.png", (150, 150))
        self.canal_img = load_image("canal.png", (120, 120))
        self.sprinkler_img = load_image("sprinkler.png", (120, 120))
        self.drip_img = load_image("drip.png", (120, 120))

        # Button Rects
        self.back_button_rect = pygame.Rect(20, 20, 200, 40)
        self.gov_info_button_rect = pygame.Rect(300, 500, 300, 50)
        self.next_level_button_rect = pygame.Rect(620, 500, 220, 50)

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

    def draw_text(self, text, x, y, color=None, font=None):
        font = font or self.font
        color = color or self.BLACK
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def draw_button(self, text, rect, color):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.BUTTON_BG)
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(self.screen, self.DARK_BLUE, rect, 2, border_radius=8)
        txt_surf = self.font.render(text, True, pygame.Color('white'))
        txt_rect = txt_surf.get_rect(center=rect.center)
        self.screen.blit(txt_surf, txt_rect)

    def restart_game(self):
        self.state = self.STATE_CROP_SELECT
        self.selected_crop = None
        self.selected_irrigation = None
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.back_button_rect.collidepoint(x, y):
                if self.set_screen:
                    from screens.challenge import ChallengePage
                    self.set_screen(ChallengePage(self.screen, self.set_screen))
                return

            if self.gov_info_button_rect.collidepoint(x, y):
                webbrowser.open("https://agriwelfare.gov.in/en/Drought")
                return

            if self.next_level_button_rect.collidepoint(x, y):
                if self.set_screen:
                    from screens.levels.level2 import Level2  # adapt this path to your project
                    self.set_screen(Level2(self.screen, self.set_screen))
                return


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
                    self.selected_irrigation = "Canal"
                    self.state = self.STATE_HARVEST
                elif 340 <= x <= 490 and 420 <= y <= 470:
                    self.selected_irrigation = "Sprinkler"
                    self.state = self.STATE_HARVEST
                elif 500 <= x <= 650 and 420 <= y <= 470:
                    self.selected_irrigation = "Drip"
                    self.state = self.STATE_HARVEST

            elif self.state == self.STATE_HARVEST:
                if 300 <= x <= 500 and 450 <= y <= 530:
                    self.state = self.STATE_QUIZ_COUNTDOWN
                    self.quiz_countdown_start = pygame.time.get_ticks()

            elif self.state == self.STATE_QUIZ and not self.feedback_pending:
                for i, opt in enumerate(self.questions[self.current_question]["options"]):
                    oy_start = 150 + i * 100
                    oy_end = oy_start + 50
                    if oy_start <= y <= oy_end:
                        if opt == self.questions[self.current_question]["answer"]:
                            self.feedback_text = "Woohoo! Correct!"
                            self.score += 1
                        else:
                            self.feedback_text = f"Oops! The answer was {self.questions[self.current_question]['answer']}"
                        self.feedback_pending = True
                        self.feedback_time = pygame.time.get_ticks()
                        break

            elif self.state == self.STATE_RESULT:
                if 340 <= x <= 460 and 400 <= y <= 450:
                    self.restart_game()

    def update(self):
        if self.state == self.STATE_QUIZ_COUNTDOWN:
            elapsed = (pygame.time.get_ticks() - self.quiz_countdown_start) / 1000.0
            if elapsed >= self.quiz_countdown_length:
                self.state = self.STATE_QUIZ
                self.current_question = 0
                self.score = 0
                self.feedback_text = ""
                self.feedback_pending = False

        if self.feedback_pending:
            now = pygame.time.get_ticks()
            if now - self.feedback_time > 1200:
                self.feedback_text = ""
                self.feedback_pending = False
                self.current_question += 1
                if self.current_question >= len(self.questions):
                    self.state = self.STATE_RESULT

    def draw(self):
        if self.state in (self.STATE_QUIZ_COUNTDOWN, self.STATE_QUIZ, self.STATE_RESULT):
            self.screen.blit(self.quiz_bg, (0, 0))
        else:
            self.screen.blit(self.farm_bg, (0, 0))

        if self.state == self.STATE_CROP_SELECT:
            self.draw_text("Choose a crop to plant:", 250, 80)
            self.draw_button("Wheat", pygame.Rect(120, 420, 150, 50), self.GREEN)
            self.draw_button("Rice", pygame.Rect(320, 420, 150, 50), self.GREEN)
            self.draw_button("Cotton", pygame.Rect(520, 420, 150, 50), self.GREEN)

            # Always show three crop images above the buttons
            self.screen.blit(self.wheat_img, (120, 220))
            self.draw_text("Wheat", 145, 350, self.BLACK)
            self.screen.blit(self.rice_img, (320, 220))
            self.draw_text("Rice", 365, 350, self.BLACK)
            self.screen.blit(self.cotton_img, (520, 220))
            self.draw_text("Cotton", 555, 350, self.BLACK)

        elif self.state == self.STATE_IRRIGATION:
            self.draw_text(f"Crop: {self.selected_crop}", 350, 80)
            self.draw_text("Choose irrigation method:", 250, 130)
            self.draw_button("Canal", pygame.Rect(180, 420, 150, 50), self.GRAY)
            self.draw_button("Sprinkler", pygame.Rect(340, 420, 150, 50), self.GRAY)
            self.draw_button("Drip", pygame.Rect(500, 420, 150, 50), self.GRAY)

            # Show only the selected crop above the irrigation choices
            if self.selected_crop == "Wheat":
                self.screen.blit(self.wheat_img, (340, 200))
            elif self.selected_crop == "Rice":
                self.screen.blit(self.rice_img, (340, 200))
            elif self.selected_crop == "Cotton":
                self.screen.blit(self.cotton_img, (340, 200))

            self.screen.blit(self.canal_img, (180, 275))
            self.screen.blit(self.sprinkler_img, (340, 275))
            self.screen.blit(self.drip_img, (500, 275))

        elif self.state == self.STATE_HARVEST:
            self.draw_text("Crop is ready to harvest!", 270, 80)
            self.screen.blit(self.harvest_img, (325, 150))
            self.draw_button("Harvest", pygame.Rect(300, 450, 200, 50), self.GRAY)

        elif self.state == self.STATE_QUIZ_COUNTDOWN:
            elapsed = (pygame.time.get_ticks() - self.quiz_countdown_start) / 1000.0
            remaining = max(0, int(self.quiz_countdown_length - elapsed))
            self.draw_text(f"Quiz starting in: {remaining}", 250, self.H // 2 - 50, self.BLACK, self.big_font)

        elif self.state == self.STATE_QUIZ:
            question = self.questions[self.current_question]
            self.draw_text(f"Q{self.current_question + 1}: {question['q']}", 60, 50)
            for i, option in enumerate(question["options"]):
                self.draw_button(option, pygame.Rect(150, 150 + i*100, 500, 50), self.LIGHT_GREEN)
            pygame.draw.line(self.screen, self.BLACK, (50, 120), (750, 120), 2)

            if self.feedback_text:
                col = self.GREEN if "Correct" in self.feedback_text else self.RED
                self.draw_text(self.feedback_text, 150, 520, col)

        elif self.state == self.STATE_RESULT:
            self.draw_text("Quiz Completed!", 320, 150)
            self.draw_text(f"Your Score: {self.score}/3", 330, 200)
            self.draw_button("Restart", pygame.Rect(340, 400, 120, 50), self.GRAY)
            self.draw_button("Back to Challenges", self.back_button_rect, self.GRAY)
            self.draw_button("Government Schemes Info", self.gov_info_button_rect, self.RED)
            self.draw_button("Next Level", self.next_level_button_rect, self.GREEN)
