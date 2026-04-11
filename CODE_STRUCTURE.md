# Code Structure & Architecture Guide

## 📋 Overview

The OS Resource Dashboard is built with **Dash** (a web framework from Plotly). Here's how it's organized:

---

## 📁 File Structure

```
OS ESE LAB/
├── OSdashbord.py         ← Main application file
├── requirements.txt      ← Python dependencies
├── README.md             ← Full documentation
├── QUICK_START.md        ← Quick user guide
└── CODE_STRUCTURE.md     ← This file!
```

---

## 🏗️ Code Organization (OSdashbord.py)

### Section 1: Module Documentation & Imports
```python
"""Module docstring explaining what the app does"""
import dash, plotly, pandas, random, datetime
```
- Explains the app's purpose and features
- Imports all necessary libraries

### Section 2: Configuration & Constants
```python
COLORS = {...}           # Color definitions
SPACING = {...}          # Layout spacing values
RESOURCE_LIMITS = {...}  # Min/max values for resources
LABELS = {...}           # User-facing text
```
**Why?** Centralizing these makes the code easy to maintain and customize.

### Section 3: Utility Functions
```python
def get_styled_div(flex=1, padding=None)
def get_styled_input(width='100%', margin_bottom='15px')
def get_styled_button(background_color, text_color='#000')
```
**Why?** Reusable functions reduce code duplication and ensure consistency.

### Section 4: Application Layout
```python
app.layout = html.Div(
    children=[
        # Header
        # Three-column section (System Load | Process Injector | Kernel Logs)
        # Process table
        # Hidden data stores
    ]
)
```
**Why?** Clean separation makes the UI structure obvious at a glance.

### Section 5: Callbacks (Application Logic)
```python
@app.callback(...)
def os_kernel_loop(...):
    """Handles spawning, terminating, and lifecycle management"""

@app.callback(...)
def render_system_metrics(...):
    """Updates all charts and graphs"""
```
**Why?** Callbacks connect user interactions to data updates.

### Section 6: Entry Point
```python
if __name__ == '__main__':
    app.run(debug=True)
```
**Why?** Allows the file to be both imported and run directly.

---

## 🔄 Data Flow

```
User Action (click button, move slider)
         ↓
Callback triggered (@app.callback)
         ↓
Process data updated / modified
         ↓
New state stored (dcc.Store)
         ↓
Charts & table re-render automatically
         ↓
User sees updated dashboard
```

---

## 🎯 Key Components Explained

### Colors Dictionary
```python
COLORS = {
    'background': '#121212',        # Dark gray
    'text_accent_cyan': '#00ffcc',  # Bright green
    # ... more colors
}
```
- Centralized color management
- Easy to apply a different theme (change one place, affects entire app)
- Improves readability with descriptive names

### Resource Limits
```python
RESOURCE_LIMITS = {
    'cpu_max': 100,              # Maximum CPU %
    'memory_max': 2048,          # Maximum RAM in MB
    'process_lifetime_min': 15,  # Minimum process duration
    # ... more limits
}
```
- All limits in one place
- Easy to adjust simulator behavior
- Self-documenting code

### Labels
```python
LABELS = {
    'title': 'OS Resource Dashboard v2.0',
    'spawn_button': 'Spawn Process',
    # ... more labels
}
```
- Centralized text reduces typos
- Easy to update text in bulk
- Could be extended for localization

---

## 🔌 Callback Functions Explained

### Callback 1: os_kernel_loop()
**Purpose:** Handles all process lifecycle events

**Triggered by:**
1. ⏱️ Clock tick (every 1 second)
2. 🔘 Spawn button click
3. 🔫 Kill button click

**What it does:**
```
If clock tick:
    - Decrease "Time Left" for each process
    - Remove processes with time_left == 0
    - Log completion events

If spawn button clicked:
    - Generate new PID (1000-9999)
    - Create process dict
    - Add to process list
    - Log creation event

If kill button clicked:
    - Remove selected process from list
    - Log termination event
```

**Returns:**
- Updated process list
- Updated kernel log
- Clear selection highlight

### Callback 2: render_system_metrics()
**Purpose:** Update visualizations with current data

**Input:**
- Current list of processes

**Calculates:**
```
total_cpu = sum of all CPU % values
total_memory = sum of all RAM MB values
total_disk = sum of all Disk I/O values
```

**Creates:**
1. **CPU Gauge** - Dial chart showing CPU %
2. **Memory Bar** - Horizontal bar showing RAM
3. **Disk Bar** - Horizontal bar showing Disk I/O

