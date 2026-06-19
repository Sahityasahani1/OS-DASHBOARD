# Code Structure & Architecture Guide — v3.0

## 📋 Overview

The OS Resource Dashboard v3.0 is built with **Dash** (a web framework from Plotly). It features a glassmorphism UI, 6 scheduling algorithms, real-time resource monitoring, and an educational process simulator — all in a single Python file.

---

## 📁 File Structure

```
OS-DASHBOARD/
├── OSdashbord.py         ← Main application file (~1300 lines)
├── requirements.txt      ← Python dependencies
├── README.md             ← Full documentation
├── QUICK_START.md        ← Quick user guide
└── CODE_STRUCTURE.md     ← This file!
```

---

## 🏗️ Code Organization (OSdashbord.py)

### Section 1: Module Documentation & Imports
```python
"""Module docstring — features list"""
import dash, plotly, random, datetime
```
- Explains the app's purpose and all features
- Imports all necessary libraries (no pandas dependency in v3.0)

### Section 2: Custom HTML Template (`app.index_string`)
```python
app.index_string = '''<!DOCTYPE html>...'''
```
- **Google Fonts**: JetBrains Mono + Inter
- **CSS Animations**: `neonPulse`, `borderGlow`, `slideInLeft`, `pulseRed`
- **Glassmorphism cards**: `.glass-card`, `.glass-card-warm`, `.glass-card-terminal`
- **Button styles**: `.spawn-btn`, `.kill-btn`, `.control-btn`, `.preset-btn`
- **Log entry styles**: `.log-approved`, `.log-denied`, `.log-kill`, `.log-deadlock`, etc.
- **Dark theme dropdown overrides**: `.Select-control`, `.Select-menu-outer`

### Section 3: Configuration & Constants
```python
COLORS = {...}             # Color palette (cyan, red, yellow, blue, purple)
RESOURCE_LIMITS = {...}    # Min/max values for CPU, RAM, Disk, lifetime, PID
PROCESS_PRESETS = {...}    # 5 preset templates (Browser, Game, Editor, Database, Compiler)
ALGO_INFO = {...}          # Descriptions for all 6 scheduling algorithms
```
**Why?** Centralizing these makes the code easy to maintain and customize.

### Section 4: Scheduling Algorithms (6 functions)
```python
def apply_fifo_scheduling(processes)
def apply_round_robin_scheduling(processes, time_quantum=10)
def apply_sjf_scheduling(processes)
def apply_priority_scheduling(processes)
def apply_random_scheduling(processes)
def apply_srtn_scheduling(processes)
```
Each function takes a list of process dicts and returns the modified list after one tick of scheduling.

### Section 5: Application Layout
```python
app.layout = html.Div(children=[
    # Title (neon animated)
    # Stats ribbon (5 stat cards)
    # Three-column section (System Load | Process Injector | Kernel Logs)
    # Resource History chart
    # Process Control section (Gantt + Table + Kill buttons)
    # Hidden state stores (5 dcc.Store) + Interval timer
])
```

### Section 6: Callbacks (10 total)
```python
fill_preset()           # Preset buttons → fill form
update_algo_info()      # Dropdown → algorithm info card
toggle_pause()          # Pause button → disable interval
change_speed()          # Speed slider → adjust interval ms
os_kernel_loop()        # Main kernel (scheduling, spawn, kill, deadlock)
render_system_metrics() # State → charts + table
render_history_chart()  # History → line chart
render_gantt_chart()    # Gantt → timeline bar chart
render_kernel_logs()    # Log entries → colored HTML divs
render_stats()          # Stats → ribbon cards
```

### Section 7: Entry Point
```python
if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🔄 Data Flow

```
User Action (click button, move slider, select preset)
         ↓
Callback triggered (@app.callback)
         ↓
State stores updated (processes, logs, stats, gantt, history)
         ↓
Dependent callbacks fire automatically
         ↓
