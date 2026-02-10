import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Tears Blue-themed Colors (RGB values)
TEARS_LIGHT = (173, 216, 230)  # Light blue
TEARS_MEDIUM = (70, 130, 180)  # Steel blue
TEARS_DARK = (25, 25, 112)     # Midnight blue
TEARS_PALE = (230, 242, 255)   # Very pale blue
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 0, 128)
SKY_BLUE = (135, 206, 235)
POWDER_BLUE = (176, 224, 230)
OCEAN_BLUE = (0, 119, 190)
DEEP_BLUE = (0, 0, 139)

# Dangerous tear colors
DANGER_RED = (220, 20, 60)     # Crimson red
DANGER_DARK_RED = (139, 0, 0)  # Dark red
DANGER_LIGHT_RED = (255, 69, 0) # Red orange

WELCOME_SCREEN = 0
PLAYING = 1
GAME_OVER = 2

# Bucket settings 
BUCKET_WIDTH = 120
BUCKET_HEIGHT = 35
BUCKET_SPEED = 8

# Falling object settings 
OBJECT_SIZE = 35
OBJECT_SPEED = 5
OBJECT_SPAWN_RATE = 60
DANGER_SPAWN_CHANCE = 15 

# Game settings
MAX_LIVES = 5

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.life -= 1
        self.velocity_y += 0.1 

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color_with_alpha = (*self.color[:3], alpha)
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

    def is_alive(self):
        return self.life > 0

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        self.hovered = False
        self.pulse_time = 0

    def draw(self, screen):
        self.pulse_time += 0.1
        pulse_offset = math.sin(self.pulse_time) * 3 if self.hovered else 0
        
        shadow_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        button_rect = pygame.Rect(self.rect.x, self.rect.y - pulse_offset, self.rect.width, self.rect.height)
        current_color = TEARS_MEDIUM if self.hovered else self.color
        pygame.draw.rect(screen, current_color, button_rect, border_radius=10)
        
        gradient_surface = pygame.Surface((self.rect.width, self.rect.height // 2), pygame.SRCALPHA)
        for i in range(self.rect.height // 2):
            alpha = int(50 * (1 - i / (self.rect.height // 2)))
            pygame.draw.line(gradient_surface, (*WHITE[:3], alpha), (0, i), (self.rect.width, i))
        screen.blit(gradient_surface, (button_rect.x, button_rect.y))
        
        pygame.draw.rect(screen, TEARS_DARK, button_rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class Bucket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BUCKET_WIDTH
        self.height = BUCKET_HEIGHT
        self.speed = BUCKET_SPEED

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        shadow_points = [
            (self.x + 12, self.y + 2),
            (self.x + self.width - 8, self.y + 2),
            (self.x + self.width + 2, self.y + self.height + 2),
            (self.x + 2, self.y + self.height + 2)
        ]
        pygame.draw.polygon(screen, (0, 0, 0, 80), shadow_points)
        
        bucket_points = [
            (self.x + 10, self.y),
            (self.x + self.width - 10, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ]
        pygame.draw.polygon(screen, TEARS_DARK, bucket_points)
        
        interior_points = [
            (self.x + 12, self.y + 3),
            (self.x + self.width - 12, self.y + 3),
            (self.x + self.width - 3, self.y + self.height - 3),
            (self.x + 3, self.y + self.height - 3)
        ]
        pygame.draw.polygon(screen, TEARS_MEDIUM, interior_points)
        
        shine_points = [
            (self.x + 15, self.y + 5),
            (self.x + self.width - 15, self.y + 5),
            (self.x + self.width - 20, self.y + 15),
            (self.x + 20, self.y + 15)
        ]
        pygame.draw.polygon(screen, TEARS_LIGHT, shine_points)
        
        self._draw_handle(screen, self.x - 8, self.y + 8)
        self._draw_handle(screen, self.x + self.width - 5, self.y + 8)
        
        pygame.draw.line(screen, WHITE, (self.x + 10, self.y), (self.x + self.width - 10, self.y), 4)
        pygame.draw.line(screen, TEARS_LIGHT, (self.x + 12, self.y + 1), (self.x + self.width - 12, self.y + 1), 2)

    def _draw_handle(self, screen, x, y):

        handle_rect = pygame.Rect(x, y, 13, 8)
        pygame.draw.rect(screen, TEARS_DARK, handle_rect, border_radius=3)
        pygame.draw.rect(screen, TEARS_MEDIUM, (x + 1, y + 1, 11, 6), border_radius=2)
        pygame.draw.line(screen, TEARS_LIGHT, (x + 2, y + 2), (x + 10, y + 2), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class FallingObject:
    def __init__(self, x, y, is_dangerous=False):
        self.x = x
        self.y = y
        self.size = OBJECT_SIZE
        self.speed = OBJECT_SPEED
        self.is_dangerous = is_dangerous
        self.rotation = 0
        self.pulse_time = 0
        
        if is_dangerous:
            self.color = DANGER_RED
            self.secondary_color = DANGER_DARK_RED
            self.highlight_color = DANGER_LIGHT_RED
            self.speed *= 1.2  
        else:
            self.color = random.choice([TEARS_MEDIUM, SKY_BLUE, POWDER_BLUE, OCEAN_BLUE])
            self.secondary_color = TEARS_DARK
            self.highlight_color = WHITE

    def update(self):
        self.y += self.speed
        self.rotation += 2
        self.pulse_time += 0.2

    def draw(self, screen):
        pulse_offset = 0
        if self.is_dangerous:
            pulse_offset = math.sin(self.pulse_time) * 3
        
        current_size = self.size + pulse_offset
        
        if self.is_dangerous:
            for i in range(3):
                glow_size = current_size + (i * 8)
                glow_alpha = 50 - (i * 15)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*DANGER_RED[:3], glow_alpha), 
                                 (glow_size // 2, glow_size // 2), glow_size // 2)
                screen.blit(glow_surface, (int(self.x - glow_size // 2), int(self.y - glow_size // 2)))
        
        teardrop_rect = pygame.Rect(int(self.x - current_size // 4), int(self.y), 
                                  current_size // 2, current_size // 2)
        pygame.draw.ellipse(screen, self.color, teardrop_rect)
        
        gradient_rect = pygame.Rect(int(self.x - current_size // 6), int(self.y + 2), 
                                  current_size // 3, current_size // 3)
        pygame.draw.ellipse(screen, self.secondary_color, gradient_rect)
        
        point_size = int(current_size // 3)
        points = [
            (int(self.x), int(self.y - point_size // 2)),
            (int(self.x - point_size // 4), int(self.y + point_size // 4)),
            (int(self.x + point_size // 4), int(self.y + point_size // 4))
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Smooth connection
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + point_size // 4)), point_size // 4)
        
        highlight_size = max(3, int(current_size // 8))
        pygame.draw.ellipse(screen, self.highlight_color, 
                          (int(self.x - highlight_size), int(self.y + 2), 
                           highlight_size * 2, highlight_size * 3))
        pygame.draw.circle(screen, self.highlight_color, 
                         (int(self.x - 2), int(self.y + 3)), max(1, highlight_size // 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT + self.size

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tears PyGame- Catch the Falling Tears!")
        self.clock = pygame.time.Clock()
        self.state = WELCOME_SCREEN

        self.title_font = pygame.font.Font(None, 84)
        self.subtitle_font = pygame.font.Font(None, 42)
        self.score_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 28)

        self.bucket = Bucket(WINDOW_WIDTH // 2 - BUCKET_WIDTH // 2, WINDOW_HEIGHT - 60)
        self.falling_objects = []
        self.particles = []

        self.score = 0
        self.lives = MAX_LIVES
        self.spawn_timer = 0
        self.animation_time = 0

        self.start_button = Button(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 120, 240, 70, "START GAME", TEARS_LIGHT, WHITE)
        self.restart_button = Button(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 50, 240, 70, "PLAY AGAIN", TEARS_LIGHT, WHITE)
        self.quit_button = Button(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 140, 240, 70, "QUIT", TEARS_DARK, WHITE)

        self.music_started = False
        
        # Sound effects
        self.tear_sound = None
        self.load_sounds()

    def load_sounds(self):
        """Load sound effects"""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            tear_sound_path = os.path.join(base_path, "tear-drop-sound.mp3")
            self.tear_sound = pygame.mixer.Sound(tear_sound_path)
            self.tear_sound.set_volume(0.9) 
            print("Tear sound effect loaded successfully.")
        except Exception as e:
            print(f"Error loading tear sound effect: {e}")
            self.tear_sound = None

    def play_tear_sound(self):
        """Play the tear catch sound effect"""
        if self.tear_sound:
            try:
                self.tear_sound.play()
            except Exception as e:
                print(f"Error playing tear sound: {e}")

    def create_particles(self, x, y, color, count=8):
        for _ in range(count):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-5, -1)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y))

    def load_music(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            music_path = os.path.join(base_path, "bgmusic.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            print("Background music loaded and playing.")
        except Exception as e:
            print(f"Error loading music: {e}")

    def draw_animated_background(self):
        self.animation_time += 0.02

        pixel_size = 8  

        DARK_BLUE = (0, 51, 102)     
        MID_BLUE = (30, 144, 255)  
        PALE_BLUE = (173, 216, 230)   

        for y in range(0, WINDOW_HEIGHT, pixel_size):
            for x in range(0, WINDOW_WIDTH, pixel_size):
                wave_offset = math.sin(self.animation_time + y * 0.06 + x * 0.02) * 16
                color_ratio = (y + wave_offset) / WINDOW_HEIGHT
                color_ratio = max(0, min(1, color_ratio))

                # Color blending
                if color_ratio < 0.5:
                    ratio = color_ratio / 0.5
                    r = int(DARK_BLUE[0] * (1 - ratio) + MID_BLUE[0] * ratio)
                    g = int(DARK_BLUE[1] * (1 - ratio) + MID_BLUE[1] * ratio)
                    b = int(DARK_BLUE[2] * (1 - ratio) + MID_BLUE[2] * ratio)
                else:
                    ratio = (color_ratio - 0.5) / 0.5
                    r = int(MID_BLUE[0] * (1 - ratio) + PALE_BLUE[0] * ratio)
                    g = int(MID_BLUE[1] * (1 - ratio) + PALE_BLUE[1] * ratio)
                    b = int(MID_BLUE[2] * (1 - ratio) + PALE_BLUE[2] * ratio)

                pygame.draw.rect(self.screen, (r, g, b), (x, y, pixel_size, pixel_size))


    def draw_floating_tears(self):

        for i in range(8):
            x = 60 + i * 100 + math.sin(self.animation_time * 0.5 + i) * 20
            y = 200 + math.cos(self.animation_time * 0.3 + i * 0.7) * 60
            
            alpha = 30 + math.sin(self.animation_time + i) * 20
            small_surface = pygame.Surface((20, 25), pygame.SRCALPHA)
            
            pygame.draw.ellipse(small_surface, (*TEARS_MEDIUM[:3], int(alpha)), (3, 7, 14, 16))
            points = [(10, 3), (6, 10), (14, 10)]
            pygame.draw.polygon(small_surface, (*TEARS_MEDIUM[:3], int(alpha)), points)
            
            self.screen.blit(small_surface, (int(x - 10), int(y - 12)))

        for i in range(15):
            x = (i * 70 + int(math.sin(self.animation_time + i) * 20)) % WINDOW_WIDTH
            y = (i * 40 + int(math.cos(self.animation_time * 1.2 + i) * 15)) % WINDOW_HEIGHT
            alpha = 40 + int(20 * math.sin(self.animation_time + i))
            glow_color = (255, 255, 255, alpha)
            
            glow_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (3, 3), 3)
            self.screen.blit(glow_surface, (x, y))


    def draw_welcome_screen(self):
        self.draw_animated_background()
        self.draw_floating_tears()
        
        title_text = "TEARS PYGAME"
        for offset in range(5, 0, -1):
            alpha = 255 - (offset * 40)
            title_surface = self.title_font.render(title_text, True, (*TEARS_DARK[:3], alpha))
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2 + offset, 120 + offset))  

            glow_surface = pygame.Surface(title_surface.get_size(), pygame.SRCALPHA)
            glow_surface.blit(title_surface, (0, 0))
            self.screen.blit(glow_surface, title_rect)
        
        # Main title
        title_surface = self.title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_surface, title_rect)
        
        pulse = math.sin(self.animation_time * 2) * 0.1 + 1
        subtitle_font = pygame.font.Font(None, int(42 * pulse))
        subtitle_text = subtitle_font.render("Catch the Falling Tears", True, TEARS_LIGHT)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Game instructions
        instructions = [
            "• Use Arrow Keys or A/D to move the bucket",
            "• Catch blue tears to score points (+10)",
            "• AVOID red tears - they cost you a life! (-1)",
            "•  You have 5 lives - don't let tears fall!",
            "• Press SPACE or click START to begin"
        ]
        
        for i, instruction in enumerate(instructions):
            color = WHITE if i % 2 == 0 else TEARS_LIGHT
            text = self.text_font.render(instruction, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 240 + i * 35))
            
            shadow_text = self.text_font.render(instruction, True, TEARS_DARK)
            shadow_rect = text_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(text, text_rect)

        self.start_button.draw(self.screen)

    def draw_game_screen(self):
        ALMOST_WHITE = (250, 252, 255)  
        SOFT_BLUE = (200, 225, 245)     

        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(ALMOST_WHITE[0] * (1 - ratio) + SOFT_BLUE[0] * ratio)
            g = int(ALMOST_WHITE[1] * (1 - ratio) + SOFT_BLUE[1] * ratio)
            b = int(ALMOST_WHITE[2] * (1 - ratio) + SOFT_BLUE[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        for i in range(0, WINDOW_WIDTH, 50):
            alpha = 15
            pygame.draw.line(self.screen, (*TEARS_LIGHT[:3], alpha), (i, 0), (i, WINDOW_HEIGHT))

        for particle in self.particles[:]:
            particle.update()
            if particle.is_alive():
                particle.draw(self.screen)
            else:
                self.particles.remove(particle)

        self.bucket.draw(self.screen)
        for obj in self.falling_objects:
            obj.draw(self.screen)

        self.draw_ui()

    def draw_ui(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, TEARS_DARK)
        score_shadow = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_shadow, (22, 22))
        self.screen.blit(score_text, (20, 20))
        
        for i in range(MAX_LIVES):
            tear_x = WINDOW_WIDTH - 60 - (i * 35)
            tear_y = 45
            
            if i < self.lives:
                # Active life - bright teardrop
                color = TEARS_MEDIUM
                highlight = WHITE
            else:
                # Lost life - faded teardrop
                color = (100, 100, 100)
                highlight = (150, 150, 150)
            
            pygame.draw.circle(self.screen, (0, 0, 0, 50), (tear_x + 1, tear_y + 4), 10)
            pygame.draw.circle(self.screen, color, (tear_x, tear_y + 3), 10)
            
            mini_points = [
                (tear_x, tear_y - 7),
                (tear_x - 5, tear_y + 3),
                (tear_x + 5, tear_y + 3)
            ]
            pygame.draw.polygon(self.screen, color, mini_points)
            
            pygame.draw.circle(self.screen, highlight, (tear_x - 3, tear_y + 1), 3)
            pygame.draw.circle(self.screen, highlight, (tear_x - 2, tear_y), 1)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for y in range(WINDOW_HEIGHT):
            alpha = int(180 * (y / WINDOW_HEIGHT))
            pygame.draw.line(overlay, (*TEARS_DARK[:3], alpha), (0, y), (WINDOW_WIDTH, y))
        self.screen.blit(overlay, (0, 0))

        game_over_text = "GAME OVER"
        for offset in range(3, 0, -1):
            glow_surface = self.title_font.render(game_over_text, True, DANGER_RED)
            glow_rect = glow_surface.get_rect(center=(WINDOW_WIDTH // 2 + offset, 200))
            self.screen.blit(glow_surface, glow_rect)
        
        main_text = self.title_font.render(game_over_text, True, DANGER_DARK_RED)
        main_rect = main_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(main_text, main_rect)

        pulse = math.sin(self.animation_time * 3) * 0.1 + 1
        score_font = pygame.font.Font(None, int(36 * pulse))
        final_score_text = score_font.render(f"Final Score: {self.score}", True, DEEP_BLUE)
        final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, 260))
        self.screen.blit(final_score_text, final_score_rect)

        self.restart_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def reset_game(self):
        self.score = 0
        self.lives = MAX_LIVES
        self.falling_objects = []
        self.particles = []
        self.spawn_timer = 0
        self.bucket.x = WINDOW_WIDTH // 2 - BUCKET_WIDTH // 2

    def update_game(self):
        self.animation_time += 0.02
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.bucket.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.bucket.move_right()

        self.spawn_timer += 1
        if self.spawn_timer >= OBJECT_SPAWN_RATE:
            self.spawn_timer = 0
            x = random.randint(OBJECT_SIZE // 2, WINDOW_WIDTH - OBJECT_SIZE // 2)
            
            # Determine if this should be a dangerous tear
            is_dangerous = random.randint(1, 100) <= DANGER_SPAWN_CHANCE
            self.falling_objects.append(FallingObject(x, -OBJECT_SIZE, is_dangerous))

        for obj in self.falling_objects[:]:
            obj.update()
            if self.bucket.get_rect().colliderect(obj.get_rect()):
                self.falling_objects.remove(obj)
                
                # Play sound effect when tear is caught
                self.play_tear_sound()
                
                if obj.is_dangerous:
                    # Red tear caught - lose a life and create red particles
                    self.lives -= 1
                    self.create_particles(obj.x, obj.y, DANGER_RED, 12)
                    
                    if self.lives <= 0:
                        self.state = GAME_OVER
                        pygame.mixer.music.stop()
                else:
                    # Blue tear caught - gain points and create blue particles
                    self.score += 10
                    self.create_particles(obj.x, obj.y, TEARS_MEDIUM, 8)
                    
            elif obj.is_off_screen():
                self.falling_objects.remove(obj)
                if not obj.is_dangerous:  # Only lose life for missing blue tears
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GAME_OVER
                        pygame.mixer.music.stop()

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == WELCOME_SCREEN:
                        if self.start_button.is_clicked(mouse_pos):
                            self.state = PLAYING
                            self.reset_game()
                            if not self.music_started:
                                self.load_music()
                                self.music_started = True
                    elif self.state == GAME_OVER:
                        if self.restart_button.is_clicked(mouse_pos):
                            self.state = PLAYING
                            self.reset_game()
                            # Restart music when playing again
                            if self.music_started:
                                self.load_music()
                        elif self.quit_button.is_clicked(mouse_pos):
                            running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == WELCOME_SCREEN:
                        self.state = PLAYING
                        self.reset_game()
                        if not self.music_started:
                            self.load_music()
                            self.music_started = True
                    elif event.key == pygame.K_r and self.state == GAME_OVER:
                        self.state = PLAYING
                        self.reset_game()
                        # Restart music when playing again with R key
                        if self.music_started:
                            self.load_music()

            if self.state == WELCOME_SCREEN:
                self.start_button.update_hover(mouse_pos)
            elif self.state == GAME_OVER:
                self.restart_button.update_hover(mouse_pos)
                self.quit_button.update_hover(mouse_pos)

            if self.state == PLAYING:
                self.update_game()

            if self.state == WELCOME_SCREEN:
                self.draw_welcome_screen()
            elif self.state == PLAYING:
                self.draw_game_screen()
            elif self.state == GAME_OVER:
                self.draw_game_screen()
                self.draw_game_over_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()