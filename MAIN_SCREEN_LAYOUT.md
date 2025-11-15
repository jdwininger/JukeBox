# Main Screen Layout - Professional JukeBox Interface

## Current Interface Design

The JukeBox features a sophisticated, responsive interface with complete theming support, PNG/SVG buttons, rollover highlights, and professional layout design.

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                         JukeBox - Album Library                                   ║
║ Volume: [████████░░] [▶][⏸][⏹]                              [⚙]                  ║
├────────────────────┬────────────────────────┬────────────────────┤
│   LEFT COLUMN      │     CENTER COLUMN      │   RIGHT COLUMN     │
│  (Browse Albums)   │   (Now Playing Box)    │  (Browse Albums)   │
├────────────────────┤                        ├────────────────────┤
│ ┌───────────────┐  │  ┌──────────────────┐  │ ┌───────────────┐  │
│ │ [📀] Album 01 │  │  │ ♪ Now Playing    │  │ │ [📀] Album 03 │  │
│ │ Prince        │  │  │ ┌──────────────┐ │  │ │ The 2 Live... │  │
│ │ Diamonds &... │  │  │ │  [📀] 01     │ │  │ │ As Nasty as...│  │
│ │ 13 tracks     │  │  │ │              │ │  │ │ 18 tracks     │  │
│ │ 1. Thunder... │  │  │ │              │ │  │ │ 1. The F...   │  │
│ │ 2. Daddy...   │  │  │ │              │ │  │ │ 2. We W...    │  │
│ │ 3. Diamond... │  │  │ │              │ │  │ │ 3. Me So...   │  │
│ └───────────────┘  │  │ └──────────────┘ │  │ └───────────────┘  │
│                    │  │ ♫ Track Title    │  │                    │
│ ┌───────────────┐  │  │ Selection 01 01  │  │ ┌───────────────┐  │
│ │ [📀] Album 02 │  │  │ ──────────────── │  │ │ [📀] Album 04 │  │
│ │ BABYMETAL     │  │  │                  │  │ │ David Bowie   │  │
│ │ BABYMETAL     │  │  │                  │  │ │ Earthling     │  │
│ │ 15 tracks     │  │  │                  │  │ │ 9 tracks      │  │
│ │ 1. BABYME...  │  │  │                  │  │ │ 1. Little...  │  │
│ │ 2. Iine      │  │  │                  │  │ │ 2. Looking... │  │
│ │ 3. Akatsuki  │  │  │                  │  │ │ 3. Battle...  │  │
│ └───────────────┘  │  └──────────────────┘  │ └───────────────┘  │
├────────────────────┴────────────────────────┴────────────────────┤
│                   [<] 4-Digit Selection Pad: [>]                  │
│                      ┌─────────────────────┐                      │
│                      │  Selection: ____    │                      │
│                      │ ┌─────────────────┐ │                      │
│                      │ │ [7] [8] [9]     │ │                      │
│                      │ │ [4] [5] [6]     │ │                      │
│                      │ │ [1] [2] [3]     │ │                      │
│                      │ │ [0] [<]         │ │                      │
│                      │ │ [CLR] [ENT]     │ │                      │
│                      │ └─────────────────┘ │                      │
│                      └─────────────────────┘                      │
├──────────────────────────────────────────────────────────────────┤
│ 4-digit: Album(2)+Track(2) | C: Config | Space: Play/Pause | ↑↓: Volume │
│                                                Queue: X songs      │
╚══════════════════════════════════════════════════════════════════════════════════╝
```

## Interface Components

### Header Section

#### Title Bar
- **Application Title**: "JukeBox - Album Library" (centered, large font)
- **Themed Background**: Full-width themed background image

#### Control Bar (Left to Right)
1. **Volume Control** (Left Side)
   - Volume label: "Volume"
   - Themed slider with track and knob
   - Real-time volume adjustment

2. **Media Control Buttons** (Center)
   - **Play Button** [▶]: PNG/SVG themed, square 50x50, rollover highlights
   - **Pause Button** [⏸]: PNG/SVG themed, square 50x50, rollover highlights  
   - **Stop Button** [⏹]: PNG/SVG themed, square 50x50, rollover highlights
   - Buttons scale with fullscreen/windowed mode
   - Brightness effect on hover (30% brighter)

3. **Configuration Button** (Right Side)
   - **Config Button** [⚙]: PNG/SVG themed gear icon, rollover highlights
   - Opens configuration screen with theme selection

### Main Content Area (3-Column Layout)

#### Left Column - Album Browsing (Albums 1 & 2)
**Top Card** (Album at browse_position)
- **Album Art**: Square album art with album number overlay
- **Artist**: Text wrapping for long names (16+ chars wrap at word boundaries)
- **Album Title**: Text wrapping (windowed: 14 chars, fullscreen: 28 chars)  
- **Track Count**: "X tracks" in blue
- **Track List**: First few tracks that fit in card space
- **Border**: White 2px border for definition

**Bottom Card** (Album at browse_position + 1)
- Same layout as top card

#### Center Column - Now Playing Display
**Enhanced Now Playing Box**
- **Yellow Border**: 3px border to indicate active status
- **Header**: "Now Playing" label in yellow
- **Large Album Art**: Centered, square format with album number
- **Track Information**: 
  - Current track title (large font, white)
  - Selection display "Selection XX YY" (medium gray)
- **Persistent Display**: Shows last played track even when stopped
- **Empty State**: "Choose an album and song." when nothing played

#### Right Column - Album Browsing (Albums 3 & 4)  
**Top Card** (Album at browse_position + 2)
- Same layout as left column cards

**Bottom Card** (Album at browse_position + 3)
- Same layout as left column cards

### Navigation Controls

#### Side Navigation Buttons
- **Left Button** [<]: 60x80 pixels (taller than wide), PNG/SVG themed
- **Right Button** [>]: 60x80 pixels (taller than wide), PNG/SVG themed
- **Positioning**: Beside number pad, equidistant spacing
- **Functionality**: Browse previous/next 4 albums
- **Responsive Scaling**: 
  - Fullscreen: 60x80 (1.0x scale)
  - Windowed: 45x60 (0.75x scale)
- **Rollover Effects**: Brighten 30% on hover

#### Browse Position System
- Shows 4 albums at once (positions 0, 1, 2, 3)
- Navigation moves by 4 albums at a time
- Prevents browsing before album 01 or past album 52
- Real-time updates when using navigation buttons

### Number Pad Section

#### Layout Design
- **Centered Positioning**: Dynamic centering regardless of screen size
- **Semi-transparent Border**: 15% black overlay border around entire pad
- **Responsive Scaling**: 
  - Fullscreen: Full size buttons and spacing
  - Windowed: 75% scale factor for proportional reduction

#### Button Layout (5 Rows)
```
Row 1: [7] [8] [9]
Row 2: [4] [5] [6]  
Row 3: [1] [2] [3]
Row 4: [0] [<]
Row 5: [CLR] [ENT]
```

#### Button Specifications
- **Bordered Buttons**: White 2px borders for clear definition
- **Color Coding**:
  - Numbers (0-9): Gray background with hover effects
  - CLR: Red background (clear function)
  - ENT: Green background (enter function)  
  - <: Blue background (backspace function)
- **Rollover Effects**: All buttons brighten when hovered
- **Responsive Sizing**: Scale with screen mode

#### Selection Display
- **Real-time Input**: Shows "Selection: XXXX" as user types
- **Color**: Yellow text when in selection mode
- **Auto-execution**: Executes automatically when 4 digits entered
- **Clear on Execute**: Resets after successful selection

### Footer Section

#### Instructions Bar
- **Comprehensive Help**: All keyboard shortcuts and usage instructions
- **Left Side**: "4-digit: Album(2) + Track(2) | C: Config | Space: Play/Pause | Alt+Enter: Fullscreen | ↑↓: Volume"
- **Dynamic Content**: Updates based on current mode

#### Status Information  
- **Queue Counter** (Right Side): "Queue: X song(s)" when queue has items
- **Theme Indicator**: Current theme shown in config screen

## Theming System Integration

### Visual Theming
- **Background Images**: Full themed backgrounds (1280x800) with scaling
- **Button Theming**: PNG/SVG support for all interactive elements
- **Color Consistency**: Theme colors used throughout interface
- **Real-time Switching**: Instant theme changes via Configuration screen

### Button Categories

#### PNG/SVG Themed (No Borders)
- ✅ Media control buttons (Play, Pause, Stop)
- ✅ Configuration button (Gear icon)
- ✅ Navigation buttons (< > arrows)
- Clean appearance with themed images
- Rollover brightness effects

#### Text-based Bordered Buttons  
- ✅ Number pad buttons (0-9, CLR, ENT, <)
- ✅ Configuration screen buttons
- ✅ Theme selection buttons
- White borders for clear definition
- Color-coded backgrounds

### Theme Selection Interface
- **Access**: Configuration screen > Theme Selection
- **Real-time Preview**: Instant switching when theme selected
- **Persistence**: Theme choice saved to configuration file
- **Discovery**: Automatic detection of all available themes

## Responsive Design Features

### Screen Mode Adaptability
- **Fullscreen Mode** (1.0x scale factor):
  - Full-size buttons and interface elements
  - Optimal spacing and proportions
  - Maximum readability

- **Windowed Mode** (0.75x scale factor):
  - Proportionally scaled interface
  - Maintains visual hierarchy
  - Compact but usable design

### Dynamic Layout Adjustments
- **Column Width**: Auto-adjusts based on screen width
- **Text Wrapping**: Intelligent word-boundary wrapping
- **Button Positioning**: Maintains relative spacing
- **Number Pad**: Always centered regardless of screen size

### Content Adaptation
- **Track Lists**: Shows tracks that fit available space
- **Text Truncation**: Smart truncation with ellipsis
- **Album Art**: Scales to fit allocated space
- **Font Sizing**: Adjusts based on fullscreen/windowed mode

## Interaction Design

### Hover Effects
- **Rollover Highlights**: 30% brightness increase on all buttons
- **Visual Feedback**: Immediate response to mouse presence
- **Consistent Behavior**: All interactive elements provide feedback
- **Performance**: Smooth, lag-free hover transitions

### Click Feedback
- **Button Depression**: Visual feedback on click
- **State Changes**: Immediate visual response
- **Audio Feedback**: System sounds for important actions
- **Error Handling**: Clear feedback for invalid operations

### Keyboard Navigation
- **Complete Support**: All functions accessible via keyboard
- **Shortcuts**: Intuitive key mappings
- **Number Input**: Direct numeric entry for song selection
- **Mode Switching**: Easy access to configuration and features

## Album Card Design

### Card Structure
1. **Album Art Section**
   - Square album art or placeholder
   - Album number overlay with white border
   - Consistent sizing across all cards

2. **Information Section**  
   - Artist name (with text wrapping)
   - Album title (with smart truncation)
   - Track count in blue
   - Track listing (as many as fit)

3. **Visual Styling**
   - White 2px borders for definition
   - Consistent padding and spacing
   - Professional card appearance
   - Readable typography hierarchy

### Content Management
- **Smart Truncation**: Preserves readability while fitting space
- **Priority Display**: Most important information always visible
- **Overflow Handling**: Graceful handling of long text
- **Consistent Heights**: All cards maintain same dimensions

## Performance Optimizations

### Rendering Efficiency
- **Background Caching**: Theme backgrounds cached after first load
- **Text Caching**: Frequently used text surfaces cached
- **Image Scaling**: Scaled images cached for reuse
- **Dirty Rectangle**: Only redraw changed screen areas

### Memory Management
- **Theme Assets**: Only current theme loaded in memory
- **Image Optimization**: Compressed PNG files for smaller memory footprint
- **Cache Limits**: Intelligent cache size management
- **Resource Cleanup**: Automatic cleanup of unused resources

---

## Current Status: ✅ PRODUCTION READY

The JukeBox interface now features:

### ✅ **Complete Theming System**
- PNG/SVG button support with automatic fallbacks
- Real-time theme switching via Configuration screen
- Professional theme assets for all built-in themes
- Comprehensive theming documentation

### ✅ **Enhanced User Experience** 
- Rollover highlights on all interactive elements
- Responsive scaling for fullscreen/windowed modes
- Smart text wrapping and truncation
- Professional visual feedback

### ✅ **Robust Navigation**
- Side navigation buttons (< >) for album browsing
- 4-digit selection system with real-time feedback
- Browse position system showing 4 albums at once
- Keyboard shortcuts for all major functions

### ✅ **Professional Layout**
- 3-column responsive design
- Enhanced Now Playing display with persistence
- Centered number pad with semi-transparent border
- Comprehensive status and instruction displays

The interface provides a polished, professional music library experience with complete customization capabilities and intuitive navigation.