Charts, table, logs, stats re-render
         ↓
User sees updated dashboard
```

### Store → Callback Dependencies
```
state-store  ──→ render_system_metrics() ──→ CPU gauge, RAM bar, Disk bar, Table
log-store    ──→ render_kernel_logs()    ──→ Color-coded log entries
stats-store  ──→ render_stats()          ──→ Stats ribbon cards
gantt-store  ──→ render_gantt_chart()    ──→ Scheduling timeline
history-store──→ render_history_chart()  ──→ 60s resource graph
```

---

## 🎯 Key Components Explained

### Colors Dictionary
```python
COLORS = {
    'bg': '#0a0a0f',          # Near-black background
    'cyan': '#00ffcc',        # Primary accent (neon green)
    'red': '#ff0055',         # Danger / high usage
    'yellow': '#ffcc00',      # Warning / memory
    'blue': '#00ccff',        # Info / history
    'text': '#e0e0e0',        # Primary text
    'text_dim': '#888',       # Secondary text
}
```

### Process Presets
```python
PROCESS_PRESETS = {
    'browser':  {'name': 'WebBrowser',   'cpu': 25,  'mem': 512,  'disk': 30,  ...},
    'game':     {'name': 'GameEngine',   'cpu': 60,  'mem': 1024, 'disk': 100, ...},
    'editor':   {'name': 'TextEditor',   'cpu': 3,   'mem': 64,   'disk': 5,   ...},
    'database': {'name': 'PostgreSQL',   'cpu': 15,  'mem': 256,  'disk': 200, ...},
    'compiler': {'name': 'GCC-Compiler', 'cpu': 40,  'mem': 512,  'disk': 80,  ...},
}
```
Used by the pattern-matching callback `fill_preset()` via `Input({'type': 'preset-btn', 'index': ALL}, 'n_clicks')`.

### Algorithm Info
```python
ALGO_INFO = {
    'fifo': {
        'name': 'FIFO (First In, First Out)',
        'type': 'Non-Preemptive',          # Badge color depends on this
        'desc': '...',                      # Explanation text
        'pros': 'Simple, no starvation',    # ✅ Green text
        'cons': 'Convoy effect',            # ⚠️ Orange text
        'fairness': '⭐⭐',               # Star rating
    },
    # ... 5 more algorithms
}
```

---

## 🔌 Callback Functions Explained

### Main Kernel Loop: `os_kernel_loop()`
**6 Outputs:** state-store, log-store, selected_rows, stats-store, gantt-store, history-store

**5 Inputs (triggers):**
1. ⏱️ Clock tick (every 1 second / adjusted by speed)
2. 🔘 Spawn button click
3. 🔫 Kill button click
4. 💀 Kill All button click
5. 🧹 Clear Logs button click

**Logic Flow:**
```
If clear-log → reset log entries only
If kill-all → terminate all processes, update stats
If clock-tick:
    Check for deadlock (over-allocation)
    Apply scheduling algorithm
    Detect executing process (compare Time Left before/after)
    Log completed processes
    Update Gantt, History, Stats
    Annotate State (RUNNING/READY) and Priority
If spawn-btn:
    Validate name exists
    Check admission control (resource limits)
    Create process or log denial
If kill-btn:
    Remove selected processes, log kills
