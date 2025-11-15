"""
UI Widgets Module - Reusable UI components for the interface
"""
import pygame
from typing import Tuple, Optional


class Slider:
    """Horizontal slider widget for value adjustment"""
    
    def __init__(self, x: int, y: int, width: int, height: int, min_val: float = 0.0, 
                 max_val: float = 100.0, initial_val: float = 50.0, label: str = "", theme=None):
        """
        Initialize slider
        
        Args:
            x: X position
            y: Y position
            width: Slider width
            height: Slider height
            min_val: Minimum value
            max_val: Maximum value
            initial_val: Initial value
            label: Optional label text
            theme: Optional theme for styling
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.label = label
        self.theme = theme
        
        # Track properties
        self.track_rect = pygame.Rect(x, y + height // 2 - 2, width, 4)
        
        # Knob properties
        self.knob_radius = max(height // 2, 8)
        self.knob_rect = pygame.Rect(0, 0, self.knob_radius * 2, self.knob_radius * 2)
        
        # Value
        self.value = self._clamp(initial_val)
        self.update_knob_position()
        
        # State
        self.is_dragging = False
        self.is_hovered = False
    
    def _clamp(self, val: float) -> float:
        """Clamp value between min and max"""
        return max(self.min_val, min(self.max_val, val))
    
    def _value_to_x(self, value: float) -> float:
        """Convert value to x position"""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.x + ratio * self.width
    
    def _x_to_value(self, x: float) -> float:
        """Convert x position to value"""
        ratio = (x - self.x) / self.width
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def update_knob_position(self) -> None:
        """Update knob position based on current value"""
        knob_x = self._value_to_x(self.value)
        self.knob_rect.center = (knob_x, self.y + self.height // 2)
    
    def update(self, pos: Tuple[int, int], mouse_pressed: bool) -> None:
        """
        Update slider state
        
        Args:
            pos: Mouse position
            mouse_pressed: Whether mouse button is pressed
        """
        self.is_hovered = self.knob_rect.collidepoint(pos)
        
        if mouse_pressed and self.is_hovered:
            self.is_dragging = True
        elif not mouse_pressed:
            self.is_dragging = False
        
        if self.is_dragging:
            self.value = self._clamp(self._x_to_value(pos[0]))
            self.update_knob_position()
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font = None, 
             track_color: Tuple[int, int, int] = (100, 100, 100),
             knob_color: Tuple[int, int, int] = (200, 200, 200),
             fill_color: Tuple[int, int, int] = (100, 200, 100)) -> None:
        """
        Draw the slider
        
        Args:
            surface: Pygame surface to draw on
            font: Optional font for label
            track_color: Color of the track
            knob_color: Color of the knob
            fill_color: Color of the filled portion
        """
        # Use theme colors if available
        if self.theme:
            track_color = self.theme.get_color('slider_track', track_color)
            knob_color = self.theme.get_color('slider_knob', knob_color)
            fill_color = self.theme.get_color('accent', fill_color)
        
        # Draw fill (value portion)
        fill_width = self.knob_rect.centerx - self.track_rect.x
        fill_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, fill_width, self.track_rect.height)
        pygame.draw.rect(surface, fill_color, fill_rect)
        
        # Draw track
        pygame.draw.rect(surface, track_color, self.track_rect)
        pygame.draw.rect(surface, (255, 255, 255), self.track_rect, 1)
        
        # Draw knob
        knob_color_actual = (150, 255, 150) if self.is_hovered else knob_color
        pygame.draw.circle(surface, knob_color_actual, self.knob_rect.center, self.knob_radius)
        pygame.draw.circle(surface, (255, 255, 255), self.knob_rect.center, self.knob_radius, 2)
        
        # Draw label and value
        if font and self.label:
            label_text = font.render(f"{self.label}: {self.value:.1f}", True, (255, 255, 255))
            surface.blit(label_text, (self.x, self.y - 25))
    
    def get_value(self) -> float:
        """Get current slider value"""
        return self.value
    
    def set_value(self, value: float) -> None:
        """Set slider value"""
        self.value = self._clamp(value)
        self.update_knob_position()


class VerticalSlider(Slider):
    """Vertical slider widget for value adjustment"""
    
    def __init__(self, x: int, y: int, width: int, height: int, min_val: float = 0.0,
                 max_val: float = 100.0, initial_val: float = 50.0, label: str = "", theme=None):
        """Initialize vertical slider"""
        super().__init__(x, y, width, height, min_val, max_val, initial_val, label, theme)
        
        # Override track for vertical orientation
        self.track_rect = pygame.Rect(x + width // 2 - 2, y, 4, height)
    
    def _value_to_y(self, value: float) -> float:
        """Convert value to y position (inverted for typical up=max convention)"""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.y + self.height - ratio * self.height
    
    def _y_to_value(self, y: float) -> float:
        """Convert y position to value"""
        ratio = (self.y + self.height - y) / self.height
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)
    
    def update_knob_position(self) -> None:
        """Update knob position based on current value"""
        knob_y = self._value_to_y(self.value)
        self.knob_rect.center = (self.x + self.width // 2, knob_y)
    
    def update(self, pos: Tuple[int, int], mouse_pressed: bool) -> None:
        """Update vertical slider state"""
        self.is_hovered = self.knob_rect.collidepoint(pos)
        
        if mouse_pressed and self.is_hovered:
            self.is_dragging = True
        elif not mouse_pressed:
            self.is_dragging = False
        
        if self.is_dragging:
            self.value = self._clamp(self._y_to_value(pos[1]))
            self.update_knob_position()
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font = None,
             track_color: Tuple[int, int, int] = (100, 100, 100),
             knob_color: Tuple[int, int, int] = (200, 200, 200),
             fill_color: Tuple[int, int, int] = (100, 200, 100)) -> None:
        """Draw the vertical slider"""
        # Use theme colors if available
        if self.theme:
            track_color = self.theme.get_color('slider_track', track_color)
            knob_color = self.theme.get_color('slider_knob', knob_color)
            fill_color = self.theme.get_color('accent', fill_color)
        
        # Draw fill (value portion)
        fill_height = self.y + self.height - self.knob_rect.centery
        fill_rect = pygame.Rect(self.track_rect.x, self.knob_rect.centery, 
                               self.track_rect.width, fill_height)
        pygame.draw.rect(surface, fill_color, fill_rect)
        
        # Draw track
        pygame.draw.rect(surface, track_color, self.track_rect)
        pygame.draw.rect(surface, (255, 255, 255), self.track_rect, 1)
        
        # Draw knob
        knob_color_actual = (150, 255, 150) if self.is_hovered else knob_color
        pygame.draw.circle(surface, knob_color_actual, self.knob_rect.center, self.knob_radius)
        pygame.draw.circle(surface, (255, 255, 255), self.knob_rect.center, self.knob_radius, 2)
        
        # Draw label and value
        if font and self.label:
            label_text = font.render(f"{self.label}: {self.value:.1f}", True, (255, 255, 255))
            surface.blit(label_text, (self.x - 100, self.y - 15))
