"""
Audio Effects Module - Handles equalizer and audio effects
"""
from typing import List, Dict
import pygame


class Equalizer:
    """5-Band Equalizer for audio manipulation"""
    
    # Frequency bands: (name, frequency_hz, default_db)
    BANDS = [
        ("60 Hz (Bass)", 60, 0.0),
        ("250 Hz (Low Mid)", 250, 0.0),
        ("1 kHz (Mid)", 1000, 0.0),
        ("4 kHz (High Mid)", 4000, 0.0),
        ("16 kHz (Treble)", 16000, 0.0),
    ]
    
    def __init__(self):
        """Initialize equalizer with default values"""
        self.gains: List[float] = [band[2] for band in self.BANDS]  # dB values
        self.enabled = False
    
    def set_band(self, band_index: int, gain_db: float) -> None:
        """
        Set gain for a specific frequency band
        
        Args:
            band_index: Index of the band (0-4)
            gain_db: Gain in decibels (-12 to +12)
        """
        if 0 <= band_index < len(self.gains):
            self.gains[band_index] = max(-12.0, min(12.0, gain_db))
    
    def get_band(self, band_index: int) -> float:
        """Get the gain for a specific band"""
        if 0 <= band_index < len(self.gains):
            return self.gains[band_index]
        return 0.0
    
    def get_all_bands(self) -> List[float]:
        """Get all band gains"""
        return self.gains.copy()
    
    def reset(self) -> None:
        """Reset all bands to 0 dB"""
        self.gains = [0.0 for _ in self.BANDS]
    
    def preset_flat(self) -> None:
        """Apply flat preset"""
        self.reset()
    
    def preset_bass_boost(self) -> None:
        """Apply bass boost preset"""
        self.gains = [6.0, 3.0, 0.0, -2.0, -4.0]
    
    def preset_treble_boost(self) -> None:
        """Apply treble boost preset"""
        self.gains = [-4.0, -2.0, 0.0, 3.0, 6.0]
    
    def preset_vocal(self) -> None:
        """Apply vocal preset"""
        self.gains = [-2.0, 4.0, 6.0, 3.0, -1.0]
    
    def get_presets(self) -> Dict[str, callable]:
        """Get available presets"""
        return {
            'Flat': self.preset_flat,
            'Bass Boost': self.preset_bass_boost,
            'Treble Boost': self.preset_treble_boost,
            'Vocal': self.preset_vocal,
        }


class AudioFader:
    """Audio fader for smooth volume transitions"""
    
    def __init__(self, current_volume: float = 0.7):
        """
        Initialize fader
        
        Args:
            current_volume: Initial volume level (0.0 to 1.0)
        """
        self.current_volume = max(0.0, min(1.0, current_volume))
        self.target_volume = self.current_volume
        self.fade_speed = 0.05  # Change per frame
        self.is_fading = False
    
    def set_target(self, target_volume: float, speed: float = 0.05) -> None:
        """
        Set target volume for fading
        
        Args:
            target_volume: Target volume (0.0 to 1.0)
            speed: Fade speed per frame (higher = faster)
        """
        self.target_volume = max(0.0, min(1.0, target_volume))
        self.fade_speed = max(0.01, min(0.2, speed))
        self.is_fading = abs(self.current_volume - self.target_volume) > 0.01
    
    def fade_to_mute(self, speed: float = 0.05) -> None:
        """Fade out to mute"""
        self.set_target(0.0, speed)
    
    def fade_to_max(self, speed: float = 0.05) -> None:
        """Fade in to maximum"""
        self.set_target(1.0, speed)
    
    def update(self) -> float:
        """
        Update fader state and return current volume
        
        Returns:
            Current volume level (0.0 to 1.0)
        """
        if self.is_fading:
            if abs(self.current_volume - self.target_volume) < self.fade_speed:
                self.current_volume = self.target_volume
                self.is_fading = False
            else:
                if self.current_volume < self.target_volume:
                    self.current_volume += self.fade_speed
                else:
                    self.current_volume -= self.fade_speed
        
        return self.current_volume
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.current_volume
    
    def set_immediate(self, volume: float) -> None:
        """Set volume immediately without fading"""
        self.current_volume = max(0.0, min(1.0, volume))
        self.target_volume = self.current_volume
        self.is_fading = False
