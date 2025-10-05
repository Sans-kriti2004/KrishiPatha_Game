import requests
from io import BytesIO
from PIL import Image
import pygame
import os
import math
import json
import time

# ---------- Backend API integration ----------
BACKEND_URL = "http://127.0.0.1:8000/analyze/environment"

def fetch_environment_data(lat, lon):
    """
    Send latitude/longitude to backend ML model to get real environment + recommendations.
    """
    try:
        resp = requests.post(BACKEND_URL, json={"latitude": lat, "longitude": lon}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print("Received data from backend:", data)
            return data
        else:
            print("Backend responded with status:", resp.status_code)
            return SAMPLE_ENVIRONMENTS["default"]
    except Exception as e:
        print("Error contacting backend:", e)
        return SAMPLE_ENVIRONMENTS["default"]


# ---- Tiny Web Mercator tile engine for Pygame ----
TILE_SIZE = 256

_session = requests.Session()
_headers = {"User-Agent": "KrishiPathaGame/1.0 (educational demo)"}
_tile_cache = {}  # (z,x,y) -> pygame.Surface

def latlon_to_pixel(lat, lon, z, tile_size=TILE_SIZE):
    lat = max(min(lat, 85.05112878), -85.05112878)  # Web Mercator clamp
    scale = (2 ** z) * tile_size
    x = (lon + 180.0) / 360.0 * scale
    siny = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)) * scale
    return x, y

def pixel_to_latlon(px, py, z, tile_size=TILE_SIZE):
    scale = (2 ** z) * tile_size
    lon = px / scale * 360.0 - 180.0
    n = math.pi - 2.0 * math.pi * (py / scale - 0.5)
    lat = math.degrees(math.atan(math.sinh(n)))
    return lat, lon

def _fetch_tile(z, x, y):
    key = (z, x, y)
    if key in _tile_cache:
        return _tile_cache[key]
   
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    try:
        resp = _session.get(url, headers=_headers, timeout=8)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            surf = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            _tile_cache[key] = surf
            return surf
    except Exception as e:
        print("Tile fetch error:", e)
    return None

def draw_webmap(surface, rect, center_lat, center_lon, zoom):
    """Draws OpenStreetMap tiles covering the given rect centered at (lat, lon)."""
    surface.set_clip(rect)
    surface.fill((180, 210, 230), rect)  # light-blue placeholder background

    cx, cy = latlon_to_pixel(center_lat, center_lon, zoom)
    left = cx - rect.w / 2
    top = cy - rect.h / 2

    start_tx = int(math.floor(left / TILE_SIZE))
    end_tx = int(math.floor((left + rect.w) / TILE_SIZE))
    start_ty = int(math.floor(top / TILE_SIZE))
    end_ty = int(math.floor((top + rect.h) / TILE_SIZE))

    max_tile_index = 2 ** zoom
    for ty in range(start_ty, end_ty + 1):
        for tx in range(start_tx, end_tx + 1):
            # Wrap X (longitude direction)
            x_wrap = tx % max_tile_index
            if ty < 0 or ty >= max_tile_index:
                continue

            tile = _fetch_tile(zoom, x_wrap, ty)
            dest_x = rect.x + int(tx * TILE_SIZE - left)
            dest_y = rect.y + int(ty * TILE_SIZE - top)

            if tile:
                surface.blit(tile, (dest_x, dest_y))
            else:
                pygame.draw.rect(surface, (66, 99, 66),
                                 pygame.Rect(dest_x, dest_y, TILE_SIZE, TILE_SIZE))

    surface.set_clip(None)


pygame.font.init()

# ---------- Simulated datasets & simple recommendation logic ----------
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
    soil = env.get("soil")
    temp = env.get("avg_temp", 25)
    recs = []
    for c in SAMPLE_CROPS:
        score = 0
        if soil in c["soils"]:
            score += 30
        if c["min_temp"] <= temp <= c["max_temp"]:
            score += 30
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

def clamp_point_to_rect(pt, rect, margin=6):
    x = max(rect.left + margin, min(int(pt[0]), rect.right - margin))
    y = max(rect.top + margin, min(int(pt[1]), rect.bottom - margin))
    return (x, y)

def get_map_surface(lat, lon, zoom=13, size=(600, 400)):
    """Fetch a static map from OpenStreetMap tiles and return as Pygame Surface."""

    # OSM tile math
    import math
    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    # Pick the center tile
    xtile, ytile = deg2num(lat, lon, zoom)

    # Build the URL (OpenStreetMap tile server)
    url = f"https://a.tile.openstreetmap.fr/osmfr/{zoom}/{xtile}/{ytile}.png"
    headers = {"User-Agent": "KrishiPathaGame/1.0 (Educational project)"}
    #resp = requests.get(url, headers=headers, timeout=10)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            # Scale tile to requested size
            img = img.resize(size)
            return pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        else:
            print("Failed to load OSM tile:", resp.status_code)
            return None
    except Exception as e:
        print("Error loading OSM tile:", e)
        return None


# ---------- Screens ----------
class ExplorePage:
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

    def update(self): pass

    def draw(self):
        self.screen.fill((28, 58, 45))
        draw_text(self.screen, "Explore Mode — Real-time Farm Planner", self.title_font, (255, 255, 255), (40, 40))
        y = 100
        for b in [
            "Select a location (type or click).",
            "Draw your field plot on the map.",
            "Get crop & livestock recommendations based on environment.",
            "Learn stage-by-stage farming & sustainability tips."
        ]:
            draw_text(self.screen, "• " + b, self.text_font, (220, 220, 220), (60, y))
            y += 36
        pygame.draw.rect(self.screen, (40, 160, 100), self.start_btn, border_radius=10)
        center_text(self.screen, "Start Explore", self.text_font, (255, 255, 255), self.start_btn)

