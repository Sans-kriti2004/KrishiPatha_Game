# screens/levels/level1.py
import pygame, os, time, math

# --------- WELCOME SCREEN ---------
class Level1Welcome:
    def __init__(self, screen, set_screen_callback):
        self.screen = screen
        self.set_screen = set_screen_callback
        self.W, self.H = self.screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 24)
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))
        bg_path = os.path.join(self.assets, "welcome_bg.jpg")
        try:
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (self.W, self.H))
        except:
            self.bg_img = pygame.Surface((self.W, self.H))
            self.bg_img.fill((200, 200, 200))
        self.continue_button = pygame.Rect(self.W//2 - 100, self.H - 100, 200, 50)

    def draw_text_with_bg(self, text, font, color, x, y, padding=6):
        txt_surf = font.render(text, True, color)
        rect = txt_surf.get_rect(topleft=(x, y))
        bg_rect = pygame.Rect(rect.x - padding, rect.y - padding, rect.width + 2*padding, rect.height + 2*padding)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=6)
        self.screen.blit(txt_surf, rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                self.set_screen(Level1Drought(self.screen, self.set_screen))

    def update(self):
        pass

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
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 16)
        base = os.path.dirname(__file__)
        self.assets = os.path.abspath(os.path.join(base, "..", "..", "extras", "level1"))
        self.bg_img = self._load_image("drought_bg.jpg", (self.W, self.H), fill=(210,180,140))
        self.river_width = max(120, self.W // 4)
        self.river_img = self._load_image("river.png", (self.river_width, self.H), fill=(0,100,255))
        self.river_y = 0
        self.river_speed = 0.12
        self.sun_img = self._load_image("sun.png", (110,110), fill=(255,200,0))
        self.sun_angle = 0
        self.sun_bob = 0
        self.field_w, self.field_h = 300, 230
        self.field_img = self._load_image("field.jpg", (self.field_w, self.field_h), fill=(139,69,19))
        self.field_rect = pygame.Rect(self.W - (self.field_w + 40), self.H - (self.field_h + 30), self.field_w, self.field_h)
        self.farmer_img = self._load_image("farmer.png", (110,170), fill=(0,200,0))
        self.farmer_img_left = pygame.transform.flip(self.farmer_img, True, False)
        self.farmer_rect = self.farmer_img.get_rect(center=(self.W // 2, self.H // 2))
        self.farmer_speed = 5
        self.facing_left = False
        self.total_time = 300
        self.start_time = time.time()
        self.max_water = 100.0
        self.current_water = self.max_water
        self.water_drain_rate = 0.02
        self.crop_plots = []
        self.mulched_plots = set()
        self.init_crop_plots()
        self.sustain = 50
        self.yield_score = 50
        self.efficiency = 50
        self.state = "playing"
        self.feedback_msg = ""
        self.feedback_timer = 0.0
        self.questions_order = ["irrigation", "soil", "allocation", "mulch", "timing"]
        self.questions_data = {
            "irrigation": {
                "q": "What irrigation system will you set up?",
                "choices": [
                    {"t":"Drip Irrigation", "fx":{"drain":0.008,"sustain":+5,"eff":+5}, "fb":"Pipes installed — efficient use."},
                    {"t":"Sprinkler", "fx":{"drain":0.018,"sustain":0,"eff":0}, "fb":"Sprinkler heads placed."},
                    {"t":"Flood", "fx":{"drain":0.06,"sustain":-8,"eff":-12}, "fb":"Flooding — high wastage!"}
                ],
                "zone":"river"
            },
            "soil": {
                "q":"How will you check soil moisture?",
                "choices":[
                    {"t":"Moisture Sensor", "fx":{"sustain":+3}, "fb":"Sensor gives accurate reading."},
                    {"t":"Visual Check", "fx":{"sustain":-1}, "fb":"Looks dry on top."},
                    {"t":"Dig & Touch", "fx":{"sustain":0}, "fb":"Approximate reading."}
                ],
                "zone":"field"
            },
            "allocation": {
                "q":"Which crops will you irrigate first?",
                "choices":[
                    {"t":"High-Value Crops", "fx":{"yield":+15,"sustain":-5}, "fb":"Boost to cash crops."},
                    {"t":"Drought-Resistant", "fx":{"yield":+5,"sustain":+5}, "fb":"Good planning choice."},
                    {"t":"All Equally", "fx":{"yield":-5,"sustain":0}, "fb":"Water spread thin; low yields."}
                ],
                "zone":"field"
            },
            "mulch": {
                "q":"Apply mulch to save soil moisture?",
                "choices":[
                    {"t":"Yes", "fx":{"sustain":+7}, "fb":"Mulch will reduce evaporation."},
                    {"t":"No", "fx":{"sustain":-5}, "fb":"Soil loses water quickly without mulch."},
                    {"t":"Maybe later", "fx":{"sustain":-1}, "fb":"Delaying mulch risks more loss."}
                ],
                "zone":"field"
            },
            "timing": {
                "q":"When will you irrigate?",
                "choices":[
                    {"t":"Early Morning", "fx":{"eff":+10,"sustain":+5}, "fb":"Best choice — minimal evaporation."},
                    {"t":"Afternoon", "fx":{"eff":-8,"sustain":-5}, "fb":"Hot sun causes heavy evaporation."},
                    {"t":"Night", "fx":{"eff":-2,"sustain":0}, "fb":"Moderate water use; watch disease risk."}
                ],
                "zone":"river"
            }
        }
        self.current_q_index = 0
        self.pending_question_key = None
        self.choice_buttons = []
        self.popup_box = None
        self.summary_ready = False
        self.summary_time = 0.0

    def _load_image(self, name, size=None, fill=None):
        path = os.path.join(self.assets, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except Exception:
            s = pygame.Surface(size if size else (50,50), pygame.SRCALPHA)
            if fill:
                s.fill(fill)
            else:
                s.fill((200,200,200))
            return s

    def init_crop_plots(self):
        self.crop_plots.clear()
        padding = 12
        inner_w = self.field_w - padding*2
        inner_h = self.field_h - padding*2
        cols, rows = 2, 2
        plot_w = inner_w // cols
        plot_h = inner_h // rows
        field_x = self.field_rect.left
        field_y = self.field_rect.top
        for r in range(rows):
            for c in range(cols):
                x = field_x + padding + c * plot_w
                y = field_y + padding + r * plot_h
                rect = pygame.Rect(x + 8, y + 6, plot_w - 16, plot_h - 14)
                self.crop_plots.append({"rect": rect, "watered": 0.0, "mulched": False, "sprout": False})

    def feedback(self, text, ttl=2.0):
        self.feedback_msg = text
        self.feedback_timer = time.time() + ttl

    def open_question(self, key):
        if self.state != "playing":
            return
        self.state = "question"
        self.pending_question_key = key
        self.choice_buttons = []
        self.popup_box = None

    def apply_choice(self, choice):
        fx = choice.get("fx", {})
        if "drain" in fx:
            self.water_drain_rate = fx["drain"]
        if "sustain" in fx:
            self.sustain = max(0, min(100, self.sustain + fx["sustain"]))
        if "yield" in fx:
            self.yield_score = max(0, min(100, self.yield_score + fx["yield"]))
        if "eff" in fx:
            self.efficiency = max(0, min(100, self.efficiency + fx["eff"]))
        self.feedback(choice.get("fb", ""), ttl=2.5)
        self.current_q_index += 1
        self.pending_question_key = None
        self.popup_box = None
        if self.current_q_index >= len(self.questions_order):
            self.prepare_summary()
        else:
            self.state = "feedback"
            self.summary_time = time.time() + 0.6

    def prepare_summary(self):
        remaining_percent = (self.current_water / self.max_water) * 100.0
        self.efficiency = int((self.efficiency + remaining_percent) / 2)
        self.summary_ready = True
        self.summary_time = time.time() + 0.8
        self.state = "feedback"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "question" and self.popup_box:
                mx, my = event.pos
                for rect, choice in self.choice_buttons:
                    if rect.collidepoint((mx,my)):
                        self.apply_choice(choice)
                        return
            if self.state == "playing":
                mx, my = event.pos
                for p in self.crop_plots:
                    if p["rect"].collidepoint((mx,my)):
                        dist = math.hypot(self.farmer_rect.centerx - p["rect"].centerx, self.farmer_rect.centery - p["rect"].centery)
                        if dist < 160 and self.current_water >= 6:
                            p["watered"] = min(100.0, p["watered"] + 20.0)
                            p["sprout"] = True
                            self.current_water = max(0.0, self.current_water - 6.0)
                            self.feedback("You watered a plot.", ttl=1.8)
                        else:
                            self.feedback("Too far or not enough water.", ttl=1.5)
                        return
            if self.state == "summary":
                try:
                    self.set_screen(None)
                except:
                    pass

    def update(self):
        now = time.time()
        elapsed = now - self.start_time
        if elapsed >= self.total_time and not self.summary_ready:
            self.prepare_summary()
        self.river_y = (self.river_y - self.river_speed) % self.H
        self.sun_angle = (self.sun_angle + 0.25) % 360
        self.sun_bob = math.sin(now * 0.9) * 4.0
        mulch_factor = 0.9 if len(self.mulched_plots) > 0 else 1.0
        self.current_water = max(0.0, self.current_water - (getattr(self, "water_drain_rate", self.water_drain_rate) * mulch_factor))
        if self.feedback_msg and now > self.feedback_timer:
            self.feedback_msg = ""
        if self.state == "playing":
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
            left_limit = self.river_width + 6
            if self.farmer_rect.left < left_limit:
                self.farmer_rect.left = left_limit
            right_limit = self.field_rect.left - 30
            if self.farmer_rect.right > right_limit:
                self.farmer_rect.right = right_limit
            top_limit = 80
            if self.farmer_rect.top < top_limit:
                self.farmer_rect.top = top_limit
            bottom_limit = self.H - 60
            if self.farmer_rect.bottom > bottom_limit:
                self.farmer_rect.bottom = bottom_limit
            if self.current_q_index < len(self.questions_order) and not self.pending_question_key:
                key = self.questions_order[self.current_q_index]
                qdata = self.questions_data.get(key)
                if not qdata:
                    self.current_q_index += 1
                else:
                    zone = qdata.get("zone", "field")
                    if zone == "river":
                        if self.farmer_rect.colliderect(pygame.Rect(0, 0, self.river_width + 8, self.H)):
                            self.open_question(key)
                    elif zone == "field":
                        if self.farmer_rect.colliderect(self.field_rect):
                            self.open_question(key)
        elif self.state == "question":
            pass
        elif self.state == "feedback":
            if self.summary_ready and now >= self.summary_time:
                self.state = "summary"
            elif not self.summary_ready and now >= self.feedback_timer:
                self.state = "playing"

    def draw(self):
        self.screen.blit(self.bg_img, (0,0))
        self.screen.blit(self.river_img, (0, self.river_y - self.H))
        self.screen.blit(self.river_img, (0, self.river_y))
        rotated = pygame.transform.rotate(self.sun_img, self.sun_angle)
        rrect = rotated.get_rect()
        rrect.topright = (self.W - 18, 18 + int(self.sun_bob))
        self.screen.blit(rotated, rrect)
        self.screen.blit(self.field_img, (self.field_rect.x, self.field_rect.y))
        for p in self.crop_plots:
            rect = p["rect"]
            pygame.draw.rect(self.screen, (60,120,40), rect, 3, border_radius=6)
            if p["mulched"]:
                overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                overlay.fill((40,20,0,110))
                self.screen.blit(overlay, (rect.x, rect.y))
            if p["sprout"]:
                spr = pygame.Surface((min(30, rect.w//3), min(30, rect.h//3)), pygame.SRCALPHA)
                pygame.draw.circle(spr, (40,180,40), (spr.get_width()//2, spr.get_height()//2), spr.get_width()//2)
                spr_rect = spr.get_rect(center=(rect.centerx, rect.centery))
                self.screen.blit(spr, spr_rect)
        farmer_draw = self.farmer_img_left if self.facing_left else self.farmer_img
        farmer_rect_draw = farmer_draw.get_rect(center=self.farmer_rect.center)
        self.screen.blit(farmer_draw, farmer_rect_draw)
        elapsed = int(time.time() - self.start_time)
        rem = max(0, self.total_time - elapsed)
        m, s = divmod(rem, 60)
        ttxt = self.large_font.render(f"Time Left: {m:02}:{s:02}", True, (255,255,255))
        self.screen.blit(ttxt, (self.W//2 - ttxt.get_width()//2, 10))
        bar_w, bar_h = 200, 26
        bx, by = 18, 18
        pygame.draw.rect(self.screen, (180,180,180), (bx,by,bar_w,bar_h), border_radius=6)
        ww = int((self.current_water / self.max_water) * bar_w)
        pygame.draw.rect(self.screen, (0,120,255), (bx,by,ww,bar_h), border_radius=6)
        self.screen.blit(self.text_font.render("Water", True, (0,0,0)), (bx, by + bar_h + 6))
        hud_x = self.W - 260; hud_y = 18
        pygame.draw.rect(self.screen, (255,255,255,180), (hud_x, hud_y, 240, 110), border_radius=8)
        self.screen.blit(self.text_font.render(f"Sustainability: {int(self.sustain)}", True, (34,139,34)), (hud_x+12, hud_y+8))
        self.screen.blit(self.text_font.render(f"Yield: {int(self.yield_score)}", True, (160,82,45)), (hud_x+12, hud_y+36))
        self.screen.blit(self.text_font.render(f"Water Efficiency: {int(self.efficiency)}", True, (30,90,180)), (hud_x+12, hud_y+64))
        if self.feedback_msg:
            fb = self.text_font.render(self.feedback_msg, True, (255,215,0))
            fb_bg = fb.get_rect(center=(self.W//2, self.H - 60))
            pygame.draw.rect(self.screen, (0,0,0), (fb_bg.x-12, fb_bg.y-8, fb_bg.w+24, fb_bg.h+14), border_radius=8)
            self.screen.blit(fb, (fb_bg.x+12, fb_bg.y+2))
        if self.state == "fetching_water":
            msg = self.large_font.render("Filling bucket with water...", True, (255,255,255))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//2))
        if self.state == "pouring_field":
            msg = self.large_font.render("Pouring water in the field...", True, (255,255,255))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//2))
        if self.state == "question" and self.pending_question_key:
            q = self.questions_data[self.pending_question_key]
            box_w, box_h = 640, 320
            box = pygame.Rect(self.W//2 - box_w//2, self.H//2 - box_h//2, box_w, box_h)
            self.popup_box = box
            pygame.draw.rect(self.screen, (255,255,255), box, border_radius=12)
            pygame.draw.rect(self.screen, (20,20,20), box, 3, border_radius=12)
            qtxt = self.large_font.render(q["q"], True, (10,10,10))
            self.screen.blit(qtxt, (box.centerx - qtxt.get_width()//2, box.top + 18))
            y = box.top + 90
            self.choice_buttons = []
            for choice in q["choices"]:
                rect = pygame.Rect(box.centerx - 180, y, 360, 56)
                pygame.draw.rect(self.screen, (30,144,255), rect, border_radius=10)
                txt = self.text_font.render(choice["t"], True, (255,255,255))
                self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
                self.choice_buttons.append((rect, choice))
                y += 76
        if self.state == "summary":
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            self.screen.blit(overlay, (0,0))
            card_w, card_h = 720, 420
            card = pygame.Rect(self.W//2 - card_w//2, self.H//2 - card_h//2, card_w, card_h)
            pygame.draw.rect(self.screen, (255,255,255), card, border_radius=12)
            pygame.draw.rect(self.screen, (0,0,0), card, 3, border_radius=12)
            title = self.large_font.render("Yay! You completed the level", True, (20,120,20))
            self.screen.blit(title, (card.centerx - title.get_width()//2, card.top + 24))
            lines = [
                f"Irrigation choice affected water drain rate.",
                f"Mulch applied: {len(self.mulched_plots)} plots.",
                f"Final sustainability, yield and water efficiency below."
            ]
            y = card.top + 90
            for ln in lines:
                t = self.text_font.render("• " + ln, True, (40,40,40))
                self.screen.blit(t, (card.left + 40, y))
                y += 36
            s1 = self.text_font.render(f"Sustainability: {int(self.sustain)}", True, (34,139,34))
            s2 = self.text_font.render(f"Yield: {int(self.yield_score)}", True, (160,82,45))
            s3 = self.text_font.render(f"Water Efficiency: {int(self.efficiency)}", True, (30,90,180))
            self.screen.blit(s1, (card.left + 40, y + 10))
            self.screen.blit(s2, (card.left + 40, y + 46))
            self.screen.blit(s3, (card.left + 40, y + 82))
            link_txt = self.small_font.render("Learn more: visit relevant gov drought-protection schemes (click anywhere to return).", True, (10,10,10))
            self.screen.blit(link_txt, (card.left + 40, card.bottom - 56))