**Returns:**
- Process table data
- Three updated chart figures

---

## 🎨 UI Layout Explained

### Three-Column Layout
```
┌────────────────────────────────────────┐
│  HEADER: "OS Resource Dashboard v2.0"  │
├────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ System   │ │ Process  │ │ Kernel │ │
│  │ Load     │ │ Injector │ │ Logs   │ │
│  │          │ │          │ │        │ │
│  │ CPU      │ │ Sliders  │ │ Events │ │
│  │ RAM      │ │ Buttons  │ │        │ │
│  │ Disk     │ │          │ │        │ │
│  └──────────┘ └──────────┘ └────────┘ │
├────────────────────────────────────────┤
│  PROCESS TABLE                         │
│  ┌──────────────────────────────────┐  │
│  │ PID | Name | CPU | RAM | Time... │  │
│  │ 1234| app  | 25  | 512 | 12     │  │
│  └──────────────────────────────────┘  │
│  [SIGKILL Button]                      │
└────────────────────────────────────────┘
```

### Component Types Used

| Component | Purpose |
|-----------|---------|
| `html.Div` | Container/layout grouping |
| `html.H1, H3` | Headings |
| `dcc.Graph` | Charts (Plotly) |
| `dcc.Input` | Text input field |
| `dcc.Slider` | Range input |
| `html.Button` | Clickable button |
| `dcc.Textarea` | Multi-line text display |
| `dash_table.DataTable` | Tabular data display |
| `dcc.Store` | Client-side data storage |
| `dcc.Interval` | Timer/clock trigger |

---

## 🔐 State Management

### dcc.Store (Hidden Data Container)
```python
dcc.Store(id='state-store', data=[])
```
- Stores the list of processes
- Updated by os_kernel_loop()
- Read by render_system_metrics()
- Persists during session (resets on page refresh)

### dcc.Interval (Timer)
```python
dcc.Interval(id='clock-tick', interval=1000, n_intervals=0)
```
- Triggers callback every 1000 milliseconds (1 second)
- Drives process timer countdown
- Enables real-time updates

---

## 📊 Chart Creation

### CPU Gauge (Speedometer)
```python
go.Indicator(
    mode="gauge+number",
    value=cpu_total,  # Current value
    gauge={
        'axis': {'range': [None, 100]},      # 0-100% scale
        'bar': {'color': '#00ffcc'},         # Green bar
        'steps': [{'range': [85, 100], ...}] # Red zone alert
    }
)
```

### Memory Bar
```python
go.Bar(
    x=[memory_total],    # Value
    y=['RAM'],           # Label
    orientation='h',     # Horizontal
    marker_color='#ffcc00'  # Yellow
)
```

---

## 🎓 Learning Path

### To Understand This Code:

1. **Read the docstrings** in each function
2. **Trace a process lifecycle:**
   - Click "Spawn Process" → os_kernel_loop() called
   - Process added to list → stored in dcc.Store
   - render_system_metrics() called → charts update
   - Each second: os_kernel_loop() decrements timers
   - Process timeout → logs [EXIT] event

3. **Modify and experiment:**
   - Change a color in COLORS dict
   - Adjust a limit in RESOURCE_LIMITS
   - Add a new chart or label

---

## 🔧 Common Modifications

### Change Dark Theme to Light
```python
COLORS = {
    'background': '#ffffff',
    'surface': '#f5f5f5',
    'text_primary': '#000000',
    # ... etc
}
```

### Add More Resource Types
```python
RESOURCE_LIMITS = {
    'gpu_min': 0,
    'gpu_max': 100,
    'gpu_default': 10,
    # ... etc
}
# Then add sliders in the UI layout
```

### Persist Data on Restart
```python
import json
# Save to file before exiting
# Load from file on startup
```

---

## 📈 Performance Considerations

- **Update Interval:** 1 second (adjust `interval=1000` in dcc.Interval)
- **Log Size:** Limited to 20 lines (adjust in RESOURCE_LIMITS['max_log_lines'])
- **Max Processes:** No hard limit, but UI slows with 100+ processes
- **Memory:** Grows as processes are created (cycle them to test limits)

---

## 🚀 Next Steps to Learn

1. **Dash Tutorial:** https://dash.plotly.com/
2. **Plotly Graphs:** https://plotly.com/python/
3. **HTML/CSS Basics:** Essential for UI customization
4. **Python Web Apps:** Framework concepts & patterns

---

This code demonstrates solid practices: clear organization, reusable components, centralized configuration, and comprehensive documentation! 🎉
