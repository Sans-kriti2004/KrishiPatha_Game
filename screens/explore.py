import pygame
import os
import math
import json
import time

pygame.font.init()

# ---------- Simulated datasets & simple recommendation logic ----------
# Replace these with actual dataset loads or API calls.
SAMPLE_ENVIRONMENTS = {
    "default": {"soil": "loamy", "avg_rainfall": 700, "avg_temp": 25, "water_source": "river"},
    "new delhi": {"soil": "sandy", "avg_rainfall": 600, "avg_temp": 30, "water_source": "tube well"},
    "up farm": {"soil": "clay", "avg_rainfall": 900, "avg_temp": 23, "water_source": "river"}
}

SAMPLE_CROPS = [
    {"name": "Wheat", "soils": ["loamy", "clay"], "min_temp": 10, "max_temp": 30, "water_need": "medium"},
    {"name": "Millet", "soils": ["sandy", "loamy"], "min_temp": 20, "max_temp": 40, "water_need": "low"},
    {"name": "Rice", "soils": ["clay"], "min_temp": 20, "max_temp": 35, "water_need": "high"},
    {"name": "Maize", "soils": ["loamy"], "min_temp": 15, "max_temp": 35, "water_need": "medium"}
]

SAMPLE_LIVESTOCK = [
    {"name": "Goat", "climate_tolerance": (5, 45), "feed_needs": "low"},
    {"name": "Cow", "climate_tolerance": (0, 40), "feed_needs": "high"},
    {"name": "Chicken", "climate_tolerance": (0, 40), "feed_needs": "low"}
]


def recommend_crops(env):
    """Simple scoring-based recommendation (placeholder for ML)."""
    soil = env.get("soil")
    temp = env.get("avg_temp", 25)
    recs = []
    for c in SAMPLE_CROPS:
        score = 0
        if soil in c["soils"]:
            score += 30
        # temperature match
        if c["min_temp"] <= temp <= c["max_temp"]:
            score += 30
        # lower water need preferred in drought
        wf = {"low": 20, "medium": 10, "high": 0}
        score += wf.get(c["water_need"], 0)
        recs.append((score, c))
    recs.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in recs[:3]]


def recommend_livestock(env):
    temp = env.get("avg_temp", 25)
    recs = []
    for a in SAMPLE_LIVESTOCK:
        min_t, max_t = a["climate_tolerance"]
        score = 0
        if min_t <= temp <= max_t:
            score += 40
        if a["feed_needs"] == "low":
            score += 10
        recs.append((score, a))
    recs.sort(reverse=True, key=lambda x: x[0])
    return [a for _, a in recs[:2]]


# ---------- Helper UI utilities ----------
def draw_text(surface, text, font, color, pos):
    surf = font.render(text, True, color)
    surface.blit(surf, pos)
    return surf.get_rect(topleft=pos)