class ExploreMap:
    def __init__(self, screen, set_screen):
        self.screen = screen
        self.set_screen = set_screen
        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.map_rect = pygame.Rect(40, 100, self.W - 80, self.H - 220)
        self.input_active = False
        self.input_rect = pygame.Rect(60, 50, 360, 36)
        self.input_text = ""
        self.hint = "Type a location name (e.g. 'New Delhi') or click on map"
        self.clicked_point = None
        self.next_btn = pygame.Rect(self.W - 200, self.H - 70, 160, 48)
        self.env = SAMPLE_ENVIRONMENTS["default"]
        self.map_surface = None
        self.center_lat, self.center_lon = (28.6139, 77.2090)  # New Delhi
        self.zoom = 12
        self.is_dragging = False
        self.drag_start = None  # (mouse_x, mouse_y)
        self.drag_center_px = None  # (global_px, global_py) snapshot at start



    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # ✅ Handle text input focus separately
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.is_dragging = False
                return
            else:
                self.input_active = False

            # ✅ Handle map dragging only when not typing
            if self.map_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.drag_start = event.pos
                self.drag_center_px = latlon_to_pixel(self.center_lat, self.center_lon, self.zoom)

                mx, my = event.pos
                self.clicked_point = clamp_point_to_rect((mx, my), self.map_rect, margin=6)
                if mx - self.map_rect.x < (self.map_rect.w // 2):
                    self.env = SAMPLE_ENVIRONMENTS.get("up farm")
                else:
                    self.env = SAMPLE_ENVIRONMENTS.get("new delhi")

            # ✅ Handle next button separately
            if self.next_btn.collidepoint(event.pos):
                # Get typed location (optional)
                loc_key = self.input_text.strip().lower()

                # Estimate coordinates if location is known
                if loc_key == "new delhi":
                    self.center_lat, self.center_lon = (28.6139, 77.2090)
                elif loc_key == "up farm":
                    self.center_lat, self.center_lon = (26.8467, 80.9462)
                else:
                    # Use clicked map location if available (approximate)
                    if self.clicked_point:
                        # Convert clicked pixel to lat/lon
                        px = (self.clicked_point[0] - self.map_rect.x - self.map_rect.w / 2)
                        py = (self.clicked_point[1] - self.map_rect.y - self.map_rect.h / 2)
                        center_px, center_py = latlon_to_pixel(self.center_lat, self.center_lon, self.zoom)
                        global_px = center_px + px
                        global_py = center_py + py
                        self.center_lat, self.center_lon = pixel_to_latlon(global_px, global_py, self.zoom)
                    else:
                        # Default fallback
                        self.center_lat, self.center_lon = (25.0, 80.0)

                # 🔹 Fetch live environment data from backend
                env_data = fetch_environment_data(self.center_lat, self.center_lon)
                self.env = env_data if isinstance(env_data, dict) else SAMPLE_ENVIRONMENTS["default"]

                # ✅ Move to ExplorePlot with dynamic environment
                self.set_screen(ExplorePlot(
                    self.screen, self.set_screen,
                    env=self.env,
                    start_point=self.clicked_point,
                    center=(self.center_lat, self.center_lon),
                    zoom=self.zoom
                ))

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # ✅ Proper delta-based map pan
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            start_px, start_py = self.drag_center_px
            new_px = start_px - dx
            new_py = start_py - dy
            self.center_lat, self.center_lon = pixel_to_latlon(new_px, new_py, self.zoom)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.map_rect.collidepoint((mouse_x, mouse_y)):
                old_zoom = self.zoom
                new_zoom = max(2, min(18, old_zoom + (1 if event.y > 0 else -1)))
                if new_zoom != old_zoom:
                    # Current center in pixel coords (old zoom)
                    cx, cy = latlon_to_pixel(self.center_lat, self.center_lon, old_zoom)

                    # Mouse position relative to map rect
                    rel_x = mouse_x - self.map_rect.x
                    rel_y = mouse_y - self.map_rect.y

                    # Global pixel under cursor at old zoom
                    cursor_global_x = cx - (self.map_rect.w / 2) + rel_x
                    cursor_global_y = cy - (self.map_rect.h / 2) + rel_y

                    # Convert that pixel to lat/lon
                    lat_under_cursor, lon_under_cursor = pixel_to_latlon(cursor_global_x, cursor_global_y, old_zoom)

                    # Convert back to pixels at new zoom
                    new_cursor_px, new_cursor_py = latlon_to_pixel(lat_under_cursor, lon_under_cursor, new_zoom)

                    # Adjust map center so that cursor stays fixed visually
                    new_center_x = new_cursor_px - (rel_x - self.map_rect.w / 2)
                    new_center_y = new_cursor_py - (rel_y - self.map_rect.h / 2)

                    self.center_lat, self.center_lon = pixel_to_latlon(new_center_x, new_center_y, new_zoom)
                    self.zoom = new_zoom

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                loc_key = self.input_text.strip().lower()
                self.env = SAMPLE_ENVIRONMENTS.get(loc_key, SAMPLE_ENVIRONMENTS["default"])
                if loc_key == "new delhi":
                    self.center_lat, self.center_lon = (28.6139, 77.2090)
                elif loc_key == "up farm":
                    self.center_lat, self.center_lon = (26.8467, 80.9462)
                else:
                    self.center_lat, self.center_lon = (25.0, 80.0)

                self.set_screen(ExplorePlot(
                    self.screen, self.set_screen,
                    env=self.env,
                    start_point=self.clicked_point,
                    center=(self.center_lat, self.center_lon),
                    zoom=self.zoom
                ))
            else:
                if len(self.input_text) < 50:
                    self.input_text += event.unicode

    def update(self): pass

    def draw(self):
        self.screen.fill((18, 40, 26))
        draw_text(self.screen, "Select Location on Map", self.title_font, (255, 255, 255), (40, 16))
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=6)

        if not _tile_cache:
            pygame.display.set_caption("Loading map tiles...")
        else:
            pygame.display.set_caption("KrishiPatha — Explore Mode")

        txt = self.input_text if self.input_text else self.hint
        color = (0, 0, 0) if self.input_text else (120, 120, 120)
        draw_text(self.screen, txt, self.text_font, color, (self.input_rect.x + 8, self.input_rect.y + 6))

        # blinking cursor if active
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.input_rect.x + 8 + self.text_font.size(self.input_text)[0] + 2
            pygame.draw.line(self.screen, (0, 0, 0),
                            (cursor_x, self.input_rect.y + 6),
                            (cursor_x, self.input_rect.y + self.input_rect.h - 6), 2)
        
        # draw map
        draw_webmap(self.screen, self.map_rect, self.center_lat, self.center_lon, self.zoom)

        if self.clicked_point:
            pygame.draw.circle(self.screen, (255, 220, 60), self.clicked_point, 8)
        
        source = "Live" if "recommended_crops" in self.env else "Sample"
        draw_text(self.screen,
            f"[{source} data] Soil: {self.env['soil']}, Rainfall: {self.env['avg_rainfall']} mm, Temp: {self.env['avg_temp']}°C",
            self.small_font, (210, 210, 210),
            (self.map_rect.left + 8, self.map_rect.bottom + 36))
        pygame.draw.rect(self.screen, (30, 140, 100), self.next_btn, border_radius=8)
        center_text(self.screen, "Plot Field", self.text_font, (255, 255, 255), self.next_btn)

