# Main Screen Layout - 3 Column x 2 Row Design

## New Display Layout

The main screen has been completely redesigned with a professional 3-column by 2-row album card layout.

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                    JukeBox - Album Library                                     ║
║ [Play][Pause][Stop][Prev][Next][PrevAlb][NextAlb][Export][Config]           ║
├──────────────────────┬──────────────────────┬──────────────────────┤
│   LEFT COLUMN        │   CENTER COLUMN      │   RIGHT COLUMN       │
│   (Previous Albums)  │   (Current Album)    │   (Next Albums)      │
├──────────────────────┤                      ├──────────────────────┤
│  ┌────────────────┐  │   ┌──────────────┐   │  ┌────────────────┐  │
│  │ Album #XX      │  │   │ Album #YY ★  │   │  │ Album #ZZ      │  │
│  ├────────────────┤  │   ├──────────────┤   │  ├────────────────┤  │
│  │Artist: ....    │  │   │ [LARGE ART]  │   │  │Artist: ....    │  │
│  │Album: ....     │  │   │              │   │  │Album: ....     │  │
│  │Tracks:         │  │   │              │   │  │Tracks:         │  │
│  │ 1. Song....    │  │   ├──────────────┤   │  │ 1. Song....    │  │
│  │ 2. Song....    │  │   │Artist: ..... │   │  │ 2. Song....    │  │
│  │ 3. Song....    │  │   │Album: ...... │   │  │ 3. Song....    │  │
│  └────────────────┘  │   │               │   │  └────────────────┘  │
│                      │   │Now Playing:   │   │                      │
│  ┌────────────────┐  │   │Track #XX:.... │   │  ┌────────────────┐  │
│  │ Album #AA      │  │   │Duration: ...  │   │  │ Album #BB      │  │
│  ├────────────────┤  │   │               │   │  ├────────────────┤  │
│  │Artist: ....    │  │   │All Tracks:    │   │  │Artist: ....    │  │
│  │Album: ....     │  │   │ 1. Song..►    │   │  │Album: ....     │  │
│  │Tracks:         │  │   │ 2. Song...    │   │  │Tracks:         │  │
│  │ 1. Song....    │  │   │ 3. Song...    │   │  │ 1. Song....    │  │
│  │ 2. Song....    │  │   │ 4. Song...    │   │  │ 2. Song....    │  │
│  │ 3. Song....    │  │   │ 5. Song...    │   │  │ 3. Song....    │  │
│  └────────────────┘  │   │ ...           │   │  └────────────────┘  │
│                      │   └───────────────┘   │                      │
├──────────────────────┴──────────────────────┴──────────────────────┤
│                     Selection: ____ (AATT)                          │
│           [ 7 ][ 8 ][ 9 ]                                           │
│           [ 4 ][ 5 ][ 6 ]                                           │
│           [ 1 ][ 2 ][ 3 ]                                           │
│           [ 0 ][ < ]                                                │
│           [CLR][ ENT ]                                              │
├────────────────────────────────────────────────────────────────────┤
│ 4-digit: Album(2)+Track(2) | C: Config | Space: Play/Pause | N/P...│
╚════════════════════════════════════════════════════════════════════╝
```

## Column Layout Description

### LEFT COLUMN - Previous Albums (2 cards)
- **Top Card**: Previous Album (-1 from current)
  - Album number (highlighted)
  - Artist name
  - Album name
  - First 3 tracks
  
- **Bottom Card**: Album before previous (-2 from current)
  - Same layout as top card

### CENTER COLUMN - Current Playing Album (Large)
- **Large Album Display** with yellow border (★)
  - Large album art area with album number
  - Full artist name
  - Full album name
  - **"Now Playing" section** (if music from this album is playing):
    - Current track number and name
    - Track duration
  - **"All Tracks" section**:
    - Complete track listing
    - Current playing track marked with ►
    - Track durations shown
    - Yellow highlight on current track

### RIGHT COLUMN - Next Albums (2 cards)
- **Top Card**: Next Album (+1 from current)
  - Album number (highlighted)
  - Artist name
  - Album name
  - First 3 tracks
  
- **Bottom Card**: Album after next (+2 from current)
  - Same layout as top card

## Bottom Section

### Number Pad (Centered)
- **Selection Display**: Shows 4-digit input in real-time
- **5x2 Calculator Layout**:
  - Rows 1-3: Number buttons (7-9, 4-6, 1-3)
  - Row 4: 0, Backspace (<)
  - Row 5: Clear (CLR), Enter (ENT)
- Color coded:
  - Green: ENT (Enter)
  - Red: CLR (Clear)
  - Blue: < (Backspace)
  - Gray: Numbers

### Audio Controls
- Volume slider with label
- Fader button
- EQ button
- Equalizer display (when toggled)

### Instructions
- Keyboard shortcuts displayed at bottom

## Album Card Details

### Card Components
1. **Album Art Area** (gray rectangle)
   - Displays large album number in center
   
2. **Album Info Section**
   - Artist name
   - Album name
   
3. **Track List**
   - Shows first 3 tracks
   - Format: `N. Track Name`

### Card Styling
- Dark gray background
- Light gray border (2px)
- Padding for spacing
- Text truncation for long names
- Fixed height of 280px for consistency

## Current Display Features

### Center Album Display
- **Yellow Border** indicates it's the current/playing album
- Shows **all tracks** in the album
- Current playing track marked with **►** symbol
- Yellow highlighting on current track
- Displays full information without truncation

### Left/Right Album Cards
- Compact format for quick browsing
- Shows **first 3 tracks only**
- Allows quick preview of adjacent albums
- Gray borders to distinguish from current

### Interactive Elements
- Album card hovering (future enhancement)
- Click to navigate to album (future enhancement)
- All buttons are clickable and show hover states

## Navigation

Users can navigate:
1. **Using 4-digit pad**: Enter AA (album) + TT (track)
2. **Using buttons**: 
   - `Prev Album` / `Next Album` buttons
   - Navigate adjacent albums
3. **Using keyboard**:
   - `N` / `P` keys for album navigation
   - Number keys for 4-digit selection

## Color Scheme

- **Yellow**: Current album border, album numbers, current track
- **White**: Main text, headers, album/artist names
- **Light Gray**: Secondary text, track listings
- **Gray**: Card backgrounds, button colors
- **Dark Gray**: Screen background
- **Green**: Status indicators, volume/duration
- **Red**: Error states

## Responsive Design

- Automatically adjusts column widths
- 1280px width assumed (standard)
- 800px height assumed (standard)
- Proportional spacing and margins
- Truncation of long text to fit columns

---

**Status**: ✅ **COMPLETE**

The new 3-column x 2-row layout provides:
- Better album browsing with visual cards
- Detailed view of current playing album
- Quick preview of upcoming/previous albums
- Centered number pad for easy selection
- Professional card-based design