Finalize: set active count, limit log size
```

### Render System Metrics: `render_system_metrics()`
**Creates 3 charts:**
1. **CPU Gauge** — `go.Indicator` with color thresholds (cyan/yellow/red)
2. **Memory Bar** — Overlaid `go.Bar` (background track + filled usage)
3. **Disk Bar** — Same overlay pattern as memory

**Also builds table data**, filtering to display columns only (strips internal fields like `time_used`).

### History Chart: `render_history_chart()`
- Three `go.Scatter` traces with `fill='tozeroy'` and `shape='spline'`
- Sliding 60-point x-axis window
- Unified hover mode

### Gantt Chart: `render_gantt_chart()`
- One `go.Bar` trace per PID, colored from a 10-color palette
- IDLE periods shown in dark gray (PID 0)
- Horizontal legend at top

---

## 🎨 CSS Architecture

### Animation Keyframes
| Animation | Effect | Used On |
|-----------|--------|---------|
| `neonPulse` | Glowing text shadow | Dashboard title |
| `borderGlow` | Pulsing border color | `.glass-card` |
| `slideInLeft` | Fade-in from left | Log entries |
| `pulseRed` | Flashing red background | Deadlock logs |

### Card Classes
| Class | Background | Border | Used For |
|-------|-----------|--------|----------|
| `.glass-card` | Dark blue gradient | Cyan glow | System Load, Process Injector, History |
| `.glass-card-warm` | Dark amber gradient | Yellow border | Process Control section |
| `.glass-card-terminal` | Near-black gradient | Cyan border | Kernel Logs |
| `.stat-card` | Dark blue, no gradient | Cyan border | Stats ribbon items |

### Log Entry Classes
| Class | Color | Border | Event Type |
|-------|-------|--------|------------|
| `.log-approved` | Cyan | Cyan | Process spawned |
| `.log-denied` | Red | Red | Admission denied |
| `.log-kill` | Red | Red | Process killed |
| `.log-exit` | Gray | Gray | Process completed |
| `.log-scheduler` | Blue | Blue | Scheduler info |
| `.log-deadlock` | Red + pulse | Red | Deadlock detected |
| `.log-warn` | Yellow | Yellow | Warnings |
| `.log-system` | Cyan | Cyan | System messages |

---

## 🔐 State Management (5 Stores)

| Store | Type | Initial Value |
|-------|------|---------------|
| `state-store` | List[Dict] | `[]` |
| `log-store` | List[Dict] | `[{level: 'system', msg: 'Kernel Initialized'}]` |
| `stats-store` | Dict | `{spawned: 0, completed: 0, killed: 0, uptime: 0, active: 0}` |
| `gantt-store` | List[Dict] | `[]` |
| `history-store` | Dict[str, List] | `{cpu: [], mem: [], disk: []}` |

### Process Dict Structure
```python
{
    'PID': 1234,           # Random 1000–9999
    'Name': 'WebBrowser',  # User-provided or preset
    'CPU (%)': 25,         # CPU requirement
    'RAM (MB)': 512,       # Memory requirement
    'Disk I/O': 30,        # Disk I/O requirement
    'Time Left (s)': 28,   # Remaining lifetime (decremented by scheduler)
    'State': 'RUNNING',    # Set by kernel loop (RUNNING or READY)
    'Priority': 1,         # Queue position after scheduling
    'time_used': 5,        # Internal: Round-Robin quantum tracker (not displayed)
}
```

---

## 🎓 Learning Path

### To Understand This Code:

1. **Read the constants** — `COLORS`, `RESOURCE_LIMITS`, `PROCESS_PRESETS`, `ALGO_INFO`
2. **Trace a process lifecycle:**
   - Click preset → `fill_preset()` fills form
   - Click Spawn → `os_kernel_loop()` creates process
   - Process stored in `state-store` → `render_system_metrics()` updates charts
   - Each tick: scheduler selects a process → State set to RUNNING
   - Time Left reaches 0 → process removed, `[EXIT]` logged
3. **Study the scheduling algorithms** — each is a standalone function
4. **Modify and experiment** — change colors, add a new preset, try new algorithms

---

## 🚀 Next Steps

- Add GPU resource simulation
- Data persistence (export logs/stats to CSV)
- Multi-core CPU simulation
- Network I/O resource type
- Drag-and-drop process priority reordering
- Algorithm comparison mode (side-by-side)

---

This code demonstrates solid practices: clean organization, centralized configuration, 10 modular callbacks, and comprehensive documentation! 🎉