class ExplorePlot:
    def __init__(self, screen, set_screen, env=None, start_point=None, center=None, zoom=12):
        self.screen = screen
        self.set_screen = set_screen
        self.env = env or SAMPLE_ENVIRONMENTS["default"]
        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.map_rect = pygame.Rect(40, 100, self.W - 80, self.H - 220)
        self.points, self.is_finished = [], False
        if start_point: self.points.append(clamp_point_to_rect(start_point, self.map_rect, margin=6))
        self.finish_btn = pygame.Rect(self.W - 220, self.H - 70, 180, 48)
        self.cancel_btn = pygame.Rect(self.W - 420, self.H - 70, 180, 48)
        self.center_lat, self.center_lon = center or (28.6139, 77.2090)
        self.zoom = zoom
        self.is_dragging = False
        self.drag_start = None
        self.drag_center_px = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.finish_btn.collidepoint(event.pos) and len(self.points) >= 3:
                self.is_finished = True
                self.set_screen(ExploreStageLearning(
                    self.screen, self.set_screen,
                    env=self.env,
                    polygon=self.points,
                    center=(self.center_lat, self.center_lon),
                    zoom=self.zoom
                ))
            elif self.cancel_btn.collidepoint(event.pos):
                self.set_screen(ExploreMap(self.screen, self.set_screen))
            elif self.map_rect.collidepoint(event.pos) and not self.is_finished:
                # ✅ Start drag only if not plotting
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.is_dragging = True
                    self.drag_start = event.pos
                    self.drag_center_px = latlon_to_pixel(self.center_lat, self.center_lon, self.zoom)
                else:
                    # Normal click adds a vertex
                    mx = max(self.map_rect.left + 6, min(event.pos[0], self.map_rect.right - 6))
                    my = max(self.map_rect.top + 6, min(event.pos[1], self.map_rect.bottom - 6))
                    self.points.append((mx, my))

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            start_px, start_py = self.drag_center_px
            new_px = start_px - dx
            new_py = start_py - dy
            self.center_lat, self.center_lon = pixel_to_latlon(new_px, new_py, self.zoom)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.map_rect.collidepoint((mouse_x, mouse_y)):
                old_zoom = self.zoom
                new_zoom = max(2, min(18, old_zoom + (1 if event.y > 0 else -1)))
                if new_zoom != old_zoom:
                    # Current center in pixel coords (old zoom)
                    cx, cy = latlon_to_pixel(self.center_lat, self.center_lon, old_zoom)

                    # Mouse position relative to map rect
                    rel_x = mouse_x - self.map_rect.x
                    rel_y = mouse_y - self.map_rect.y

                    # Global pixel under cursor at old zoom
                    cursor_global_x = cx - (self.map_rect.w / 2) + rel_x
                    cursor_global_y = cy - (self.map_rect.h / 2) + rel_y

                    # Convert that pixel to lat/lon
                    lat_under_cursor, lon_under_cursor = pixel_to_latlon(cursor_global_x, cursor_global_y, old_zoom)

                    # Convert back to pixels at new zoom
                    new_cursor_px, new_cursor_py = latlon_to_pixel(lat_under_cursor, lon_under_cursor, new_zoom)

                    # Adjust map center so that cursor stays fixed visually
                    new_center_x = new_cursor_px - (rel_x - self.map_rect.w / 2)
                    new_center_y = new_cursor_py - (rel_y - self.map_rect.h / 2)

                    self.center_lat, self.center_lon = pixel_to_latlon(new_center_x, new_center_y, new_zoom)
                    self.zoom = new_zoom

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.points) >= 3:
                self.set_screen(ExploreStageLearning(
                    self.screen, self.set_screen,
                    env=self.env,
                    polygon=self.points,
                    center=(self.center_lat, self.center_lon),
                    zoom=self.zoom
                ))
            elif event.key == pygame.K_BACKSPACE and self.points:
                self.points.pop()

    def update(self): pass

    def draw(self):
        self.screen.fill((14, 40, 22))
        draw_text(self.screen, 
                "Draw your plot: click to add vertices (Enter to finish, Backspace to undo)",
                self.title_font, (255, 255, 255), (40, 20))

        if not _tile_cache:
            pygame.display.set_caption("Loading map tiles...")
        else:
            pygame.display.set_caption("KrishiPatha — Explore Mode")

        # 🔹 Show map if available
        draw_webmap(self.screen, self.map_rect, self.center_lat, self.center_lon, self.zoom)
        # then draw polygon vertices/lines as you already do

        # 🔹 Draw polygon lines on top
        if len(self.points) >= 2:
            pygame.draw.lines(self.screen, (150, 210, 150), False, self.points, 4)
        for p in self.points:
            pygame.draw.circle(self.screen, (0, 200, 0), p, 6)

        # 🔹 Draw buttons
        pygame.draw.rect(self.screen, (30, 140, 100), self.finish_btn, border_radius=6)
        center_text(self.screen, "Finish Plot", self.small_font, (255, 255, 255), self.finish_btn)

        pygame.draw.rect(self.screen, (160, 60, 60), self.cancel_btn, border_radius=6)
        center_text(self.screen, "Cancel", self.small_font, (255, 255, 255), self.cancel_btn)
        

