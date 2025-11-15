#!/usr/bin/env python3
"""
Test script to demonstrate equalizer functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.audio_effects import Equalizer

def test_equalizer():
    """Test equalizer functionality"""
    print("Testing JukeBox Equalizer")
    print("=" * 40)
    
    eq = Equalizer()
    
    # Test flat EQ
    print("1. Flat EQ (no adjustment):")
    print(f"   Volume adjustment: {eq.get_volume_adjustment():.2f}x")
    print(f"   Applied to 50% volume: {eq.apply_to_volume(0.5):.2f}")
    print()
    
    # Test bass boost
    print("2. Bass Boost preset:")
    eq.preset_bass_boost()
    print(f"   Gains: {eq.get_all_bands()}")
    print(f"   Volume adjustment: {eq.get_volume_adjustment():.2f}x")
    print(f"   Applied to 50% volume: {eq.apply_to_volume(0.5):.2f}")
    emphasis = eq.get_frequency_emphasis()
    print(f"   Frequency emphasis: Bass={emphasis['bass']:.1f}dB, Mid={emphasis['mid']:.1f}dB, Treble={emphasis['treble']:.1f}dB")
    print()
    
    # Test treble boost
    print("3. Treble Boost preset:")
    eq.preset_treble_boost()
    print(f"   Gains: {eq.get_all_bands()}")
    print(f"   Volume adjustment: {eq.get_volume_adjustment():.2f}x")
    print(f"   Applied to 50% volume: {eq.apply_to_volume(0.5):.2f}")
    emphasis = eq.get_frequency_emphasis()
    print(f"   Frequency emphasis: Bass={emphasis['bass']:.1f}dB, Mid={emphasis['mid']:.1f}dB, Treble={emphasis['treble']:.1f}dB")
    print()
    
    # Test vocal preset
    print("4. Vocal preset:")
    eq.preset_vocal()
    print(f"   Gains: {eq.get_all_bands()}")
    print(f"   Volume adjustment: {eq.get_volume_adjustment():.2f}x")
    print(f"   Applied to 50% volume: {eq.apply_to_volume(0.5):.2f}")
    emphasis = eq.get_frequency_emphasis()
    print(f"   Frequency emphasis: Bass={emphasis['bass']:.1f}dB, Mid={emphasis['mid']:.1f}dB, Treble={emphasis['treble']:.1f}dB")
    print()
    
    # Test custom settings
    print("5. Custom extreme settings:")
    eq.reset()
    eq.set_band(0, 12.0)  # Max bass
    eq.set_band(2, -12.0)  # Min mid
    eq.set_band(4, 12.0)  # Max treble
    print(f"   Gains: {eq.get_all_bands()}")
    print(f"   Volume adjustment: {eq.get_volume_adjustment():.2f}x")
    print(f"   Applied to 50% volume: {eq.apply_to_volume(0.5):.2f}")
    print()
    
    print("Equalizer test complete!")
    print("\nTo test in JukeBox:")
    print("1. Run: PYTHONPATH=. python3 src/main.py")
    print("2. Open Config -> Equalizer")  
    print("3. Adjust sliders or apply presets")
    print("4. Play music and notice volume changes based on EQ settings")

if __name__ == "__main__":
    test_equalizer()