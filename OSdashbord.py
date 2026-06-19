"""
OS Resource Dashboard v3.0
An interactive dashboard to monitor and manage OS resource allocation and processes.

Features:
- Real-time CPU, Memory, and Disk I/O monitoring with 60s history graph
- 6 scheduling algorithms with visual explanations and Gantt timeline
- Process spawning with preset templates (Browser, Game, Editor, Database, Compiler)
- Active process management with State/Priority tracking
- Color-coded kernel event logging with level indicators
- Pause/Resume scheduler with speed control (0.5x–4x)
- System statistics ribbon (Uptime, Spawned, Completed, Killed, Active)
- Deadlock detection and admission control
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx, ALL
import plotly.graph_objs as go
import random
from datetime import datetime

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "OS Resource Dashboard v3.0"

# Custom HTML template with Google Fonts, CSS animations, and glassmorphism
app.index_string = '''<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0a0f; font-family: 'JetBrains Mono', 'Consolas', monospace; }

        /* ====== Animations ====== */
        @keyframes neonPulse {
            0%, 100% { text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc44, 0 0 40px #00ffcc22; }
            50% { text-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc33, 0 0 20px #00ffcc11; }
        }
        @keyframes borderGlow {
            0%, 100% { border-color: rgba(0,255,204,0.12); box-shadow: 0 0 15px rgba(0,255,204,0.04); }
            50% { border-color: rgba(0,255,204,0.3); box-shadow: 0 0 25px rgba(0,255,204,0.08); }
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseRed {
            0%, 100% { background-color: rgba(255, 0, 85, 0.08); }
            50% { background-color: rgba(255, 0, 85, 0.2); }
        }

        /* ====== Card Styles ====== */
        .glass-card {
            background: linear-gradient(135deg, rgba(18,18,28,0.95), rgba(12,12,22,0.98));
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0,255,204,0.12);
            border-radius: 16px;
            padding: 24px;
            animation: borderGlow 4s ease-in-out infinite;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,255,204,0.06);
        }
        .glass-card-warm {
            background: linear-gradient(135deg, rgba(22,18,12,0.95), rgba(16,14,10,0.98));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,204,0,0.15);
            border-radius: 16px;
            padding: 24px;
            transition: transform 0.25s ease;
        }
        .glass-card-terminal {
            background: linear-gradient(135deg, rgba(5,5,12,0.98), rgba(2,2,8,0.99));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0,255,204,0.2);
            border-radius: 16px;
            padding: 20px;
        }

        /* ====== Stat Cards ====== */
        .stat-card {
            background: linear-gradient(135deg, rgba(20,20,30,0.95), rgba(12,12,22,0.95));
            border: 1px solid rgba(0,255,204,0.12);
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
            flex: 1;
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            border-color: rgba(0,255,204,0.35);
            transform: scale(1.03);
            box-shadow: 0 4px 20px rgba(0,255,204,0.08);
        }

        /* ====== Preset Buttons ====== */
        .preset-btn {
            background: linear-gradient(135deg, rgba(25,25,40,0.95), rgba(18,18,30,0.95));
            border: 1px solid rgba(0,255,204,0.18);
            border-radius: 10px;
            padding: 10px 14px;
            color: #d0d0d0;
            cursor: pointer;
            transition: all 0.25s ease;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            text-align: center;
            flex: 1;
        }
        .preset-btn:hover {
            border-color: #00ffcc;
            background: linear-gradient(135deg, rgba(0,255,204,0.12), rgba(0,255,204,0.04));
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,255,204,0.12);
            color: #00ffcc;
        }

        /* ====== Action Buttons ====== */
        .spawn-btn {
            background: linear-gradient(135deg, #00ffcc, #00cc99) !important;
            border: none !important; border-radius: 10px !important;
            padding: 13px 24px !important; font-weight: 700 !important;
            font-size: 13px !important; cursor: pointer !important;
            transition: all 0.3s ease !important; text-transform: uppercase !important;
            letter-spacing: 1.5px !important; color: #000 !important;
            width: 100% !important; font-family: 'JetBrains Mono', monospace !important;
        }
        .spawn-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(0,255,204,0.35) !important;
        }
        .kill-btn {
            background: linear-gradient(135deg, #ff0055, #cc0044) !important;
            border: none !important; border-radius: 8px !important;
            padding: 10px 24px !important; color: #fff !important;
            font-weight: 700 !important; cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
        }
        .kill-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(255,0,85,0.3) !important;
        }
        .kill-all-btn {
            background: linear-gradient(135deg, #880033, #660022) !important;
            border: none !important; border-radius: 8px !important;
            padding: 10px 24px !important; color: #ff6688 !important;
            font-weight: 700 !important; cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
        }
        .kill-all-btn:hover {
            background: linear-gradient(135deg, #aa0044, #880033) !important;
            color: #fff !important;
            box-shadow: 0 6px 25px rgba(255,0,85,0.2) !important;
        }
        .control-btn {
            background: rgba(20,20,35,0.9) !important;
            border: 1px solid rgba(0,255,204,0.3) !important;
            border-radius: 8px !important; padding: 8px 20px !important;
            color: #00ffcc !important; font-weight: 600 !important;
            cursor: pointer !important; transition: all 0.25s ease !important;
            font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
        }
        .control-btn:hover {
            background: rgba(0,255,204,0.08) !important;
            border-color: #00ffcc !important;
        }
        .clear-btn {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 6px !important; padding: 5px 14px !important;
            color: #666 !important; font-size: 11px !important;
            cursor: pointer !important; transition: all 0.2s ease !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        .clear-btn:hover {
            border-color: rgba(255,255,255,0.3) !important; color: #aaa !important;
        }

        /* ====== Kernel Log Entries ====== */
        .log-entry {
            padding: 5px 10px; border-radius: 4px; margin-bottom: 3px;
            font-size: 11.5px; font-family: 'JetBrains Mono', monospace;
            animation: slideInLeft 0.3s ease;
            border-left: 3px solid transparent; line-height: 1.5;
        }
        .log-approved  { color: #00ffcc; border-left-color: #00ffcc; background: rgba(0,255,204,0.04); }
        .log-denied    { color: #ff4477; border-left-color: #ff0055; background: rgba(255,0,85,0.04); }
        .log-kill      { color: #ff4477; border-left-color: #ff0055; background: rgba(255,0,85,0.06); }
        .log-exit      { color: #666;    border-left-color: #444; }
        .log-scheduler { color: #00ccff; border-left-color: #00ccff; background: rgba(0,204,255,0.04); }
        .log-deadlock  { color: #ff0055; border-left-color: #ff0055; background: rgba(255,0,85,0.12);
                         animation: slideInLeft 0.3s ease, pulseRed 2s ease-in-out infinite; font-weight: 600; }
        .log-system    { color: #00ffcc; border-left-color: #00ffcc; }
        .log-warn      { color: #ffcc00; border-left-color: #ffcc00; background: rgba(255,204,0,0.04); }

        /* ====== Scrollable Log Container ====== */
        .kernel-log-scroll {
            height: 380px; overflow-y: auto; padding-right: 6px;
        }
        .kernel-log-scroll::-webkit-scrollbar { width: 5px; }
        .kernel-log-scroll::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 3px; }
        .kernel-log-scroll::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.2); border-radius: 3px; }
        .kernel-log-scroll::-webkit-scrollbar-thumb:hover { background: rgba(0,255,204,0.4); }

        /* ====== Algorithm Info Box ====== */
        .algo-info-box {
            background: rgba(0,255,204,0.03);
            border: 1px solid rgba(0,255,204,0.12);
            border-radius: 10px; padding: 14px; margin: 10px 0 15px 0;
            font-size: 11px; line-height: 1.6;
        }

        /* ====== Section Titles ====== */
        .section-title {
            font-family: 'Inter', 'JetBrains Mono', sans-serif;
            font-weight: 600; margin-bottom: 16px; font-size: 16px; letter-spacing: 0.5px;
        }

        /* ====== DataTable Spacing ====== */
        .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
            border-collapse: separate !important; border-spacing: 0 3px !important;
        }

        /* ====== Dropdown Dark Theme ====== */
        .Select-control { background-color: rgba(15,15,25,0.9) !important; border-color: rgba(255,255,255,0.1) !important; }
        .Select-value-label, .Select-value { color: #e0e0e0 !important; }
        .Select-menu-outer { background-color: rgba(15,15,25,0.98) !important; border-color: rgba(255,255,255,0.1) !important; }
        .Select-option { background-color: rgba(15,15,25,0.98) !important; color: #e0e0e0 !important; }
        .Select-option.is-focused { background-color: rgba(0,255,204,0.15) !important; }
        .Select-arrow { border-color: #666 transparent transparent !important; }
        .Select-placeholder { color: #555 !important; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>'''

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

COLORS = {
    'bg': '#0a0a0f',
    'cyan': '#00ffcc',
    'red': '#ff0055',
    'yellow': '#ffcc00',
    'blue': '#00ccff',
    'purple': '#aa66ff',
    'text': '#e0e0e0',
    'text_dim': '#888',
    'text_muted': '#555',
}

RESOURCE_LIMITS = {
    'cpu_min': 1, 'cpu_max': 100, 'cpu_default': 15,
    'memory_min': 16, 'memory_max': 2048, 'memory_default': 256,
    'memory_max_system': 8192,
    'disk_min': 0, 'disk_max': 500, 'disk_default': 50,
    'disk_max_system': 1000,
    'process_lifetime_min': 15, 'process_lifetime_max': 45,
    'pid_min': 1000, 'pid_max': 9999,
    'max_log_entries': 50,
}

# Process preset templates for quick spawning
PROCESS_PRESETS = {
    'browser':  {'name': 'WebBrowser',   'cpu': 25,  'mem': 512,  'disk': 30,  'icon': '🌐', 'label': 'Browser'},
    'game':     {'name': 'GameEngine',   'cpu': 60,  'mem': 1024, 'disk': 100, 'icon': '🎮', 'label': 'Game'},
    'editor':   {'name': 'TextEditor',   'cpu': 3,   'mem': 64,   'disk': 5,   'icon': '📝', 'label': 'Editor'},
    'database': {'name': 'PostgreSQL',   'cpu': 15,  'mem': 256,  'disk': 200, 'icon': '🗄️', 'label': 'Database'},
    'compiler': {'name': 'GCC-Compiler', 'cpu': 40,  'mem': 512,  'disk': 80,  'icon': '🔬', 'label': 'Compiler'},
}

# Scheduling algorithm descriptions for the info card
ALGO_INFO = {
    'fifo': {
        'name': 'FIFO (First In, First Out)', 'type': 'Non-Preemptive',
        'desc': 'Processes execute in arrival order. The first process to arrive runs to completion before the next begins.',
        'pros': 'Simple, no starvation for arrived processes',
        'cons': 'Convoy effect — short processes wait behind long ones',
        'fairness': '⭐⭐',
    },
    'round_robin': {
        'name': 'Round-Robin (TQ=10s)', 'type': 'Preemptive',
        'desc': 'Each process gets a fixed time quantum (10s). After the quantum expires, the process moves to the back of the queue.',
        'pros': 'Fair CPU distribution, good response time',
        'cons': 'Context switch overhead, not optimal for throughput',
        'fairness': '⭐⭐⭐⭐',
    },
    'sjf': {
        'name': 'Shortest Job First', 'type': 'Non-Preemptive',
        'desc': 'The process with the shortest total burst time executes first. Optimal for minimizing average waiting time.',
        'pros': 'Minimum average waiting time',
        'cons': 'Starvation risk for long processes',
        'fairness': '⭐⭐',
    },
    'srtn': {
        'name': 'Shortest Remaining Time Next', 'type': 'Preemptive',
        'desc': 'Preemptive SJF — at every tick, the process with the least remaining time runs. New shorter jobs preempt longer ones.',
        'pros': 'Optimal average waiting time',
        'cons': 'High starvation risk, frequent context switches',
        'fairness': '⭐⭐',
    },
    'priority': {
        'name': 'Priority-Based (CPU %)', 'type': 'Non-Preemptive',
        'desc': 'Processes sorted by priority (lower CPU% = higher priority). The highest priority process executes first.',
        'pros': 'Important processes get CPU first',
        'cons': 'Indefinite starvation for low-priority processes',
        'fairness': '⭐',
    },
    'random': {
        'name': 'Random Selection', 'type': 'Preemptive',
        'desc': 'At each tick, a random process is selected for execution. Fully non-deterministic scheduling.',
        'pros': 'Simple, no complex data structures needed',
        'cons': 'Unpredictable, no fairness guarantees',
        'fairness': '⭐⭐⭐',
    },
}


# ============================================================================
# SCHEDULING ALGORITHMS (unchanged logic from v2.0)
# ============================================================================

def apply_fifo_scheduling(processes):
    """
    FIFO (First In, First Out) Scheduling.
    Processes complete in the order they were created.
    Uses spawn time to determine execution order.
    """
    if processes:
        processes[0]['Time Left (s)'] -= 1
        if processes[0]['Time Left (s)'] <= 0:
            return [p for p in processes if p['Time Left (s)'] > 0]
    return processes


def apply_round_robin_scheduling(processes, time_quantum=10):
    """
    Round-Robin Scheduling with fixed time quantum.
    Each process gets time_quantum seconds before switching.
    """
    if not processes:
        return processes

    current = processes.pop(0)
    current['time_used'] = current.get('time_used', 0) + 1

    if current['time_used'] < time_quantum and current['Time Left (s)'] > 0:
        processes.insert(0, current)
    elif current['Time Left (s)'] > 0:
        current['time_used'] = 0
        processes.append(current)

    if processes and 'time_used' in processes[0]:
        processes[0]['Time Left (s)'] -= 1
        if processes[0]['Time Left (s)'] <= 0:
            processes.pop(0)

    return processes


def apply_sjf_scheduling(processes):
    """
    Shortest Job First (SJF) Scheduling.
    Process with shortest remaining time executes first.
    """
    if not processes:
        return processes

    processes.sort(key=lambda p: p['Time Left (s)'])
    processes[0]['Time Left (s)'] -= 1
    return [p for p in processes if p['Time Left (s)'] > 0]


def apply_priority_scheduling(processes):
    """
    Priority-Based Scheduling.
    Priority inversely proportional to CPU requirement (lower CPU = higher priority).
    """
    if not processes:
        return processes

    processes.sort(key=lambda p: p['CPU (%)'])

    for process in processes:
        if process['Time Left (s)'] > 0:
            process['Time Left (s)'] -= 1
            break

    return [p for p in processes if p['Time Left (s)'] > 0]


def apply_random_scheduling(processes):
    """
    Random Scheduling Algorithm.
    At each time unit, a random process is selected and executed.
    """
    if not processes:
        return processes

    random_index = random.randint(0, len(processes) - 1)
    processes[random_index]['Time Left (s)'] -= 1
    return [p for p in processes if p['Time Left (s)'] > 0]


def apply_srtn_scheduling(processes):
    """
    Shortest Remaining Time Next (SRTN) Scheduling.
    Preemptive version: every tick, re-sort by remaining time and
    execute only the process with the least time left.
    """
    if not processes:
        return processes

    processes.sort(key=lambda p: p['Time Left (s)'])
    processes[0]['Time Left (s)'] -= 1
    return [p for p in processes if p['Time Left (s)'] > 0]


# ============================================================================
# APP LAYOUT
# ============================================================================

# Common inline styles
_label_style = {
    'color': COLORS['text_dim'], 'fontSize': '11px',
    'textTransform': 'uppercase', 'letterSpacing': '1px',
    'marginBottom': '6px', 'display': 'block',
}
_input_style = {
    'width': '100%', 'padding': '10px 12px', 'marginBottom': '14px',
    'backgroundColor': 'rgba(15,15,25,0.8)', 'color': '#fff',
    'border': '1px solid rgba(255,255,255,0.1)', 'borderRadius': '8px',
    'fontFamily': "'JetBrains Mono', monospace", 'fontSize': '13px',
    'outline': 'none',
}

app.layout = html.Div(
    style={
        'backgroundColor': COLORS['bg'], 'color': COLORS['text'],
        'padding': '24px 28px', 'minHeight': '100vh',
        'fontFamily': "'JetBrains Mono', monospace",
    },
    children=[
        # ====== TITLE ======
        html.H1('OS Resource Dashboard v3.0', style={
            'textAlign': 'center', 'color': COLORS['cyan'], 'fontSize': '28px',
            'fontFamily': "'JetBrains Mono', monospace", 'fontWeight': '700',
            'animation': 'neonPulse 3s ease-in-out infinite',
            'marginBottom': '4px', 'letterSpacing': '2px',
        }),
        html.P('Real-time Process Scheduling & Resource Monitor', style={
            'textAlign': 'center', 'color': COLORS['text_muted'], 'fontSize': '11px',
            'marginBottom': '20px', 'letterSpacing': '3px', 'textTransform': 'uppercase',
        }),

        # ====== STATS RIBBON ======
        html.Div(id='stats-container', style={
            'display': 'flex', 'gap': '12px', 'marginBottom': '20px',
        }),

        # ====== THREE-COLUMN SECTION ======
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'},
            children=[
                # ---------- COLUMN 1: System Load ----------
                html.Div(className='glass-card', style={'flex': '1'}, children=[
                    html.H3('⚡ System Load', className='section-title',
                             style={'color': COLORS['red']}),
                    dcc.Graph(id='cpu-gauge', style={'height': '200px'},
                              config={'displayModeBar': False}),
                    dcc.Graph(id='mem-bar', style={'height': '100px'},
                              config={'displayModeBar': False}),
                    dcc.Graph(id='disk-bar', style={'height': '100px'},
                              config={'displayModeBar': False}),
                ]),

                # ---------- COLUMN 2: Process Injector ----------
                html.Div(className='glass-card', style={'flex': '1'}, children=[
                    html.H3('🚀 Process Injector', className='section-title',
                             style={'color': COLORS['cyan']}),

                    # Preset quick-spawn buttons
                    html.Div(
                        style={'display': 'flex', 'gap': '8px', 'marginBottom': '16px',
                               'flexWrap': 'wrap'},
                        children=[
                            html.Button(
                                f"{p['icon']} {p['label']}",
                                id={'type': 'preset-btn', 'index': key},
                                n_clicks=0, className='preset-btn',
                            )
                            for key, p in PROCESS_PRESETS.items()
                        ],
                    ),

                    # Scheduling algorithm dropdown
                    html.Label('Scheduling Algorithm', style=_label_style),
                    dcc.Dropdown(
                        id='scheduler-algo',
                        options=[
                            {'label': 'FIFO (First In, First Out)', 'value': 'fifo'},
                            {'label': 'Round-Robin (TQ: 10s)', 'value': 'round_robin'},
                            {'label': 'Shortest Job First (SJF)', 'value': 'sjf'},
                            {'label': 'SRTN (Shortest Remaining Time)', 'value': 'srtn'},
                            {'label': 'Priority-Based', 'value': 'priority'},
                            {'label': 'Random Selection', 'value': 'random'},
                        ],
                        value='random',
                        style={'marginBottom': '4px'},
                    ),

                    # Algorithm info card (populated by callback)
                    html.Div(id='algo-info', className='algo-info-box'),

                    # Process name input
                    html.Label('Process Name', style=_label_style),
                    dcc.Input(id='proc-name', type='text',
                              placeholder='e.g., MyProcess', style=_input_style),

                    # Resource sliders
                    html.Label('CPU (%)', style={**_label_style, 'color': COLORS['cyan'],
                                                  'fontWeight': '600'}),
                    dcc.Slider(id='cpu-req', min=1, max=100, step=1, value=15,
                               marks=None, tooltip={'always_visible': True}),

                    html.Label('RAM (MB)', style={**_label_style, 'color': COLORS['yellow'],
                                                   'fontWeight': '600', 'marginTop': '10px'}),
                    dcc.Slider(id='mem-req', min=16, max=2048, step=16, value=256,
                               marks=None, tooltip={'always_visible': True}),

                    html.Label('Disk I/O (MB/s)', style={**_label_style, 'color': COLORS['red'],
                                                          'fontWeight': '600', 'marginTop': '10px'}),
                    dcc.Slider(id='disk-req', min=0, max=500, step=10, value=50,
                               marks=None, tooltip={'always_visible': True}),

                    # Spawn button
                    html.Button('⚡ Spawn Process', id='spawn-btn', n_clicks=0,
                                className='spawn-btn', style={'marginTop': '16px'}),
                ]),

                # ---------- COLUMN 3: Kernel Logs ----------
                html.Div(className='glass-card-terminal', style={'flex': '1'}, children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'space-between',
                               'alignItems': 'center', 'marginBottom': '12px'},
                        children=[
                            html.H3('📟 Kernel Logs', className='section-title',
                                     style={'color': COLORS['cyan'], 'margin': '0'}),
                            html.Button('Clear', id='clear-log-btn', n_clicks=0,
                                        className='clear-btn'),
                        ],
                    ),
                    html.Div(id='kernel-log-container', className='kernel-log-scroll'),
                ]),
            ],
        ),

        # ====== RESOURCE HISTORY CHART ======
        html.Div(className='glass-card', style={'marginBottom': '20px'}, children=[
            html.H3('📈 Resource History (60s Window)', className='section-title',
                     style={'color': COLORS['blue']}),
            dcc.Graph(id='history-chart', style={'height': '200px'},
                      config={'displayModeBar': False}),
        ]),

        # ====== PROCESS CONTROL SECTION ======
        html.Div(className='glass-card-warm', children=[
            # Header row with title + controls
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between',
                       'alignItems': 'center', 'marginBottom': '16px',
                       'flexWrap': 'wrap', 'gap': '12px'},
                children=[
                    html.H3('🖥️ Active Process Control Block (PCB)',
                             className='section-title',
                             style={'color': COLORS['yellow'], 'margin': '0'}),
                    html.Div(
                        style={'display': 'flex', 'gap': '14px', 'alignItems': 'center'},
                        children=[
                            html.Button('⏸ Pause', id='pause-btn', n_clicks=0,
                                        className='control-btn'),
                            html.Div(
                                style={'display': 'flex', 'alignItems': 'center',
                                       'gap': '8px'},
                                children=[
                                    html.Span('Speed:', style={
                                        'color': '#666', 'fontSize': '11px', 'whiteSpace': 'nowrap'}),
                                    html.Div(style={'width': '180px'}, children=[
                                        dcc.Slider(
                                            id='speed-slider', min=0.5, max=4,
                                            step=None, value=1, included=False,
                                            marks={0.5: '0.5×', 1: '1×', 2: '2×', 4: '4×'},
                                        ),
                                    ]),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Scheduling Gantt Timeline
            html.Div(style={'marginBottom': '16px'}, children=[
                html.Div('Scheduling Timeline (Last 30 Ticks)', style={
                    'color': '#666', 'fontSize': '11px', 'marginBottom': '6px',
                    'textTransform': 'uppercase', 'letterSpacing': '1px',
                }),
                dcc.Graph(id='gantt-chart', style={'height': '100px'},
                          config={'displayModeBar': False}),
            ]),

            # Process Table
            dash_table.DataTable(
                id='process-table',
                columns=[
                    {"name": "PID",          "id": "PID"},
                    {"name": "Name",         "id": "Name"},
                    {"name": "State",        "id": "State"},
                    {"name": "CPU (%)",      "id": "CPU (%)"},
                    {"name": "RAM (MB)",     "id": "RAM (MB)"},
                    {"name": "Disk I/O",     "id": "Disk I/O"},
                    {"name": "Time Left",    "id": "Time Left (s)"},
                    {"name": "Priority",     "id": "Priority"},
                ],
                data=[],
                row_selectable='multi',
                style_header={
                    'backgroundColor': 'rgba(255,204,0,0.08)',
                    'color': COLORS['yellow'], 'fontWeight': '600', 'fontSize': '12px',
                    'border': 'none', 'borderBottom': '2px solid rgba(255,204,0,0.25)',
                    'fontFamily': "'JetBrains Mono', monospace",
                    'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                },
                style_data={
                    'backgroundColor': 'rgba(15,15,25,0.6)',
                    'color': '#d0d0d0', 'fontSize': '12px',
                    'fontFamily': "'JetBrains Mono', monospace",
                    'border': 'none', 'borderBottom': '1px solid rgba(255,255,255,0.04)',
                },
                style_cell={
                    'textAlign': 'center', 'padding': '10px 12px', 'minWidth': '80px',
                },
                style_data_conditional=[
                    # Selected row highlight
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': 'rgba(255,0,85,0.2)',
                        'border': '1px solid rgba(255,0,85,0.4)', 'color': '#fff',
                    },
                    # RUNNING state — cyan glow
                    {
                        'if': {'filter_query': '{State} = "RUNNING"'},
                        'backgroundColor': 'rgba(0,255,204,0.08)',
                        'borderLeft': '3px solid #00ffcc',
                    },
                    # Time Left < 5 — critical (red)
                    {
                        'if': {'filter_query': '{Time Left (s)} < 5',
                               'column_id': 'Time Left (s)'},
                        'color': '#ff0055', 'fontWeight': '700',
                    },
                    # Time Left 5-10 — warning (yellow)
                    {
                        'if': {'filter_query': '{Time Left (s)} >= 5 && {Time Left (s)} < 10',
                               'column_id': 'Time Left (s)'},
                        'color': '#ffcc00',
                    },
                ],
            ),

            # Kill buttons row
            html.Div(
                style={'display': 'flex', 'gap': '12px', 'marginTop': '14px'},
                children=[
                    html.Button('☠️ SIGKILL (Force Stop)', id='kill-btn',
                                n_clicks=0, className='kill-btn'),
                    html.Button('💀 Kill All Processes', id='kill-all-btn',
                                n_clicks=0, className='kill-all-btn'),
                ],
            ),
        ]),

        # ====== HIDDEN STATE STORES ======
        dcc.Store(id='state-store', data=[]),
        dcc.Store(id='log-store', data=[
            {'level': 'system', 'time': '00:00:00',
             'msg': '[SYS] Kernel v3.0 Initialized — Awaiting processes...'}
        ]),
        dcc.Store(id='stats-store', data={
            'spawned': 0, 'completed': 0, 'killed': 0, 'uptime': 0, 'active': 0,
        }),
        dcc.Store(id='gantt-store', data=[]),
        dcc.Store(id='history-store', data={'cpu': [], 'mem': [], 'disk': []}),
        dcc.Interval(id='clock-tick', interval=1000, n_intervals=0),
    ],
)


# ============================================================================
# CALLBACKS
# ============================================================================

# ---------- 1. Preset Buttons → Fill Form ----------
@app.callback(
    Output('proc-name', 'value'),
    Output('cpu-req', 'value'),
    Output('mem-req', 'value'),
    Output('disk-req', 'value'),
    Input({'type': 'preset-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def fill_preset(n_clicks_list):
    """Auto-fill the process injector form when a preset button is clicked."""
    if not any(n for n in n_clicks_list if n):
        raise dash.exceptions.PreventUpdate
    triggered = ctx.triggered_id
    if triggered and isinstance(triggered, dict):
        preset = PROCESS_PRESETS.get(triggered['index'])
        if preset:
            return preset['name'], preset['cpu'], preset['mem'], preset['disk']
    raise dash.exceptions.PreventUpdate


# ---------- 2. Algorithm Info Card ----------
@app.callback(
    Output('algo-info', 'children'),
    Input('scheduler-algo', 'value'),
)
def update_algo_info(algo):
    """Display a description card for the selected scheduling algorithm."""
    info = ALGO_INFO.get(algo, {})
    if not info:
        return []
    badge_bg = 'rgba(255,204,0,0.12)' if info['type'] == 'Preemptive' else 'rgba(0,204,255,0.12)'
    badge_color = '#ffcc00' if info['type'] == 'Preemptive' else '#00ccff'
    return [
        html.Div(f"📋 {info['name']}", style={
            'fontWeight': '600', 'marginBottom': '6px', 'color': '#00ffcc', 'fontSize': '12px'}),
        html.Span(info['type'], style={
            'display': 'inline-block', 'padding': '2px 8px', 'borderRadius': '4px',
            'fontSize': '10px', 'fontWeight': '600',
            'backgroundColor': badge_bg, 'color': badge_color, 'marginBottom': '8px'}),
        html.P(info['desc'], style={'color': '#aaa', 'marginTop': '8px', 'marginBottom': '6px'}),
        html.Div(f"✅ {info['pros']}", style={'color': '#00ffcc', 'marginBottom': '3px'}),
        html.Div(f"⚠️ {info['cons']}", style={'color': '#ff6644', 'marginBottom': '3px'}),
        html.Div(f"Fairness: {info['fairness']}", style={'color': '#888'}),
    ]


# ---------- 3. Pause / Resume ----------
@app.callback(
    Output('clock-tick', 'disabled'),
    Output('pause-btn', 'children'),
    Input('pause-btn', 'n_clicks'),
    State('clock-tick', 'disabled'),
    prevent_initial_call=True,
)
def toggle_pause(n_clicks, is_disabled):
    """Toggle the scheduler clock on/off."""
    paused = not is_disabled
    return paused, ('▶ Resume' if paused else '⏸ Pause')


# ---------- 4. Speed Control ----------
@app.callback(
    Output('clock-tick', 'interval'),
    Input('speed-slider', 'value'),
)
def change_speed(speed):
    """Adjust the tick interval based on the speed slider."""
    if not speed or speed <= 0:
        return 1000
    return int(1000 / speed)


# ---------- 5. Main Kernel Loop ----------
@app.callback(
    Output('state-store', 'data'),
    Output('log-store', 'data'),
    Output('process-table', 'selected_rows'),
    Output('stats-store', 'data'),
    Output('gantt-store', 'data'),
    Output('history-store', 'data'),
    Input('clock-tick', 'n_intervals'),
    Input('spawn-btn', 'n_clicks'),
    Input('kill-btn', 'n_clicks'),
    Input('kill-all-btn', 'n_clicks'),
    Input('clear-log-btn', 'n_clicks'),
    State('proc-name', 'value'),
    State('cpu-req', 'value'),
    State('mem-req', 'value'),
    State('disk-req', 'value'),
    State('scheduler-algo', 'value'),
    State('process-table', 'selected_rows'),
    State('state-store', 'data'),
    State('log-store', 'data'),
    State('stats-store', 'data'),
    State('gantt-store', 'data'),
    State('history-store', 'data'),
    prevent_initial_call=True,
)
def os_kernel_loop(n_tick, spawn_n, kill_n, kill_all_n, clear_n,
                   proc_name, cpu_req, mem_req, disk_req, scheduler_algo,
                   selected_rows, process_data, log_data, stats_data,
                   gantt_data, history_data):
    """
    Main kernel loop — handles process lifecycle, spawning, termination,
    scheduling, deadlock detection, and all state updates.
    """
    triggered = ctx.triggered_id
    timestamp = datetime.now().strftime("%H:%M:%S")

    # ---- Initialize mutable copies of all state ----
    processes = [dict(p) for p in (process_data or [])]
    log_entries = list(log_data) if log_data else []
    stats = dict(stats_data) if stats_data else {
        'spawned': 0, 'completed': 0, 'killed': 0, 'uptime': 0, 'active': 0}
    gantt = list(gantt_data) if gantt_data else []
    history = {}
    _hd = history_data or {}
    for k in ('cpu', 'mem', 'disk'):
        history[k] = list(_hd.get(k, []))

    selected = selected_rows or []
    scheduler_algo = scheduler_algo or 'random'
    executing_pid = None

    # Current resource totals (pre-action)
    total_cpu = sum(p.get('CPU (%)', 0) for p in processes)
    total_mem = sum(p.get('RAM (MB)', 0) for p in processes)
    total_disk = sum(p.get('Disk I/O', 0) for p in processes)

    # ================================================================
    # HANDLE TRIGGERS
    # ================================================================

    if triggered == 'clear-log-btn':
        # ----- Clear Logs -----
        log_entries = [{'level': 'system', 'time': timestamp,
                        'msg': '[SYS] Logs cleared by Admin.'}]

    elif triggered == 'kill-all-btn' and processes:
        # ----- Kill All -----
        for p in processes:
            log_entries.insert(0, {'level': 'kill', 'time': timestamp,
                'msg': f"[KILL] PID {p['PID']} ({p['Name']}) terminated (Kill All)."})
            stats['killed'] += 1
        processes = []
        selected = []

    elif triggered == 'clock-tick':
        # ----- Scheduler Tick -----
        stats['uptime'] = n_tick

        # Capture pre-scheduling state for comparison
        old_times = {p['PID']: p['Time Left (s)'] for p in processes}
        old_pids = set(old_times.keys())

        is_deadlock = (total_cpu > 100
                       or total_mem > RESOURCE_LIMITS['memory_max_system']
                       or total_disk > RESOURCE_LIMITS['disk_max_system'])

        if is_deadlock and processes:
            log_entries.insert(0, {'level': 'deadlock', 'time': timestamp,
                'msg': (f"💀 [DEADLOCK] Over-allocated! CPU:{total_cpu}% "
                        f"RAM:{total_mem}MB Disk:{total_disk}MB/s "
                        f"— Kill a process to recover.")})
        elif processes:
            # Apply selected scheduling algorithm
            if scheduler_algo == 'fifo':
                processes = apply_fifo_scheduling(processes)
            elif scheduler_algo == 'round_robin':
                processes = apply_round_robin_scheduling(processes, time_quantum=10)
            elif scheduler_algo == 'sjf':
                processes = apply_sjf_scheduling(processes)
            elif scheduler_algo == 'srtn':
                processes = apply_srtn_scheduling(processes)
            elif scheduler_algo == 'priority':
                processes = apply_priority_scheduling(processes)
            else:
                processes = apply_random_scheduling(processes)

            # Identify which process was executed (time decremented)
            new_pids = {p['PID'] for p in processes}
            for p in processes:
                if p['PID'] in old_times and p['Time Left (s)'] == old_times[p['PID']] - 1:
                    executing_pid = p['PID']
                    break
            if not executing_pid:
                # Check completed processes (removed from list)
                for pid in (old_pids - new_pids):
                    if old_times[pid] == 1:
                        executing_pid = pid
                        break

            # Log completed processes
            completed_pids = old_pids - {p['PID'] for p in processes}
            for pid in completed_pids:
                old_proc = next((p for p in (process_data or []) if p['PID'] == pid), None)
                if old_proc:
                    log_entries.insert(0, {'level': 'exit', 'time': timestamp,
                        'msg': f"[EXIT] PID {pid} ({old_proc['Name']}) completed."})
                    stats['completed'] += 1

        # Annotate State and Priority based on scheduling results
        for i, p in enumerate(processes):
            p['Priority'] = i + 1
            p['State'] = 'RUNNING' if p.get('PID') == executing_pid else 'READY'

        # Update Gantt timeline
        if executing_pid:
            exec_name = ''
            for p in list(process_data or []) + processes:
                if p.get('PID') == executing_pid:
                    exec_name = p.get('Name', '')
                    break
            gantt.append({'tick': n_tick, 'pid': executing_pid, 'name': exec_name})
        elif processes:
            gantt.append({'tick': n_tick, 'pid': 0, 'name': 'IDLE'})
        gantt = gantt[-30:]

        # Update resource history (post-scheduling values)
        post_cpu = sum(p.get('CPU (%)', 0) for p in processes)
        post_mem = sum(p.get('RAM (MB)', 0) for p in processes)
        post_disk = sum(p.get('Disk I/O', 0) for p in processes)
        mem_pct = (post_mem / RESOURCE_LIMITS['memory_max_system']) * 100
        disk_pct = (post_disk / RESOURCE_LIMITS['disk_max_system']) * 100
        history['cpu'].append(round(post_cpu, 1))
        history['mem'].append(round(mem_pct, 1))
        history['disk'].append(round(disk_pct, 1))
        for k in ('cpu', 'mem', 'disk'):
            history[k] = history[k][-60:]

        # Periodic scheduler info log
        if n_tick > 0 and n_tick % 10 == 0:
            algo_names = {
                'fifo': 'FIFO', 'round_robin': 'Round-Robin (TQ=10s)',
                'sjf': 'SJF', 'srtn': 'SRTN',
                'priority': 'Priority-Based', 'random': 'Random',
            }
            log_entries.insert(0, {'level': 'scheduler', 'time': timestamp,
                'msg': (f"[SCHEDULER] Algorithm: {algo_names.get(scheduler_algo, '?')} "
                        f"| Active: {len(processes)} processes")})

    elif triggered == 'spawn-btn':
        # ----- Spawn Process -----
        if not proc_name or not proc_name.strip():
            log_entries.insert(0, {'level': 'warn', 'time': timestamp,
                'msg': "[WARN] Cannot spawn: No process name specified."})
        elif ((total_cpu + cpu_req <= 100)
              and (total_mem + mem_req <= RESOURCE_LIMITS['memory_max_system'])
              and (total_disk + disk_req <= RESOURCE_LIMITS['disk_max_system'])):
            new_pid = random.randint(RESOURCE_LIMITS['pid_min'], RESOURCE_LIMITS['pid_max'])
            lifetime = random.randint(
                RESOURCE_LIMITS['process_lifetime_min'],
                RESOURCE_LIMITS['process_lifetime_max'])
            processes.append({
                'PID': new_pid, 'Name': proc_name.strip(),
                'CPU (%)': cpu_req, 'RAM (MB)': mem_req, 'Disk I/O': disk_req,
                'Time Left (s)': lifetime,
                'State': 'READY', 'Priority': len(processes) + 1,
            })
            log_entries.insert(0, {'level': 'approved', 'time': timestamp,
                'msg': (f"[APPROVED] PID {new_pid} ({proc_name.strip()}) spawned "
                        f"— Lifetime: {lifetime}s")})
            stats['spawned'] += 1
        else:
            log_entries.insert(0, {'level': 'denied', 'time': timestamp,
                'msg': (f"[DENIED] '{proc_name}' rejected! Would exceed limits "
                        f"(CPU:{total_cpu + cpu_req}% RAM:{total_mem + mem_req}MB "
                        f"Disk:{total_disk + disk_req}MB/s)")})

    elif triggered == 'kill-btn' and selected_rows:
        # ----- Kill Selected Processes -----
        for idx in sorted(selected_rows, reverse=True):
            if idx < len(processes):
                killed = processes.pop(idx)
                log_entries.insert(0, {'level': 'kill', 'time': timestamp,
                    'msg': f"[KILL] PID {killed['PID']} ({killed['Name']}) terminated by Admin."})
                stats['killed'] += 1
        selected = []
        # Re-annotate priority after removal
        for i, p in enumerate(processes):
            p['Priority'] = i + 1

    # ---- Finalize ----
    stats['active'] = len(processes)
    log_entries = log_entries[:RESOURCE_LIMITS['max_log_entries']]

    return processes, log_entries, selected, stats, gantt, history


# ---------- 6. Render System Metrics (Charts + Table) ----------
@app.callback(
    Output('process-table', 'data'),
    Output('cpu-gauge', 'figure'),
    Output('mem-bar', 'figure'),
    Output('disk-bar', 'figure'),
    Input('state-store', 'data'),
)
def render_system_metrics(process_data):
    """
    Update CPU gauge, memory bar, disk bar, and process table
    based on current process list.
    """
    processes = process_data or []
    cpu_total = sum(p.get('CPU (%)', 0) for p in processes)
    mem_total = sum(p.get('RAM (MB)', 0) for p in processes)
    disk_total = sum(p.get('Disk I/O', 0) for p in processes)

    font_family = "'JetBrains Mono', monospace"

    # ====== CPU GAUGE ======
    cpu_color = '#00ffcc' if cpu_total < 70 else ('#ffcc00' if cpu_total < 85 else '#ff0055')
    cpu_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cpu_total,
        title={'text': "CPU Usage", 'font': {'color': '#888', 'size': 13, 'family': font_family}},
        number={'suffix': '%', 'font': {'color': cpu_color, 'size': 28, 'family': font_family}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#333', 'dtick': 25,
                     'tickfont': {'color': '#555', 'size': 10}},
            'bar': {'color': cpu_color, 'thickness': 0.7},
            'bgcolor': 'rgba(30,30,40,0.5)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 70], 'color': 'rgba(0,255,204,0.04)'},
                {'range': [70, 85], 'color': 'rgba(255,204,0,0.04)'},
                {'range': [85, 100], 'color': 'rgba(255,0,85,0.06)'},
            ],
            'threshold': {
                'line': {'color': '#ff0055', 'width': 2},
                'thickness': 0.8, 'value': 85,
            },
        },
    ))
    cpu_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#888', 'family': font_family},
        height=180,
    )

    # ====== MEMORY BAR (progress-bar style) ======
    mem_max = RESOURCE_LIMITS['memory_max_system']
    mem_pct = (mem_total / mem_max) * 100 if mem_max else 0
    mem_color = '#ffcc00' if mem_pct < 75 else ('#ff8800' if mem_pct < 90 else '#ff0055')

    mem_fig = go.Figure()
    mem_fig.add_trace(go.Bar(
        x=[mem_max], y=['RAM'], orientation='h',
        marker_color='rgba(255,204,0,0.06)', showlegend=False, width=0.5))
    mem_fig.add_trace(go.Bar(
        x=[mem_total], y=['RAM'], orientation='h',
        marker_color=mem_color, showlegend=False, width=0.5,
        text=[f' {mem_total} / {mem_max} MB ({mem_pct:.0f}%) '],
        textposition='inside', insidetextanchor='middle',
        textfont={'color': '#fff', 'size': 11, 'family': font_family}))
    mem_fig.update_layout(
        barmode='overlay',
        xaxis=dict(range=[0, mem_max], visible=False),
        yaxis=dict(tickfont={'color': '#ffcc00', 'size': 12, 'family': font_family}),
        margin=dict(l=50, r=15, t=8, b=8),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=55,
    )

    # ====== DISK I/O BAR (progress-bar style) ======
    disk_max = RESOURCE_LIMITS['disk_max_system']
    disk_pct = (disk_total / disk_max) * 100 if disk_max else 0
    disk_color = '#ff4477' if disk_pct < 75 else '#ff0055'

    disk_fig = go.Figure()
    disk_fig.add_trace(go.Bar(
        x=[disk_max], y=['Disk'], orientation='h',
        marker_color='rgba(255,0,85,0.06)', showlegend=False, width=0.5))
    disk_fig.add_trace(go.Bar(
        x=[disk_total], y=['Disk'], orientation='h',
        marker_color=disk_color, showlegend=False, width=0.5,
        text=[f' {disk_total} / {disk_max} MB/s ({disk_pct:.0f}%) '],
        textposition='inside', insidetextanchor='middle',
        textfont={'color': '#fff', 'size': 11, 'family': font_family}))
    disk_fig.update_layout(
        barmode='overlay',
        xaxis=dict(range=[0, disk_max], visible=False),
        yaxis=dict(tickfont={'color': '#ff4477', 'size': 12, 'family': font_family}),
        margin=dict(l=50, r=15, t=8, b=8),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=55,
    )

    # ====== PROCESS TABLE DATA ======
    display_fields = ['PID', 'Name', 'State', 'CPU (%)', 'RAM (MB)',
                      'Disk I/O', 'Time Left (s)', 'Priority']
    table_data = [{k: p.get(k, '') for k in display_fields} for p in processes]

    return table_data, cpu_fig, mem_fig, disk_fig


# ---------- 7. Resource History Chart ----------
@app.callback(
    Output('history-chart', 'figure'),
    Input('history-store', 'data'),
)
def render_history_chart(history_data):
    """Render a 60-second sliding window line chart of CPU, RAM, and Disk usage %."""
    font_family = "'JetBrains Mono', monospace"
    fig = go.Figure()

    if not history_data or not history_data.get('cpu'):
        fig.add_annotation(
            text="📊 Collecting data...", x=0.5, y=0.5,
            xref='paper', yref='paper', showarrow=False,
            font={'color': '#444', 'size': 14, 'family': font_family})
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=180, margin=dict(l=0, r=0, t=0, b=0))
        return fig

    cpu = history_data['cpu']
    mem = history_data['mem']
    disk = history_data['disk']
    x = list(range(len(cpu)))

    fig.add_trace(go.Scatter(
        x=x, y=cpu, mode='lines', name='CPU %',
        line={'color': '#00ffcc', 'width': 2, 'shape': 'spline'},
        fill='tozeroy', fillcolor='rgba(0,255,204,0.06)'))
    fig.add_trace(go.Scatter(
        x=x, y=mem, mode='lines', name='RAM %',
        line={'color': '#ffcc00', 'width': 2, 'shape': 'spline'},
        fill='tozeroy', fillcolor='rgba(255,204,0,0.06)'))
    fig.add_trace(go.Scatter(
        x=x, y=disk, mode='lines', name='Disk %',
        line={'color': '#ff0055', 'width': 2, 'shape': 'spline'},
        fill='tozeroy', fillcolor='rgba(255,0,85,0.06)'))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#555', 'family': font_family, 'size': 10},
        height=180,
        margin=dict(l=40, r=20, t=10, b=30),
        xaxis=dict(title='Seconds Elapsed', gridcolor='rgba(255,255,255,0.03)',
                   range=[0, 60], dtick=10),
        yaxis=dict(title='Usage %', range=[0, 105],
                   gridcolor='rgba(255,255,255,0.03)', dtick=25),
        legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center',
                    font={'size': 10}),
        hovermode='x unified',
    )
    return fig


# ---------- 8. Gantt Chart ----------
@app.callback(
    Output('gantt-chart', 'figure'),
    Input('gantt-store', 'data'),
)
def render_gantt_chart(gantt_data):
    """Render a scheduling timeline showing which PID executed at each tick."""
    font_family = "'JetBrains Mono', monospace"
    fig = go.Figure()

    if not gantt_data:
        fig.add_annotation(
            text="⏳ Awaiting scheduler activity...", x=0.5, y=0.5,
            xref='paper', yref='paper', showarrow=False,
            font={'color': '#444', 'size': 12, 'family': font_family})
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=80, margin=dict(l=0, r=0, t=0, b=0))
        return fig

    # Color palette for PIDs
    palette = ['#00ffcc', '#ff0055', '#ffcc00', '#00ccff', '#aa66ff',
               '#ff8844', '#44ff88', '#ff44aa', '#88ccff', '#ffaa00']
    pid_color = {}
    color_idx = 0

    # Collect unique PIDs in appearance order
    seen_pids = []
    for entry in gantt_data:
        if entry['pid'] not in seen_pids:
            seen_pids.append(entry['pid'])

    for pid in seen_pids:
        if pid == 0:
            pid_color[pid] = 'rgba(50,50,50,0.5)'
        else:
            pid_color[pid] = palette[color_idx % len(palette)]
            color_idx += 1

    # One trace per PID for legend grouping
    for pid in seen_pids:
        entries = [e for e in gantt_data if e['pid'] == pid]
        ticks = [e['tick'] for e in entries]
        name = entries[0].get('name', str(pid))
        label = 'IDLE' if pid == 0 else f"PID {pid} ({name})"
        fig.add_trace(go.Bar(
            x=ticks, y=[1] * len(ticks), name=label,
            marker_color=pid_color[pid], width=0.9,
            hovertemplate=f"{label}<br>Tick: %{{x}}<extra></extra>"))

    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#555', 'family': font_family, 'size': 10},
        height=80,
        margin=dict(l=10, r=10, t=5, b=20),
        xaxis=dict(title='Tick', gridcolor='rgba(255,255,255,0.03)', dtick=5),
        yaxis=dict(visible=False),
        legend=dict(orientation='h', y=1.35, x=0.5, xanchor='center',
                    font={'size': 9}),
        showlegend=True,
    )
    return fig


# ---------- 9. Kernel Log Rendering ----------
@app.callback(
    Output('kernel-log-container', 'children'),
    Input('log-store', 'data'),
)
def render_kernel_logs(log_data):
    """Convert structured log entries into color-coded HTML divs."""
    if not log_data:
        return [html.Div('[SYS] Kernel Initialized...',
                         className='log-entry log-system')]

    children = []
    for entry in log_data:
        level = entry.get('level', 'system')
        time_str = entry.get('time', '')
        msg = entry.get('msg', '')
        text = f"[{time_str}] {msg}" if time_str else msg
        children.append(html.Div(text, className=f"log-entry log-{level}"))
    return children


# ---------- 10. Stats Ribbon Rendering ----------
@app.callback(
    Output('stats-container', 'children'),
    Input('stats-store', 'data'),
)
def render_stats(stats_data):
    """Render the statistics ribbon with glowing stat cards."""
    if not stats_data:
        stats_data = {'spawned': 0, 'completed': 0, 'killed': 0,
                      'uptime': 0, 'active': 0}

    uptime = stats_data.get('uptime', 0)
    mins, secs = divmod(uptime, 60)

    items = [
        ('⏱', 'UPTIME',    f"{mins:02d}:{secs:02d}", '#00ccff'),
        ('🚀', 'SPAWNED',   str(stats_data.get('spawned', 0)),   '#00ffcc'),
        ('✅', 'COMPLETED', str(stats_data.get('completed', 0)), '#44ff88'),
        ('☠️', 'KILLED',    str(stats_data.get('killed', 0)),    '#ff0055'),
        ('📊', 'ACTIVE',    str(stats_data.get('active', 0)),    '#ffcc00'),
    ]

    return [
        html.Div(className='stat-card', children=[
            html.Div(icon, style={'fontSize': '18px', 'marginBottom': '4px'}),
            html.Div(label, style={
                'color': '#444', 'fontSize': '10px',
                'letterSpacing': '1.5px', 'marginBottom': '4px'}),
            html.Div(value, style={
                'color': color, 'fontSize': '22px', 'fontWeight': '700',
                'fontFamily': "'JetBrains Mono', monospace"}),
        ])
        for icon, label, value, color in items
    ]


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Launch the Dash server with debug mode enabled.

    The dashboard will be accessible at http://localhost:8050/

    Debug mode enables:
    - Hot reloading on code changes
    - Enhanced error messages
    - Interactive debugger (Dash DevTools)
    """
    app.run(debug=True)