class ExploreStageLearning:
    def __init__(self, screen, set_screen, env=None, polygon=None, center=None, zoom=12):
        self.screen = screen
        self.set_screen = set_screen
        self.W, self.H = screen.get_size()
        self.env = env or SAMPLE_ENVIRONMENTS["default"]

        self.map_rect = pygame.Rect(40, 100, int(self.W * 0.60), self.H - 160)
        self.side_rect = pygame.Rect(self.map_rect.right + 30, 100, self.W - self.map_rect.right - 70, self.map_rect.h)

        self.polygon = [clamp_point_to_rect(p, self.map_rect, margin=6) for p in (polygon or [])]

        self.title_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)

        # If backend provided real-time recommendations, use them
        if "recommended_crops" in self.env:
            self.crops_reco = [{"name": name, "water_need": "medium"} for name in self.env["recommended_crops"]]
        else:
            self.crops_reco = recommend_crops(self.env)

        if "recommended_livestock" in self.env:
            self.livestock_reco = [{"name": name, "feed_needs": "medium"} for name in self.env["recommended_livestock"]]
        else:
            self.livestock_reco = recommend_livestock(self.env)

        self.reco_explanations = {
            "Wheat": "Wheat grows well in loamy and clay soils, tolerates moderate temperatures and needs medium water.",
            "Millet": "Millet is drought-tolerant, grows in sandy or loamy soils and requires low water.",
            "Rice": "Rice prefers clay soils and high water; gives high yield where water is abundant.",
            "Maize": "Maize likes loamy soils and warm weather; needs timely irrigation."
        }
        self.livestock_explanations = {
            "Goat": "Goats are hardy, low-feed animals suitable for dry areas.",
            "Cow": "Cows require higher feed but give milk and other outputs.",
            "Chicken": "Chickens are low-feed, quick-turn animals giving eggs and meat."
        }

        self.stage_feedback = ""
        self.stage_feedback_until = 0
        self.choices = {}
        self.crop_rects, self.livestock_rects = [], []

        self.crop_input, self.livestock_input = "", ""
        self.crop_input_active, self.livestock_input_active = False, False
        self.crop_input_rect, self.livestock_input_rect = None, None

        self.selected_reco = None
        self._popup_buttons = {}

        self.locked = False  # once confirmed, lock selections
        self.next_btn = pygame.Rect(self.W - 220, self.H - 70, 180, 48)

        self.center_lat, self.center_lon = center or (28.6139, 77.2090)
        self.zoom = zoom
        self.is_dragging = False
        self.drag_start = None
        self.drag_center_px = None

    def draw_wrapped_text(self, surface, text, font, color, rect, line_height=20):
        words = text.split(" ")
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= rect.w - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)

        y = rect.y
        for line in lines:
            line_surf = font.render(line, True, color)
            surface.blit(line_surf, (rect.x + 10, y))
            y += line_height
        return len(lines) * line_height

    def handle_event(self, event):
        if self.locked:
            # ✅ If locked, only allow clicking "Next"
            if event.type == pygame.MOUSEBUTTONDOWN and self.next_btn.collidepoint(event.pos):
                if "crop" in self.choices and "livestock" in self.choices:
                    self.set_screen(ExploreWaterAndProcess(
                    self.screen, self.set_screen,
                    env=self.env,
                    crop=self.choices["crop"],
                    livestock=self.choices["livestock"],
                    polygon=self.polygon,
                    center=(self.center_lat, self.center_lon),
                    zoom=self.zoom
                ))
            return

        # Map interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.map_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.drag_start = event.pos
                self.drag_center_px = latlon_to_pixel(self.center_lat, self.center_lon, self.zoom)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            self.drag_start = None
            self.drag_center_px = None

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            start_px, start_py = self.drag_center_px
            new_px = start_px - dx
            new_py = start_py - dy
            self.center_lat, self.center_lon = pixel_to_latlon(new_px, new_py, self.zoom)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.map_rect.collidepoint((mouse_x, mouse_y)):
                old_zoom = self.zoom
                new_zoom = max(2, min(18, old_zoom + (1 if event.y > 0 else -1)))
                if new_zoom != old_zoom:
                    cx, cy = latlon_to_pixel(self.center_lat, self.center_lon, old_zoom)
                    rel_x = mouse_x - self.map_rect.x
                    rel_y = mouse_y - self.map_rect.y
                    cursor_global_x = cx - (self.map_rect.w / 2) + rel_x
                    cursor_global_y = cy - (self.map_rect.h / 2) + rel_y
                    lat_under_cursor, lon_under_cursor = pixel_to_latlon(cursor_global_x, cursor_global_y, old_zoom)
                    new_cursor_px, new_cursor_py = latlon_to_pixel(lat_under_cursor, lon_under_cursor, new_zoom)
                    new_center_x = new_cursor_px - (rel_x - self.map_rect.w / 2)
                    new_center_y = new_cursor_py - (rel_y - self.map_rect.h / 2)
                    self.center_lat, self.center_lon = pixel_to_latlon(new_center_x, new_center_y, new_zoom)
                    self.zoom = new_zoom

        # Recommendation popup
        if self.selected_reco:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._popup_buttons["choose"].collidepoint(event.pos):
                    kind, name = self.selected_reco
                    self.choices[kind] = {"choice": name, "meta": "recommended"}
                    self.stage_feedback = f"Stored recommended {kind}: {name}"
                    self.stage_feedback_until = time.time() + 2
                    self.selected_reco = None
                elif self._popup_buttons["cancel"].collidepoint(event.pos):
                    self.selected_reco = None
            return

        # Crop/livestock input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.crop_input_rect and self.crop_input_rect.collidepoint(event.pos):
                self.crop_input_active, self.livestock_input_active = True, False
            elif self.livestock_input_rect and self.livestock_input_rect.collidepoint(event.pos):
                self.livestock_input_active, self.crop_input_active = True, False
            else:
                self.crop_input_active = self.livestock_input_active = False

            if hasattr(self, "_confirm_crop_btn") and self._confirm_crop_btn.collidepoint(event.pos):
                if self.crop_input.strip():
                    name = self.crop_input.strip().capitalize()
                    self.choices["crop"] = {"choice": name, "meta": "custom"}
                    self.stage_feedback = f"Crop selected: {name}"
                    self.stage_feedback_until = time.time() + 2
                    self.crop_input = ""

            if hasattr(self, "_confirm_livestock_btn") and self._confirm_livestock_btn.collidepoint(event.pos):
                if self.livestock_input.strip():
                    name = self.livestock_input.strip().capitalize()
                    self.choices["livestock"] = {"choice": name, "meta": "custom"}
                    self.stage_feedback = f"Livestock selected: {name}"
                    self.stage_feedback_until = time.time() + 2
                    self.livestock_input = ""

            mx, my = event.pos
            for name, rect in self.crop_rects:
                if rect.collidepoint((mx, my)):
                    self.selected_reco = ("crop", name)
                    return
            for name, rect in self.livestock_rects:
                if rect.collidepoint((mx, my)):
                    self.selected_reco = ("livestock", name)
                    return

        elif event.type == pygame.KEYDOWN:
            if self.crop_input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.crop_input = self.crop_input[:-1]
                else:
                    self.crop_input += event.unicode
            elif self.livestock_input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.livestock_input = self.livestock_input[:-1]
                else:
                    self.livestock_input += event.unicode

        # Lock both choices
        if "crop" in self.choices and "livestock" in self.choices:
            self.locked = True
            self.stage_feedback = "Choices locked! Proceed to water & irrigation setup."
            self.stage_feedback_until = time.time() + 3

    def update(self, dt=1/60):
        if self.stage_feedback and time.time() > self.stage_feedback_until:
            self.stage_feedback = ""

    def draw(self):
        self.screen.fill((18, 40, 22))
        draw_text(self.screen, "Explore — Stage Learning", self.title_font, (255, 255, 255), (40, 20))

        draw_webmap(self.screen, self.map_rect, self.center_lat, self.center_lon, self.zoom)

        # polygon
        if len(self.polygon) >= 3:
            pygame.draw.polygon(self.screen, (60, 180, 60), self.polygon, 0)
            pygame.draw.polygon(self.screen, (20, 220, 40), self.polygon, 3)
        elif len(self.polygon) >= 2:
            pygame.draw.lines(self.screen, (150, 210, 150), False, self.polygon, 3)
        for p in self.polygon:
            pygame.draw.circle(self.screen, (0, 200, 0), p, 5)

        pygame.draw.rect(self.screen, (30, 40, 30), self.side_rect)
        draw_text(self.screen, "Recommendations", self.title_font, (255, 255, 255),
                (self.side_rect.x + 12, self.side_rect.y + 10))

        # crop section
        self.crop_rects, self.livestock_rects = [], []
        y = self.side_rect.y + 40
        draw_text(self.screen, "Top crops:", self.text_font, (220, 220, 220), (self.side_rect.x + 12, y))
        for c in self.crops_reco:
            y += 28
            rect = pygame.Rect(self.side_rect.x + 14, y, self.side_rect.w - 28, 26)
            self.crop_rects.append((c["name"], rect))
            color = (80, 160, 80) if ("crop" in self.choices and self.choices["crop"]["choice"] == c["name"]) else (40, 80, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            draw_text(self.screen, c["name"], self.small_font, (230, 230, 230), (rect.x + 6, rect.y + 4))

        y += 40
        draw_text(self.screen, "Or type your crop:", self.small_font, (200, 200, 200), (self.side_rect.x + 12, y))
        self.crop_input_rect = pygame.Rect(self.side_rect.x + 14, y + 22, self.side_rect.w - 28, 28)
        pygame.draw.rect(self.screen, (255, 255, 255), self.crop_input_rect, border_radius=4)
        shown = self.crop_input if (self.crop_input or self.crop_input_active) else "Type crop..."
        draw_text(self.screen, shown, self.small_font, (0, 0, 0), (self.crop_input_rect.x + 6, self.crop_input_rect.y + 6))
        confirm_crop_btn = pygame.Rect(self.side_rect.x + 14, self.crop_input_rect.bottom + 8, self.side_rect.w - 28, 28)
        pygame.draw.rect(self.screen, (30, 140, 80), confirm_crop_btn, border_radius=6)
        center_text(self.screen, "Confirm Crop", self.small_font, (255, 255, 255), confirm_crop_btn)
        self._confirm_crop_btn = confirm_crop_btn

        # livestock
        y = confirm_crop_btn.bottom + 40
        draw_text(self.screen, "Livestock:", self.text_font, (220, 220, 220), (self.side_rect.x + 12, y))
        for a in self.livestock_reco:
            y += 28
            rect = pygame.Rect(self.side_rect.x + 14, y, self.side_rect.w - 28, 26)
            self.livestock_rects.append((a["name"], rect))
            color = (80, 160, 80) if ("livestock" in self.choices and self.choices["livestock"]["choice"] == a["name"]) else (40, 80, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            draw_text(self.screen, a["name"], self.small_font, (230, 230, 230), (rect.x + 6, rect.y + 4))

        y += 40
        draw_text(self.screen, "Or type your livestock:", self.small_font, (200, 200, 200), (self.side_rect.x + 12, y))
        self.livestock_input_rect = pygame.Rect(self.side_rect.x + 14, y + 22, self.side_rect.w - 28, 28)
        pygame.draw.rect(self.screen, (255, 255, 255), self.livestock_input_rect, border_radius=4)
        shown2 = self.livestock_input if (self.livestock_input or self.livestock_input_active) else "Type livestock..."
        draw_text(self.screen, shown2, self.small_font, (0, 0, 0), (self.livestock_input_rect.x + 6, self.livestock_input_rect.y + 6))
        confirm_livestock_btn = pygame.Rect(self.side_rect.x + 14, self.livestock_input_rect.bottom + 8, self.side_rect.w - 28, 28)
        pygame.draw.rect(self.screen, (30, 140, 80), confirm_livestock_btn, border_radius=6)
        center_text(self.screen, "Confirm Livestock", self.small_font, (255, 255, 255), confirm_livestock_btn)
        self._confirm_livestock_btn = confirm_livestock_btn

        # ✅ draw next button when both locked
        if self.locked:
            pygame.draw.rect(self.screen, (40, 160, 100), self.next_btn, border_radius=8)
            center_text(self.screen, "Next →", self.text_font, (255, 255, 255), self.next_btn)

        if self.stage_feedback:
            feedback_surf = self.text_font.render(self.stage_feedback, True, (255, 215, 0))
            feedback_x = self.map_rect.x + (self.map_rect.w - feedback_surf.get_width()) // 2
            feedback_y = self.map_rect.bottom + 10
            self.screen.blit(feedback_surf, (feedback_x, feedback_y))


        # ---------------- Popup ----------------
        if self.selected_reco:
            kind, name = self.selected_reco
            explanation = (self.reco_explanations.get(name) if kind == "crop"
                        else self.livestock_explanations.get(name, ""))

            w, base_h = 420, 120
            popup_rect = pygame.Rect(self.W//2 - w//2, self.H//2 - base_h//2, w, base_h)

            # measure wrapped text height
            text_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 50, popup_rect.w - 20, 9999)
            text_height = self.draw_wrapped_text(self.screen, explanation, self.small_font,
                                                (220, 220, 220), text_rect, line_height=20)

            # recalc popup rect with final height
            total_h = min(280, 100 + text_height)
            popup_rect = pygame.Rect(self.W//2 - w//2, self.H//2 - total_h//2, w, total_h)

            # draw background
            pygame.draw.rect(self.screen, (40, 60, 40), popup_rect, border_radius=8)
            pygame.draw.rect(self.screen, (200, 200, 200), popup_rect, 2, border_radius=8)

            # title
            draw_text(self.screen, f"{kind.title()}: {name}", self.text_font, (255, 255, 255),
                    (popup_rect.x + 16, popup_rect.y + 16))

            # draw wrapped explanation again inside popup
            text_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 50, popup_rect.w - 20, popup_rect.h - 90)
            self.draw_wrapped_text(self.screen, explanation, self.small_font, (220, 220, 220), text_rect, line_height=20)

            # buttons
            choose_btn = pygame.Rect(popup_rect.x + 20, popup_rect.bottom - 50, 120, 32)
            cancel_btn = pygame.Rect(popup_rect.right - 140, popup_rect.bottom - 50, 120, 32)
            pygame.draw.rect(self.screen, (40, 160, 100), choose_btn, border_radius=6)
            pygame.draw.rect(self.screen, (160, 60, 60), cancel_btn, border_radius=6)
            center_text(self.screen, "Choose", self.small_font, (255, 255, 255), choose_btn)
            center_text(self.screen, "Cancel", self.small_font, (255, 255, 255), cancel_btn)

            self._popup_buttons = {"choose": choose_btn, "cancel": cancel_btn}

        # ---------------- Feedback ----------------
        if self.stage_feedback:
            feedback_surf = self.text_font.render(self.stage_feedback, True, (255, 215, 0))
            # Position the feedback centered below the map, not on the side panel
            feedback_x = self.map_rect.x + (self.map_rect.w - feedback_surf.get_width()) // 2
            feedback_y = self.map_rect.bottom + 10  # just below the map
            self.screen.blit(feedback_surf, (feedback_x, feedback_y))


# ---------- Next Stage: Water and Irrigation Setup ----------
class ExploreWaterAndProcess:
    def __init__(self, screen, set_screen, env, crop, livestock, polygon=None, center=(28.6139, 77.2090), zoom=12):
        self.screen = screen
        self.set_screen = set_screen
        self.env = env
        self.crop = crop
        self.livestock = livestock
        self.W, self.H = screen.get_size()

        self.center_lat, self.center_lon = center
        self.zoom = zoom
        self.polygon = polygon or []

        self.title_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)

        self.map_rect = pygame.Rect(40, 100, int(self.W * 0.60), self.H - 160)
        self.side_rect = pygame.Rect(self.map_rect.right + 30, 100, self.W - self.map_rect.right - 70, self.map_rect.h)

        self.is_dragging = False
        self.drag_start = None
        self.drag_center_px = None

        self.options = {
            "water_amount": ["Low", "Medium", "High"],
            "irrigation": ["Drip", "Sprinkler", "Manual"]
        }
        self.selected = {"water_amount": None, "irrigation": None}
        self.buttons = []
        self.selected_popup = None
        self._popup_buttons = {}
        self.next_btn = pygame.Rect(self.W - 220, self.H - 70, 180, 48)

        # ✅ Explanation text for popup info
        self.explanations = {
            "Low": "Low water suits drought-tolerant crops like millet or pulses. Conserves resources but may reduce yield.",
            "Medium": "Balanced water level ensures steady growth and sustainable yield under most conditions.",
            "High": "High water helps rice and sugarcane but risks waterlogging and resource overuse.",
            "Drip": "Delivers water directly to roots, saving 50–70% water — ideal for precision farming.",
            "Sprinkler": "Uniform coverage with moderate efficiency, best for large, open fields.",
            "Manual": "Traditional method. Cheap but labor-heavy and less efficient for big farms."
        }

    def draw_wrapped_text(self, surface, text, font, color, rect, line_height=20):
        words = text.split(" ")
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= rect.w - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        y = rect.y
        for line in lines:
            surf = font.render(line, True, color)
            surface.blit(surf, (rect.x + 10, y))
            y += line_height
        return len(lines) * line_height

    def handle_event(self, event):
        # Map dragging and zoom
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.map_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.drag_start = event.pos
                self.drag_center_px = latlon_to_pixel(self.center_lat, self.center_lon, self.zoom)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            self.drag_start = None
            self.drag_center_px = None
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx, dy = event.pos[0] - self.drag_start[0], event.pos[1] - self.drag_start[1]
            sx, sy = self.drag_center_px
            new_px, new_py = sx - dx, sy - dy
            self.center_lat, self.center_lon = pixel_to_latlon(new_px, new_py, self.zoom)
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.map_rect.collidepoint((mx, my)):
                self.zoom = max(2, min(18, self.zoom + (1 if event.y > 0 else -1)))

        # Popup confirmation
        if self.selected_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._popup_buttons["choose"].collidepoint(event.pos):
                    key, val = self.selected_popup
                    self.selected[key] = val
                    self.selected_popup = None
                elif self._popup_buttons["cancel"].collidepoint(event.pos):
                    self.selected_popup = None
            return

        # Click option buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            for (key, val, rect) in self.buttons:
                if rect.collidepoint(event.pos):
                    self.selected_popup = (key, val)
                    return

            # ✅ Move to simulation when both chosen
            if self.next_btn.collidepoint(event.pos):
                if all(self.selected.values()):
                    try:
                        self.set_screen(ExploreSimulation(
                            self.screen, self.set_screen,
                            env=self.env, crop=self.crop,
                            livestock=self.livestock,
                            process=self.selected
                        ))
                    except Exception as e:
                        print("Failed to move to simulation:", e)

    def update(self, dt=1/60): pass

    def draw(self):
        self.screen.fill((18, 40, 22))
        draw_text(self.screen, "Water & Irrigation Setup", self.title_font, (255, 255, 255), (40, 20))

        # 🗺 Draw map + polygon
        draw_webmap(self.screen, self.map_rect, self.center_lat, self.center_lon, self.zoom)
        if len(self.polygon) >= 3:
            pygame.draw.polygon(self.screen, (60, 180, 60), self.polygon, 0)
            pygame.draw.polygon(self.screen, (20, 220, 40), self.polygon, 3)
        elif len(self.polygon) >= 2:
            pygame.draw.lines(self.screen, (150, 210, 150), False, self.polygon, 3)
        for p in self.polygon:
            pygame.draw.circle(self.screen, (0, 200, 0), p, 5)

        # 🌾 Side panel
        pygame.draw.rect(self.screen, (30, 40, 30), self.side_rect)
        draw_text(self.screen, "Select Water & Irrigation", self.text_font, (255, 255, 255),
                  (self.side_rect.x + 12, self.side_rect.y + 10))
        y = self.side_rect.y + 60
        self.buttons.clear()

        for key, values in self.options.items():
            draw_text(self.screen, key.replace("_", " ").title() + ":", self.small_font, (230, 230, 230),
                      (self.side_rect.x + 12, y))
            y += 30
            for val in values:
                rect = pygame.Rect(self.side_rect.x + 14, y, self.side_rect.w - 28, 28)
                color = (80, 160, 80) if self.selected[key] == val else (40, 80, 40)
                pygame.draw.rect(self.screen, color, rect, border_radius=5)
                draw_text(self.screen, val, self.small_font, (255, 255, 255), (rect.x + 8, rect.y + 6))
                self.buttons.append((key, val, rect))
                y += 40
            y += 20

        # 🟩 Next button
        if all(self.selected.values()):
            pygame.draw.rect(self.screen, (40, 160, 100), self.next_btn, border_radius=8)
            center_text(self.screen, "Generate Process →", self.text_font, (255, 255, 255), self.next_btn)
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), self.next_btn, border_radius=8)
            center_text(self.screen, "Select All Options", self.text_font, (180, 180, 180), self.next_btn)

        # 💬 Popup explanation box
        if self.selected_popup:
            key, val = self.selected_popup
            explanation = self.explanations.get(val, "No details available.")
            w, h = 440, 200
            popup_rect = pygame.Rect(self.W // 2 - w // 2, self.H // 2 - h // 2, w, h)
            pygame.draw.rect(self.screen, (40, 60, 40), popup_rect, border_radius=8)
            pygame.draw.rect(self.screen, (200, 200, 200), popup_rect, 2, border_radius=8)
            draw_text(self.screen, f"{key.title()}: {val}", self.text_font, (255, 255, 255),
                      (popup_rect.x + 16, popup_rect.y + 16))
            text_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 50, popup_rect.w - 20, popup_rect.h - 90)
            self.draw_wrapped_text(self.screen, explanation, self.small_font, (220, 220, 220), text_rect)

            choose_btn = pygame.Rect(popup_rect.x + 20, popup_rect.bottom - 50, 120, 32)
            cancel_btn = pygame.Rect(popup_rect.right - 140, popup_rect.bottom - 50, 120, 32)
            pygame.draw.rect(self.screen, (40, 160, 100), choose_btn, border_radius=6)
            pygame.draw.rect(self.screen, (160, 60, 60), cancel_btn, border_radius=6)
            center_text(self.screen, "Choose", self.small_font, (255, 255, 255), choose_btn)
            center_text(self.screen, "Cancel", self.small_font, (255, 255, 255), cancel_btn)
            self._popup_buttons = {"choose": choose_btn, "cancel": cancel_btn}


