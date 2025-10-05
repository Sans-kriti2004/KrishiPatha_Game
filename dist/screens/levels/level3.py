import pygame
import os
import webbrowser

class Level3:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()

        # Colors and fonts
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 150, 0)
        self.RED = (220, 50, 50)
        self.LIGHT_GREEN = (144, 238, 144)
        self.GRAY = (200, 200, 200)
        self.DARK_BLUE = (10, 30, 80)
        self.BUTTON_BG = (0, 0, 0, 110)
        self.font = pygame.font.Font(None, 34)
        self.big_font = pygame.font.Font(None, 72)

        # States
        self.STATE_QUIZ_COUNTDOWN = "quiz_countdown"
        self.STATE_QUIZ = "quiz"
        self.STATE_RESULT = "result"

        self.state = self.STATE_QUIZ_COUNTDOWN
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False
        self.feedback_time = 0
        self.quiz_countdown_start = 0
        self.quiz_countdown_length = 3

        # Paths and quiz background, with debug print
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))
        quiz_bg_path = os.path.join(self.assets, "quiz_bg3.png")
        print("Quiz background path:", quiz_bg_path)
        try:
            self.quiz_bg = pygame.image.load(quiz_bg_path)
            self.quiz_bg = pygame.transform.scale(self.quiz_bg, (self.W, self.H))
        except Exception as e:
            print("Failed to load quiz_bg.png:", e)
            self.quiz_bg = None

        # Button rects for result screen
        self.replay_button_rect = pygame.Rect(200, 400, 160, 50)
        self.back_button_rect = pygame.Rect(20, 20, 200, 40)
        self.gov_info_button_rect = pygame.Rect(300, 500, 300, 50)
        self.next_level_button_rect = pygame.Rect(620, 500, 220, 50)

        #quiz questions
        self.questions = self.questions = [
    {
        "q": "Which combination of agricultural practices is a primary cause of soil structure decline and the loss of beneficial soil organic matter (SOM)?",
        "options": [
            "Crop rotation and perennial planting.",
            "Excessive tillage and monocropping (planting the same crop repeatedly).",
            "Planting legumes and applying composted manure.",
            "Contour farming and establishing windbreaks."
        ],
        "answer": "Excessive tillage and monocropping (planting the same crop repeatedly)."
    },
    {
        "q": "What is the most effective biological strategy for a farmer to increase soil organic matter (SOM) and improve aggregation in degraded, low-residue land?",
        "options": [
            "Applying chemical fertilizers heavily to boost biomass growth.",
            "Implementing diverse crop rotations and planting cover crops (green manures).",
            "Allowing the land to remain bare fallow for an entire season.",
            "Regularly using heavy machinery for deep subsoiling."
        ],
        "answer": "Implementing diverse crop rotations and planting cover crops (green manures)."
    },
    {
        "q": "For a field suffering from soil salinity (accumulation of soluble salts), which intervention is necessary before any other corrective measure can be successful?",
        "options": [
            "Planting salt-tolerant rice varieties.",
            "Adding large amounts of lime to the soil.",
            "Ensuring adequate subsurface drainage to allow for leaching.",
            "Applying nitrogen fertilizer at double the recommended rate."
        ],
        "answer": "Ensuring adequate subsurface drainage to allow for leaching."
    },
    {
        "q": "A soil test shows a field has a highly acidic pH (below 5.0), leading to aluminum toxicity and reduced nutrient availability. The most common and practical corrective measure is to apply:",
        "options": [
            "Gypsum (Calcium Sulfate).",
            "Sulfur powder.",
            "Organic compost only.",
            "Calcitic or Dolomitic Limestone."
        ],
        "answer": "Calcitic or Dolomitic Limestone."
    },
    {
        "q": "On steep, degraded agricultural hillsides that experience heavy rainfall runoff, which physical conservation technique is most effective at interrupting water flow and creating a series of level planting areas?",
        "options": [
            "No-till farming.",
            "Terracing.",
            "Establishing windbreaks.",
            "Contour plowing (without shaping the land)."
        ],
        "answer": "Terracing."
    }
]



    def draw_text(self, text, x, y, color=None, font=None):
        font = font or self.font
        color = color or self.BLACK
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def draw_wrapped_text(self, text, rect, color=None):
        color = color or self.BLACK
        words = text.split(' ')
        space_width, space_height = self.font.size(' ')
        max_width = rect.width - 20  # padding
        x, y = rect.topleft
        line = ''
        for word in words:
            test_line = line + word + ' '
            test_width, _ = self.font.size(test_line)
            if test_width <= max_width:
                line = test_line
            else:
                render_line = self.font.render(line, True, color)
                self.screen.blit(render_line, (x + 10, y))
                y += space_height + 5
                line = word + ' '
        if line:
            render_line = self.font.render(line, True, color)
            self.screen.blit(render_line, (x + 10, y))

    def draw_button(self, text, rect, color):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.BUTTON_BG)
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(self.screen, self.DARK_BLUE, rect, 2, border_radius=8)
        self.draw_wrapped_text(text, rect, color=pygame.Color('white'))

    def restart_game(self):
        self.state = self.STATE_QUIZ_COUNTDOWN
        self.score = 0
        self.current_question = 0
        self.feedback_text = ""
        self.feedback_pending = False
        self.quiz_countdown_start = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.state == self.STATE_RESULT:
                if self.replay_button_rect.collidepoint(x, y):
                    self.restart_game()
                    return
                if self.back_button_rect.collidepoint(x, y):
                    if self.set_screen:
                        from screens.challenge import ChallengePage
                        self.set_screen(ChallengePage(self.screen, self.set_screen))
                    return
                if self.gov_info_button_rect.collidepoint(x, y):
                    webbrowser.open("https://agriwelfare.gov.in/")
                    return
                if self.next_level_button_rect.collidepoint(x, y):
                    print("Next level button clicked - implement level transition")
                    return

            elif self.state == self.STATE_QUIZ and not self.feedback_pending:
                for i, option in enumerate(self.questions[self.current_question]["options"]):
                    oy_start = 150 + i * 90
                    oy_end = oy_start + 50
                    if oy_start <= y <= oy_end:
                        if option == self.questions[self.current_question]["answer"]:
                            self.feedback_text = "Correct!"
                            self.score += 1
                        else:
                            self.feedback_text = f"The answer was: {self.questions[self.current_question]['answer']}"
                        self.feedback_pending = True
                        self.feedback_time = pygame.time.get_ticks()
                        break

    def update(self):
        if self.state == self.STATE_QUIZ_COUNTDOWN:
            if self.quiz_countdown_start == 0:
                self.quiz_countdown_start = pygame.time.get_ticks()
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
        if self.quiz_bg:
            self.screen.blit(self.quiz_bg, (0, 0))
        else:
            self.screen.fill(self.WHITE)

        if self.state == self.STATE_QUIZ_COUNTDOWN:
            elapsed = (pygame.time.get_ticks() - self.quiz_countdown_start) / 1000.0
            remaining = max(0, int(self.quiz_countdown_length - elapsed))
            self.draw_text(f"Flood Quiz starting in: {remaining}", 210, self.H // 2 - 40, self.BLACK, self.big_font)

        elif self.state == self.STATE_QUIZ:
            question = self.questions[self.current_question]
            question_rect = pygame.Rect(60, 30, 700, 100)  # width and height to contain question text nicely
            self.draw_wrapped_text(f"Q{self.current_question + 1}: {question['q']}", question_rect, self.BLACK)

            for i, option in enumerate(question["options"]):
                self.draw_button(option, pygame.Rect(150, 150 + i * 90, 600, 70), self.LIGHT_GREEN)
            pygame.draw.line(self.screen, self.BLACK, (50, 120), (750, 120), 2)
            if self.feedback_text:
                color = self.GREEN if "Correct" in self.feedback_text else self.RED
                self.draw_text(self.feedback_text, 180, 550, color)

        elif self.state == self.STATE_RESULT:
            self.draw_text("Flood Quiz Completed!", 260, 150, self.BLACK, self.big_font)
            self.draw_text(f"Your Score: {self.score}/{len(self.questions)}", 320, 230, self.GREEN, self.font)

            self.draw_button("Replay", self.replay_button_rect, self.GRAY)
            self.draw_button("Back to Challenges", self.back_button_rect, self.GRAY)
            self.draw_button("Government Schemes Info", self.gov_info_button_rect, self.RED)
            self.draw_button("Next Level", self.next_level_button_rect, self.GREEN)