def center_text(surface, text, font, color, rect):
    surf = font.render(text, True, color)
    pos = (rect.x + (rect.w - surf.get_width()) // 2, rect.y + (rect.h - surf.get_height()) // 2)
    surface.blit(surf, pos)
    return surf.get_rect(topleft=pos)


# small helper to clamp a point inside a rect with margin
def clamp_point_to_rect(pt, rect, margin=6):
    x = max(rect.left + margin, min(int(pt[0]), rect.right - margin))
    y = max(rect.top + margin, min(int(pt[1]), rect.bottom - margin))
    return (x, y)


# ---------- Screens ----------
class ExplorePage:
    """Initial entry screen for Explore Mode."""
    def __init__(self, screen, set_screen):
        self.screen = screen
        self.set_screen = set_screen
        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.start_btn = pygame.Rect(self.W // 2 - 120, self.H - 140, 240, 56)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_btn.collidepoint(event.pos):
                self.set_screen(ExploreMap(self.screen, self.set_screen))

    def update(self):
        pass

    def draw(self):
        self.screen.fill((28, 58, 45))
        draw_text(self.screen, "Explore Mode — Real-time Farm Planner", self.title_font, (255, 255, 255), (40, 40))
        y = 100
        bullets = [
            "Select a location (type or click).",
            "Draw your field plot on the map.",
            "Get crop & livestock recommendations based on environment.",
            "Learn stage-by-stage farming & sustainability tips."
        ]
        for b in bullets:
            draw_text(self.screen, "• " + b, self.text_font, (220, 220, 220), (60, y))
            y += 36

        # Start button
        pygame.draw.rect(self.screen, (40, 160, 100), self.start_btn, border_radius=10)
        center_text(self.screen, "Start Explore", self.text_font, (255, 255, 255), self.start_btn)


class ExploreMap:
    """Map-like interface where user picks a location by typing or clicking."""
    def __init__(self, screen, set_screen):
        self.screen = screen
        self.set_screen = set_screen
        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # simple placeholder 'map' (we use blank background) — replace with tile or static map image
        self.map_rect = pygame.Rect(40, 100, self.W - 80, self.H - 220)

        # location input
        self.input_active = False
        self.input_rect = pygame.Rect(60, 40, 360, 36)
        self.input_text = ""
        self.hint = "Type a location name (e.g. 'New Delhi') or click on map"

        # last clicked coordinate on "map" (in map-space)
        self.clicked_point = None

        # proceed button
        self.next_btn = pygame.Rect(self.W - 200, self.H - 70, 160, 48)

        # sample env chosen
        self.env = SAMPLE_ENVIRONMENTS["default"]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

            if self.map_rect.collidepoint(event.pos):
                # click -> set clicked_point
                mx, my = event.pos
                # normalize to map coords or just store pixel coords
                # clamp the clicked point inside the map area (visual safety)
                self.clicked_point = clamp_point_to_rect((mx, my), self.map_rect, margin=6)

                # set env detection by clicking -> simulate env by snapping to a name
                cx = mx - self.map_rect.x
                if cx < (self.map_rect.w // 2):
                    self.env = SAMPLE_ENVIRONMENTS.get("up farm")
                else:
                    self.env = SAMPLE_ENVIRONMENTS.get("new delhi")
            if self.next_btn.collidepoint(event.pos):
                # finalize: if typed location, try to map; else use clicked_point
                loc_key = self.input_text.strip().lower()
                env = SAMPLE_ENVIRONMENTS.get(loc_key)
                if env:
                    self.env = env
                # pass environment and clicked_point to next screen
                # clicked_point may be None -> ExplorePlot handles None
                self.set_screen(ExplorePlot(self.screen, self.set_screen, env=self.env, start_point=self.clicked_point))

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                # same as pressing Next
                loc_key = self.input_text.strip().lower()
                env = SAMPLE_ENVIRONMENTS.get(loc_key, SAMPLE_ENVIRONMENTS["default"])
                self.env = env
                self.set_screen(ExplorePlot(self.screen, self.set_screen, env=self.env, start_point=self.clicked_point))
            else:
                if len(self.input_text) < 50:
                    self.input_text += event.unicode

    def update(self):
        pass

    def draw(self):
        self.screen.fill((18, 40, 26))
        draw_text(self.screen, "Select Location on Map", self.title_font, (255, 255, 255), (40, 16))

        # input box
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=6)
        txt = self.input_text if self.input_text else self.hint
        color = (0, 0, 0) if self.input_text else (120, 120, 120)
        draw_text(self.screen, txt, self.text_font, color, (self.input_rect.x + 8, self.input_rect.y + 6))

        # draw map area
        pygame.draw.rect(self.screen, (80, 120, 80), self.map_rect)
        # draw a faint grid for feel
        for x in range(self.map_rect.left, self.map_rect.right, 60):
            pygame.draw.line(self.screen, (70, 100, 70), (x, self.map_rect.top), (x, self.map_rect.bottom))
        for y in range(self.map_rect.top, self.map_rect.bottom, 60):
            pygame.draw.line(self.screen, (70, 100, 70), (self.map_rect.left, y), (self.map_rect.right, y))
        # show clicked point
        if self.clicked_point:
            pygame.draw.circle(self.screen, (255, 220, 60), self.clicked_point, 8)
            draw_text(self.screen, "Selected point", self.small_font, (255, 255, 255), (self.clicked_point[0] + 10, self.clicked_point[1] - 8))

        # env summary
        draw_text(self.screen, "Detected environment:", self.text_font, (220, 220, 220), (self.map_rect.left + 8, self.map_rect.bottom + 10))
        draw_text(self.screen, f"Soil: {self.env['soil']}, Rainfall: {self.env['avg_rainfall']} mm, Temp: {self.env['avg_temp']}°C", self.small_font, (210, 210, 210), (self.map_rect.left + 8, self.map_rect.bottom + 36))

        # Next button
        pygame.draw.rect(self.screen, (30, 140, 100), self.next_btn, border_radius=8)
        center_text(self.screen, "Plot Field", self.text_font, (255, 255, 255), self.next_btn)


class ExplorePlot:
    """Allow user to draw a polygon plot on the map area (click to add vertices)."""
    def __init__(self, screen, set_screen, env=None, start_point=None):
        self.screen = screen
        self.set_screen = set_screen
        self.env = env or SAMPLE_ENVIRONMENTS["default"]
        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.map_rect = pygame.Rect(40, 100, self.W - 80, self.H - 220)
        self.points = []
        self.is_finished = False
        # clamp and add start point if provided
        if start_point:
            self.points.append(clamp_point_to_rect(start_point, self.map_rect, margin=6))
        self.finish_btn = pygame.Rect(self.W - 220, self.H - 70, 180, 48)
        self.cancel_btn = pygame.Rect(self.W - 420, self.H - 70, 180, 48)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.finish_btn.collidepoint(event.pos) and len(self.points) >= 3:
                # compute simple polygon, finalize and proceed
                self.is_finished = True
                # send polygon (pixel coords) and env to next stage
                self.set_screen(ExploreStageLearning(self.screen, self.set_screen, env=self.env, polygon=self.points))
                return
            if self.cancel_btn.collidepoint(event.pos):
                self.set_screen(ExploreMap(self.screen, self.set_screen))
                return

            if self.map_rect.collidepoint(event.pos) and not self.is_finished:
                # clamp point inside map_rect (prevents plotting outside)
                mx = max(self.map_rect.left + 6, min(event.pos[0], self.map_rect.right - 6))
                my = max(self.map_rect.top + 6, min(event.pos[1], self.map_rect.bottom - 6))
                self.points.append((mx, my))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.points) >= 3:
                self.set_screen(ExploreStageLearning(self.screen, self.set_screen, env=self.env, polygon=self.points))
            if event.key == pygame.K_BACKSPACE and self.points:
                self.points.pop()

    def update(self):
        pass

    def draw(self):
        self.screen.fill((14, 40, 22))
        draw_text(self.screen, "Draw your plot: click to add vertices (Enter to finish, Backspace to undo)", self.title_font, (255, 255, 255), (40, 20))
        # map area
        pygame.draw.rect(self.screen, (55, 95, 55), self.map_rect)
        # draw partial polygon
        
        # Draw field outline if enough points exist
        if len(self.points) >= 2:
            pygame.draw.lines(self.screen, (150, 210, 150), False, self.points, 4)
        # Draw the points themselves
        for p in self.points:
            pygame.draw.circle(self.screen, (0, 200, 0), p, 6)

        # show simple centroid area estimate and info
        if len(self.points) >= 3:
            # compute polygon area (shoelace) - for display
            area = abs(sum(self.points[i][0] * self.points[(i + 1) % len(self.points)][1] - self.points[(i + 1) % len(self.points)][0] * self.points[i][1] for i in range(len(self.points)))) / 2.0
            draw_text(self.screen, f"Plot area (pixel units): {int(area)}", self.small_font, (230, 230, 230), (self.map_rect.left + 8, self.map_rect.top + 8))
        # buttons
        pygame.draw.rect(self.screen, (180, 60, 60), self.cancel_btn, border_radius=8)
        center_text(self.screen, "Back", self.small_font, (255, 255, 255), self.cancel_btn)
        pygame.draw.rect(self.screen, (30, 140, 80), self.finish_btn, border_radius=8)
        center_text(self.screen, "Confirm Plot", self.small_font, (255, 255, 255), self.finish_btn)


class ExploreStageLearning:
    """Main interactive stage:
    - shows the planted plot
    - recommends crops & livestock
    - user picks options stage-by-stage
    - includes a small chat assistant panel
    """
    def __init__(self, screen, set_screen, env=None, polygon=None):
        self.screen = screen
        self.set_screen = set_screen
        self.W, self.H = screen.get_size()
        self.env = env or SAMPLE_ENVIRONMENTS["default"]

        # layout
        self.map_rect = pygame.Rect(40, 100, int(self.W * 0.62), self.H - 160)
        self.side_rect = pygame.Rect(self.map_rect.right + 12, 100,
                                     self.W - self.map_rect.right - 52, self.map_rect.h)

        # clamp polygon
        self.polygon = [clamp_point_to_rect(p, self.map_rect, 6) for p in (polygon or [])]

        # fonts
        self.title_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)

        # recommendations
        self.crops_reco = recommend_crops(self.env)
        self.livestock_reco = recommend_livestock(self.env)

        # explanations
        self.reco_explanations = {
            "Wheat": "Wheat grows well in loamy and clay soils, tolerates moderate temperatures and needs medium water. Recommended for steady yields.",
            "Millet": "Millet is drought-tolerant, does well in sandy or loamy soils and requires low water. Good for dry conditions.",
            "Rice": "Rice prefers clay soils and high water; expect high water usage and high yield where water is available.",
            "Maize": "Maize likes loamy soils and warm weather; yields depend on timely irrigation."
        }
        self.livestock_explanations = {
            "Goat": "Goats are low-feed, hardy animals suitable for small holdings and dry areas.",
            "Cow": "Cows require higher feed but give milk and other outputs; need more care and water.",
            "Chicken": "Chickens are low-feed, quick-turn animals giving eggs and meat; simple housing needed."
        }

        # stages
        self.stages = ["irrigation", "soil", "allocation", "mulch", "timing"]
        self.stage_index = 0
        self.stage_state = "idle"
        self.stage_feedback = ""
        self.stage_feedback_until = 0

        # storage
        self.choices = {}
        self.choice_buttons = []

        # chat assistant
        self.chat_history = [("bot", "Hi! Ask me about crops, irrigation, or livestock for this location.")]
        self.chat_input = ""
        self.chat_active = False
        self.chat_rect = pygame.Rect(self.side_rect.x + 8,
                                     self.side_rect.bottom - 120,
                                     self.side_rect.w - 16, 28)

        # recommendation popup
        self.crop_rects = []
        self.livestock_rects = []
        self.selected_reco = None
        self.custom_input = ""
        self.reco_panel_rect = pygame.Rect(self.side_rect.x + 12, self.side_rect.y + 140,
                                           self.side_rect.w - 24, 180)

        # summary
        self.show_summary = False
        self.anim_until = 0

    # ------------------ Chat helper ------------------
    def bot_answer(self, q):
        q = q.lower()
        if "drip" in q or "irrigation" in q:
            return "Drip irrigation saves water by delivering it directly to roots."
        if "mulch" in q:
            return "Mulch reduces evaporation and keeps soil moist longer."
        if "livestock" in q:
            return "Goats need less feed than cows, making them good for dry areas."
        if "yield" in q:
            return "Yield depends on crop type, water use, and soil care."
        return "Use sensors & local weather data for best decisions. (Demo answer)"

    # ------------------ Events ------------------
    def handle_event(self, event):
        if self.show_summary:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.set_screen(None)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # clickable crop/livestock
            for name, rect in self.crop_rects:
                if rect.collidepoint((mx, my)):
                    self.selected_reco = ("crop", name)
                    return
            for name, rect in self.livestock_rects:
                if rect.collidepoint((mx, my)):
                    self.selected_reco = ("livestock", name)
                    return

            # popup buttons
            if self.selected_reco:
                panel = self.reco_panel_rect
                use_btn = pygame.Rect(panel.right - 140, panel.bottom - 36, 120, 28)
                custom_btn = pygame.Rect(panel.right - 280, panel.bottom - 36, 120, 28)
                input_rect = pygame.Rect(panel.x + 12, panel.bottom - 70, panel.w - 24, 26)

                if use_btn.collidepoint((mx, my)):
                    kind, name = self.selected_reco
                    self.choices[kind] = {"choice": name, "meta": {"applied_from": "recommended"}}
                    self.stage_feedback = f"Applied recommended {kind}: {name}"
                    self.stage_feedback_until = time.time() + 2.0
                    self.selected_reco = None
                    return
                if custom_btn.collidepoint((mx, my)):
                    if self.custom_input.strip():
                        choice_name = self.custom_input.strip().capitalize()
                        kind, _ = self.selected_reco
                        self.choices[kind] = {"choice": choice_name, "meta": {"applied_from": "custom"}}
                        self.stage_feedback = f"Applied custom {kind}: {choice_name}"
                        self.stage_feedback_until = time.time() + 2.0
                        self.custom_input = ""
                        self.selected_reco = None
                    return
                if input_rect.collidepoint((mx, my)):
                    self.chat_active = False  # switch focus
                    self.custom_active = True
                    return

            # stage buttons
            for rect, meta in self.choice_buttons:
                if rect.collidepoint((mx, my)):
                    self.apply_stage_choice(meta)
                    return

            # chat input/send
            chat_send_rect = pygame.Rect(self.side_rect.right - 82, self.side_rect.bottom - 32, 62, 24)
            chat_input_rect = pygame.Rect(self.side_rect.x + 8, self.side_rect.bottom - 32, self.side_rect.w - 90, 24)
            if chat_input_rect.collidepoint((mx, my)):
                self.chat_active = True
                return
            if chat_send_rect.collidepoint((mx, my)):
                if self.chat_input.strip():
                    self.chat_history.append(("user", self.chat_input.strip()))
                    self.chat_history.append(("bot", self.bot_answer(self.chat_input.strip())))
                    self.chat_input = ""
                    self.chat_active = False
                return

        elif event.type == pygame.KEYDOWN:
            if self.chat_active:
                if event.key == pygame.K_RETURN:
                    if self.chat_input.strip():
                        self.chat_history.append(("user", self.chat_input.strip()))
                        self.chat_history.append(("bot", self.bot_answer(self.chat_input.strip())))
                        self.chat_input = ""
                        self.chat_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                else:
                    self.chat_input += event.unicode
            elif self.selected_reco:  # typing custom choice
                if event.key == pygame.K_RETURN:
                    if self.custom_input.strip():
                        choice_name = self.custom_input.strip().capitalize()
                        kind, _ = self.selected_reco
                        self.choices[kind] = {"choice": choice_name, "meta": {"applied_from": "custom"}}
                        self.stage_feedback = f"Applied custom {kind}: {choice_name}"
                        self.stage_feedback_until = time.time() + 2.0
                        self.custom_input = ""
                        self.selected_reco = None
                elif event.key == pygame.K_BACKSPACE:
                    self.custom_input = self.custom_input[:-1]
                else:
                    self.custom_input += event.unicode

    # ------------------ Stage logic ------------------
    def start_stage_question(self):
        if self.stage_index >= len(self.stages):
            self.show_summary = True
            return
        self.choice_buttons.clear()
        # define choices like before
        # (omitted here to keep it short)

    def apply_stage_choice(self, meta):
        label = meta["label"]
        m = meta["meta"]
        self.choices[self.stages[self.stage_index]] = {"choice": label, "meta": m}
        self.stage_feedback = m.get("msg", "Choice applied.")
        self.stage_feedback_until = time.time() + 2.5
        self.stage_state = "answered"
        self.choice_buttons.clear()
        self.anim_until = time.time() + 2.5

    def next_stage(self):
        self.stage_index += 1
        self.stage_state = "idle"
        self.choice_buttons.clear()
        if self.stage_index < len(self.stages):
            self.start_stage_question()
        else:
            self.show_summary = True

    def update(self, dt=1/60):
        if self.stage_feedback and time.time() > self.stage_feedback_until:
            self.stage_feedback = ""
        if self.stage_state == "idle" and self.stage_index < len(self.stages):
            self.start_stage_question()
        if self.stage_state == "answered" and time.time() >= self.anim_until:
            self.next_stage()

    # ------------------ Draw ------------------
    def draw(self):
        self.screen.fill((18, 40, 22))
        draw_text(self.screen, "Explore — Stage Learning", self.title_font, (255, 255, 255), (40, 20))

        # plot
        pygame.draw.rect(self.screen, (40, 80, 50), self.map_rect)
        if len(self.polygon) >= 3:
            pygame.draw.polygon(self.screen, (60, 120, 60, 180), self.polygon)
            pygame.draw.polygon(self.screen, (30, 160, 40), self.polygon, 3)

        # sidebar
        pygame.draw.rect(self.screen, (30, 40, 30), self.side_rect)

        # Recommendations
        draw_text(self.screen, "Recommendations", self.title_font, (255, 255, 255),
                  (self.side_rect.x + 12, self.side_rect.y + 10))
        self.crop_rects, self.livestock_rects = [], []
        y = self.side_rect.y + 56
        draw_text(self.screen, "Top crops:", self.text_font, (220, 220, 220),
                  (self.side_rect.x + 12, y))
        for c in self.crops_reco:
            y += 22
            draw_text(self.screen, f"- {c['name']} ({c['water_need']})", self.small_font,
                      (200, 200, 200), (self.side_rect.x + 18, y))
            self.crop_rects.append((c["name"], pygame.Rect(self.side_rect.x + 14, y - 2,
                                                           self.side_rect.w - 28, 20)))

        y += 28
        draw_text(self.screen, "Livestock:", self.text_font, (220, 220, 220),
                  (self.side_rect.x + 12, y))
        for a in self.livestock_reco:
            y += 22
            draw_text(self.screen, f"- {a['name']} (feed: {a['feed_needs']})", self.small_font,
                      (200, 200, 200), (self.side_rect.x + 18, y))
            self.livestock_rects.append((a["name"], pygame.Rect(self.side_rect.x + 14, y - 2,
                                                                self.side_rect.w - 28, 20)))

        # Popup
        if self.selected_reco:
            panel = self.reco_panel_rect
            pygame.draw.rect(self.screen, (25, 35, 25), panel, border_radius=8)
            pygame.draw.rect(self.screen, (80, 120, 80), panel, width=1, border_radius=8)
            kind, name = self.selected_reco
            title = "Crop" if kind == "crop" else "Livestock"
            draw_text(self.screen, f"{title}: {name}", self.text_font,
                      (255, 255, 255), (panel.x + 12, panel.y + 8))
            expl = self.reco_explanations.get(name) if kind == "crop" else self.livestock_explanations.get(name, "")
            yy = panel.y + 40
            for ln in expl.split(". "):
                draw_text(self.screen, ln, self.small_font, (220, 220, 220), (panel.x + 12, yy))
                yy += 16
            # custom input
            input_rect = pygame.Rect(panel.x + 12, panel.bottom - 70, panel.w - 24, 26)
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect, border_radius=4)
            draw_text(self.screen, self.custom_input or "Type your own choice...", self.small_font,
                      (0, 0, 0), (input_rect.x + 6, input_rect.y + 4))
            # buttons
            use_btn = pygame.Rect(panel.right - 140, panel.bottom - 36, 120, 28)
            custom_btn = pygame.Rect(panel.right - 280, panel.bottom - 36, 120, 28)
            pygame.draw.rect(self.screen, (30, 140, 80), use_btn, border_radius=6)
            center_text(self.screen, "Use recommended", self.small_font, (255, 255, 255), use_btn)
            pygame.draw.rect(self.screen, (30, 100, 160), custom_btn, border_radius=6)
            center_text(self.screen, "Confirm custom", self.small_font, (255, 255, 255), custom_btn)

        # Chatbox (bottom)
        chat_title_rect = pygame.Rect(self.side_rect.x + 8, self.side_rect.bottom - 120,
                                      self.side_rect.w - 24, 20)
        pygame.draw.rect(self.screen, (40, 40, 40), chat_title_rect, border_radius=6)
        draw_text(self.screen, "AI Helper", self.small_font, (255, 255, 255),
                  (chat_title_rect.x + 8, chat_title_rect.y + 2))

        self.chat_rect = pygame.Rect(self.side_rect.x + 8, self.side_rect.bottom - 32,
                                     self.side_rect.w - 90, 24)
        pygame.draw.rect(self.screen, (255, 255, 255), self.chat_rect, border_radius=6)
        draw_text(self.screen, self.chat_input or "Type a question...", self.small_font,
                  (0, 0, 0), (self.chat_rect.x + 6, self.chat_rect.y + 4))

        send_btn = pygame.Rect(self.chat_rect.right + 4, self.chat_rect.y, 62, 24)
        pygame.draw.rect(self.screen, (60, 160, 90), send_btn, border_radius=6)
        center_text(self.screen, "Send", self.small_font, (255, 255, 255), send_btn)

        # ---- Selected recommendation panel (Step 1) ----
        if self.selected_reco:
            panel = self.reco_panel_rect
            pygame.draw.rect(self.screen, (20, 30, 20), panel, border_radius=8)
            pygame.draw.rect(self.screen, (60, 60, 60), panel, width=1, border_radius=8)
            kind, name = self.selected_reco
            title = "Crop" if kind == "crop" else "Livestock"
            draw_text(self.screen, f"{title}: {name}", self.text_font, (255, 255, 255), (panel.x + 10, panel.y + 8))
            expl = self.reco_explanations.get(name) if kind == "crop" else self.livestock_explanations.get(name)
            if not expl:
                expl = "No explanation available."
            # wrap text roughly
            lines = []
            words = expl.split(" ")
            line = ""
            for w in words:
                if len(line + " " + w) > 48:
                    lines.append(line)
                    line = w
                else:
                    if line:
                        line += " " + w
                    else:
                        line = w
            if line:
                lines.append(line)
            yy = panel.y + 44
            for ln in lines[:5]:
                draw_text(self.screen, ln, self.small_font, (220, 220, 220), (panel.x + 10, yy))
                yy += 16

            # action buttons
            use_btn = pygame.Rect(panel.right - 140, panel.bottom - 40, 120, 28)
            close_btn = pygame.Rect(panel.right - 270, panel.bottom - 40, 120, 28)
            pygame.draw.rect(self.screen, (30, 140, 80), use_btn, border_radius=6)
            center_text(self.screen, "Use recommended", self.small_font, (255, 255, 255), use_btn)
            pygame.draw.rect(self.screen, (120, 120, 120), close_btn, border_radius=6)
            center_text(self.screen, "Close", self.small_font, (255, 255, 255), close_btn)

        # summary overlay
        if self.show_summary:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            card = pygame.Rect(self.W//2 - 340, self.H//2 - 220, 680, 440)
            pygame.draw.rect(self.screen, (255, 255, 255), card, border_radius=12)
            draw_text(self.screen, "Summary — Explore Mode", self.title_font, (10, 80, 10), (card.x + 24, card.y + 14))
            y2 = card.y + 64
            for idx, st in enumerate(self.stages):
                ch = self.choices.get(st, {"choice": "—"})
                draw_text(self.screen, f"{idx+1}. {st}: {ch['choice']}", self.small_font, (0, 0, 0), (card.x + 34, y2))
                y2 += 26

    # When summary overlay is visible, clicking should return
    def handle_summary_click(self):
        self.set_screen(None)


# ---------- If you want quick local run for testing ----------
if __name__ == "__main__":
    # Quick runner so you can run this file standalone for testing
    pygame.init()
    screen = pygame.display.set_mode((1200, 720))
    clock = pygame.time.Clock()
    current = ExplorePage(screen, lambda s: None)  # placeholder

    # For quick manual testing: pressing ENTER will cycle screens
    screens_cycle = [ExplorePage(screen, lambda s: None), ExploreMap(screen, lambda s: None),
                     ExplorePlot(screen, lambda s: None), ExploreStageLearning(screen, lambda s: None, env=SAMPLE_ENVIRONMENTS["default"], polygon=[(200,200),(400,180),(480,360)])]
    idx = 0
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                idx = (idx + 1) % len(screens_cycle)
                current = screens_cycle[idx]
            current.handle_event(ev)
        current.update()
        current.draw()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