# ---------- Simulation Screen ----------
class ExploreSimulation:
    def __init__(self, screen, set_screen, env, crop, livestock, process):
        self.screen = screen
        self.set_screen = set_screen
        self.env = env
        self.crop = crop
        self.livestock = livestock
        self.process = process

        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)

        self.start_time = time.time()
        self.sim_duration = 8  # seconds for fake loading
        self.progress = 0.0
        self.done = False

        self.video_placeholder = pygame.Rect(200, 160, self.W - 400, self.H - 320)
    
    def handle_event(self, event):
        # Allow skipping the simulation with Enter or mouse click once complete
        if self.done:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.set_screen(ExploreResults(self.screen, self.set_screen, {"yield": 3000, "score": 80}, self.crop, self.livestock, self.process))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.set_screen(ExploreResults(self.screen, self.set_screen, {"yield": 3000, "score": 80}, self.crop, self.livestock, self.process))


    def update(self):
        elapsed = time.time() - self.start_time
        self.progress = min(1.0, elapsed / self.sim_duration)
        if self.progress >= 1.0 and not self.done:
            self.done = True
            time.sleep(0.5)
            # send to backend for results
            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/analyze/simulate",
                    json={
                        "crop": self.crop["choice"],
                        "livestock": self.livestock["choice"],
                        "water_amount": self.process["water_amount"],
                        "irrigation": self.process["irrigation"],
                        "soil": self.env.get("soil", "loamy"),
                        "temp": self.env.get("avg_temp", 25),
                        "rainfall": self.env.get("avg_rainfall", 700)
                    },
                    timeout=10
                )
                data = resp.json() if resp.status_code == 200 else {"yield": 0, "score": 0}
            except Exception as e:
                print("Simulation backend error:", e)
                data = {"yield": 0, "score": 0}

            self.set_screen(ExploreResults(self.screen, self.set_screen, data, self.crop, self.livestock, self.process))

    def draw(self):
        self.screen.fill((15, 35, 25))
        draw_text(self.screen, "Simulating Farming Process...", self.title_font, (255, 255, 255), (40, 30))

        pygame.draw.rect(self.screen, (50, 80, 50), self.video_placeholder, border_radius=12)
        center_text(self.screen, "Crop Growth Simulation Running...", self.text_font, (240, 240, 240), self.video_placeholder)

        # progress bar
        bar_rect = pygame.Rect(200, self.video_placeholder.bottom + 40, self.W - 400, 30)
        pygame.draw.rect(self.screen, (80, 120, 80), bar_rect, border_radius=6)
        inner_width = int(bar_rect.w * self.progress)
        pygame.draw.rect(self.screen, (60, 200, 90), (bar_rect.x, bar_rect.y, inner_width, bar_rect.h), border_radius=6)
        percent_text = f"{int(self.progress * 100)}%"
        center_text(self.screen, percent_text, self.text_font, (255, 255, 255), bar_rect)


