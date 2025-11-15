# Side Navigation Buttons Documentation

## Overview
Side navigation buttons have been added to the main screen to allow users to easily browse through albums without disrupting playback. The buttons are positioned on the left and right edges of the screen for intuitive navigation.

## Button Placement
- **Left Navigation Button (`<`)**: Positioned at the left edge of the screen, vertically centered
  - Location: `x=10, y=height/2-30`
  - Size: `30px width x 60px height`
  - Color: Blue
  - Function: Scrolls the album view backward by 1 album

- **Right Navigation Button (`>`)**: Positioned at the right edge of the screen, vertically centered
  - Location: `x=width-40, y=height/2-30`
  - Size: `30px width x 60px height`
  - Color: Blue
  - Function: Scrolls the album view forward by 1 album

## Functionality

### Album View Offset
The system uses an `album_view_offset` state variable to track the user's navigation position:
- **Initial Value**: 0 (displays albums relative to currently playing album)
- **Positive Offset**: Navigates forward through the album library
- **Negative Offset**: Navigates backward through the album library
- **Wraparound**: Uses modulo arithmetic to wrap around at library ends

### Display Logic
When the right navigation button (`>`) is clicked:
```python
self.album_view_offset += 1
```

When the left navigation button (`<`) is clicked:
```python
self.album_view_offset -= 1
```

The main screen then displays albums relative to the offset:
```python
display_album_idx = (current_album_idx + self.album_view_offset) % len(albums)
```

This ensures the view wraps around when reaching the beginning or end of the library.

### 3-Column Display Update
The 3-column x 2-row layout automatically updates based on the offset:
- **Left Column**: Shows albums 2 positions before the displayed center album
- **Center Column**: Shows the album at the display offset
- **Right Column**: Shows albums 1 and 2 positions after the displayed center album

## User Interaction

### Hover Effects
- Buttons highlight when the mouse hovers over them
- Uses the same hover system as other UI buttons

### Click Handling
- Buttons are clickable areas that update the `album_view_offset`
- Clicking triggers an immediate screen refresh showing the new albums
- Current album playback continues uninterrupted

## Code Changes

### UI Class Updates
1. **`__init__()` method**:
   - Added `self.album_view_offset = 0` state variable
   - Added `self.left_nav_button` and `self.right_nav_button` Button objects

2. **`setup_buttons()` method**:
   - Created left and right navigation buttons with blue color

3. **`handle_events()` method**:
   - Added mouse motion hover updates for navigation buttons
   - Added click handling for navigation buttons that modify `album_view_offset`

4. **`draw_main_screen()` method**:
   - Modified album index calculation to use `album_view_offset`
   - Added button rendering at the end of the method
   - Updated display logic to show albums based on offset

## Benefits
- **Non-intrusive Navigation**: Doesn't interfere with playback controls
- **Visual Accessibility**: Buttons positioned at screen edges for easy discovery
- **Smooth Scrolling**: Users can quickly browse adjacent albums
- **Wraparound Support**: Seamlessly cycles through the entire library

## Technical Details
- Button positions calculated as fractions of screen width/height for responsiveness
- Modulo arithmetic ensures safe wraparound handling
- Hover state updates synchronized with other button hover logic
- Display refresh happens on the next `pygame.display.flip()` call