# ---------- Results Screen ----------
class ExploreResults:
    def __init__(self, screen, set_screen, data, crop, livestock, process):
        self.screen = screen
        self.set_screen = set_screen
        self.data = data
        self.crop = crop
        self.livestock = livestock
        self.process = process

        self.W, self.H = screen.get_size()
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 16)

        # ✅ single home button
        self.home_btn = pygame.Rect(self.W // 2 - 100, self.H - 80, 200, 50)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.home_btn.collidepoint(event.pos):
                # ✅ Return to the very first game page
                from screens.landing import LandingPage
                self.set_screen(LandingPage(self.screen, self.set_screen))

    def update(self, dt=1/60):
        pass

    def draw(self):
        self.screen.fill((18, 45, 28))
        draw_text(self.screen, "Farming Results & Sustainability Report", self.title_font, (255, 255, 255), (40, 30))

        y = 120
        draw_text(self.screen, f"Crop: {self.crop['choice']}", self.text_font, (240, 240, 240), (100, y)); y += 40
        draw_text(self.screen, f"Livestock: {self.livestock['choice']}", self.text_font, (240, 240, 240), (100, y)); y += 40
        draw_text(self.screen, f"Water Level: {self.process['water_amount']}", self.text_font, (240, 240, 240), (100, y)); y += 40
        draw_text(self.screen, f"Irrigation Type: {self.process['irrigation']}", self.text_font, (240, 240, 240), (100, y)); y += 60

        # Yield and score
        yield_val = self.data.get("yield", 0)
        score_val = self.data.get("score", 0)
        draw_text(self.screen, f"Predicted Yield: {yield_val} kg/acre", self.text_font, (255, 255, 0), (100, y)); y += 40
        draw_text(self.screen, f"Sustainability Score: {score_val}%", self.text_font, (80, 255, 120), (100, y)); y += 40

        draw_text(
            self.screen,
            "Tips: Rotate crops and balance livestock feed to improve efficiency.",
            self.small_font, (220, 220, 220), (100, y + 30)
        )

        # ✅ draw the Home button
        pygame.draw.rect(self.screen, (40, 140, 100), self.home_btn, border_radius=8)
        center_text(self.screen, "Go to Home Page", self.text_font, (255, 255, 255), self.home_btn)


# ---------- If you want quick local run for testing ----------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1200, 720))
    clock = pygame.time.Clock()

    current_screen = None

    def set_screen(new_screen):
        global current_screen   # ✅ use global instead of nonlocal
        current_screen = new_screen

    # Start from the ExplorePage
    set_screen(ExplorePage(screen, set_screen))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_screen:
                current_screen.handle_event(event)

        if current_screen:
            current_screen.update()
            current_screen.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
