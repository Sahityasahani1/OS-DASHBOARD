"""
OS Resource Dashboard v2.0
An interactive dashboard to monitor and manage OS resource allocation and processes.

Features:
- Real-time CPU, Memory, and Disk I/O monitoring
- Process spawning simulator with configurable resource requirements
- Active process management (kill/terminate processes)
- Kernel event logging
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx
import plotly.graph_objs as go
import pandas as pd
import random
from datetime import datetime

# ============================================================================
# APPLICATION CONFIGURATION & STYLING CONSTANTS
# ============================================================================

# Initialize Dash Application
app = dash.Dash(__name__)

# Color Palette (Dark Theme)
COLORS = {
    'background': '#121212',        # Dark background
    'surface': '#1e1e1e',           # Component background
    'surface_dark': '#000',         # Dark surface (logs)
    'text_primary': '#e0e0e0',      # Main text
    'text_accent_cyan': '#00ffcc',  # Cyan accent
    'text_accent_red': '#ff0055',   # Red accent
    'text_accent_yellow': '#ffcc00',# Yellow accent
    'border': '#333',               # Border color
    'border_accent': '#00ffcc',     # Accent border
    'danger': '#ff0055',            # Danger/warning color
    'success': '#00ffcc'            # Success color
}

# Layout/Spacing Constants
SPACING = {
    'main_padding': '20px',
    'component_padding': '20px',
    'small_padding': '10px',
    'gap': '20px',
    'border_radius': '10px'
}

# Resource Limits & Defaults
RESOURCE_LIMITS = {
    'cpu_min': 1,
    'cpu_max': 100,
    'cpu_default': 15,
    'memory_min': 16,
    'memory_max': 2048,
    'memory_default': 256,
    'memory_max_system': 8192,
    'disk_min': 0,
    'disk_max': 500,
    'disk_default': 50,
    'disk_max_system': 1000,
    'process_lifetime_min': 15,
    'process_lifetime_max': 45,
    'pid_min': 1000,
    'pid_max': 9999,
    'max_log_lines': 20
}

# UI Text Labels
LABELS = {
    'title': 'OS Resource Dashboard v2.0',
    'system_load': 'System Load',
    'process_injector': 'Process Injector',
    'kernel_logs': 'Kernel Logs',
    'process_control': 'Active Process Control Block (PCB)',
    'process_name': 'Process Name',
    'cpu_label': 'CPU (%)',
    'memory_label': 'RAM (MB)',
    'disk_label': 'Disk I/O (MB/s)',
    'spawn_button': 'Spawn Process',
    'kill_button': 'SIGKILL (Force Stop)',
    'kernel_init': '[SYS] Kernel Initialized...\n'
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_styled_div(flex=1, padding=None):
    """
    Create a consistently styled container div.
    
    Args:
        flex (int): Flex value for layout
        padding (str): Custom padding, defaults to component_padding
    
    Returns:
        dict: Style dictionary for the div
    """
    return {
        'flex': str(flex),
        'backgroundColor': COLORS['surface'],
        'padding': padding or SPACING['component_padding'],
        'borderRadius': SPACING['border_radius'],
        'border': f"1px solid {COLORS['border']}"
    }

def get_styled_input(width='100%', margin_bottom='15px'):
    """Create a consistently styled input field."""
    return {
        'width': width,
        'padding': SPACING['small_padding'],
        'marginBottom': margin_bottom,
        'backgroundColor': '#222',
        'color': '#fff',
        'border': '1px solid #444'
    }

def get_styled_button(background_color, text_color='#000'):
    """Create a consistently styled button."""
    return {
        'padding': '15px',
        'marginTop': '20px',
        'backgroundColor': background_color,
        'color': text_color,
        'fontWeight': 'bold',
        'border': 'none',
        'cursor': 'pointer',
        'width': '100%'
    }

# ============================================================================
# APP LAYOUT - Main Dashboard Structure
# ============================================================================

app.layout = html.Div(
    style={
        'backgroundColor': COLORS['background'],
        'color': COLORS['text_primary'],
        'padding': SPACING['main_padding'],
        'minHeight': '100vh',
        'fontFamily': 'Consolas, monospace'
    },
    children=[
        # ====== HEADER ======
        html.H1(
            LABELS['title'],
            style={
                'textAlign': 'center',
                'color': COLORS['text_accent_cyan'],
                'textShadow': f"0 0 10px {COLORS['text_accent_cyan']}"
            }
        ),

        # ====== THREE-COLUMN SECTION: System Load | Process Injector | Kernel Logs ======
        html.Div(
            style={'display': 'flex', 'gap': SPACING['gap'], 'marginBottom': SPACING['gap']},
            children=[
                # COLUMN 1: System Load Monitoring
                html.Div(
                    style=get_styled_div(),
                    children=[
                        html.H3(
                            LABELS['system_load'],
                            style={'color': COLORS['text_accent_red']}
                        ),
                        dcc.Graph(
                            id='cpu-gauge',
                            style={'height': '200px'},
                            config={'displayModeBar': False}
                        ),
                        dcc.Graph(
                            id='mem-bar',
                            style={'height': '150px'},
                            config={'displayModeBar': False}
                        ),
                        dcc.Graph(
                            id='disk-bar',
                            style={'height': '150px'},
                            config={'displayModeBar': False}
                        )
                    ]
                ),

                # COLUMN 2: Process Injector (Controls)
                html.Div(
                    style=get_styled_div(),
                    children=[
                        html.H3(
                            LABELS['process_injector'],
                            style={'color': COLORS['text_accent_cyan']}
                        ),
                        dcc.Input(
                            id='proc-name',
                            type='text',
                            placeholder=LABELS['process_name'],
                            style=get_styled_input()
                        ),
                        html.Label(
                            LABELS['cpu_label'],
                            style={'color': COLORS['text_primary'], 'fontWeight': 'bold'}
                        ),
                        dcc.Slider(
                            id='cpu-req',
                            min=RESOURCE_LIMITS['cpu_min'],
                            max=RESOURCE_LIMITS['cpu_max'],
                            step=1,
                            value=RESOURCE_LIMITS['cpu_default'],
                            marks=None,
                            tooltip={'always_visible': True}
                        ),
                        html.Label(
                            LABELS['memory_label'],
                            style={'color': COLORS['text_primary'], 'fontWeight': 'bold', 'marginTop': '15px'}
                        ),
                        dcc.Slider(
                            id='mem-req',
                            min=RESOURCE_LIMITS['memory_min'],
                            max=RESOURCE_LIMITS['memory_max'],
                            step=16,
                            value=RESOURCE_LIMITS['memory_default'],
                            marks=None,
                            tooltip={'always_visible': True}
                        ),
                        html.Label(
                            LABELS['disk_label'],
                            style={'color': COLORS['text_primary'], 'fontWeight': 'bold', 'marginTop': '15px'}
                        ),
                        dcc.Slider(
                            id='disk-req',
                            min=RESOURCE_LIMITS['disk_min'],
                            max=RESOURCE_LIMITS['disk_max'],
                            step=10,
                            value=RESOURCE_LIMITS['disk_default'],
                            marks=None,
                            tooltip={'always_visible': True}
                        ),
                        html.Button(
                            LABELS['spawn_button'],
                            id='spawn-btn',
                            n_clicks=0,
                            style=get_styled_button(COLORS['text_accent_cyan'])
                        )
                    ]
                ),

                # COLUMN 3: Kernel Logs
                html.Div(
                    style={
                        'flex': '1',
                        'backgroundColor': COLORS['surface_dark'],
                        'padding': '15px',
                        'borderRadius': SPACING['border_radius'],
                        'border': f"1px solid {COLORS['border_accent']}"
                    },
                    children=[
                        html.H3(
                            LABELS['kernel_logs'],
                            style={'color': COLORS['text_accent_cyan'], 'marginTop': '0'}
                        ),
                        dcc.Textarea(
                            id='kernel-log',
                            value=LABELS['kernel_init'],
                            readOnly=True,
                            style={
                                'width': '100%',
                                'height': '350px',
                                'backgroundColor': COLORS['surface_dark'],
                                'color': COLORS['text_accent_cyan'],
                                'border': 'none',
                                'resize': 'none'
                            }
                        )
                    ]
                )
            ]
        ),

        # ====== PROCESS CONTROL TABLE ======
        html.Div(
            style=get_styled_div(flex=None),
            children=[
                html.H3(
                    LABELS['process_control'],
                    style={'color': COLORS['text_accent_yellow']}
                ),
                dash_table.DataTable(
                    id='process-table',
                    columns=[{"name": i, "id": i} for i in ['PID', 'Name', 'CPU (%)', 'RAM (MB)', 'Disk I/O', 'Time Left (s)']],
                    data=[],
                    row_selectable='single',
                    style_header={
                        'backgroundColor': COLORS['border'],
                        'color': COLORS['text_accent_yellow'],
                        'fontWeight': 'bold'
                    },
                    style_data={
                        'backgroundColor': '#222',
                        'color': COLORS['text_primary']
                    },
                    style_cell={
                        'textAlign': 'center',
                        'padding': SPACING['small_padding'],
                        'border': f"1px solid {COLORS['border']}"
                    },
                    style_data_conditional=[{
                        'if': {'state': 'selected'},
                        'backgroundColor': COLORS['text_accent_red'],
                        'color': '#fff'
                    }]
                ),
                html.Button(
                    LABELS['kill_button'],
                    id='kill-btn',
                    n_clicks=0,
                    style={
                        'marginTop': '15px',
                        'backgroundColor': COLORS['text_accent_red'],
                        'color': '#fff',
                        'padding': SPACING['small_padding'] + ' 20px',
                        'border': 'none',
                        'fontWeight': 'bold',
                        'cursor': 'pointer'
                    }
                )
            ]
        ),

        # ====== HIDDEN STATE MANAGEMENT ======
        dcc.Store(id='state-store', data=[]),
        dcc.Interval(id='clock-tick', interval=1000, n_intervals=0)
    ]
)


# ============================================================================
# CALLBACKS - Application Logic
# ============================================================================

@app.callback(
    Output('state-store', 'data'),
    Output('kernel-log', 'value'),
    Output('process-table', 'selected_rows'),
    Input('clock-tick', 'n_intervals'),
    Input('spawn-btn', 'n_clicks'),
    Input('kill-btn', 'n_clicks'),
    State('proc-name', 'value'),
    State('cpu-req', 'value'),
    State('mem-req', 'value'),
    State('disk-req', 'value'),
    State('process-table', 'selected_rows'),
    State('state-store', 'data'),
    State('kernel-log', 'value'),
    prevent_initial_call=True
)
def os_kernel_loop(n_tick, spawn_n, kill_n, proc_name, cpu_req, mem_req, disk_req, 
                   selected_rows, process_data, current_log):
    """
    Main kernel loop - handles process lifecycle, spawning, and termination.
    
    This callback is triggered by three events:
    1. Clock tick (every second) - decrements process timers
    2. Spawn button click - creates a new process
    3. Kill button click - terminates selected process
    
    Args:
        n_tick: Number of clock intervals (auto-increment every 1 second)
        spawn_n: Spawn button click count
        kill_n: Kill button click count
        proc_name: Name of process to create
        cpu_req: CPU requirement in %
        mem_req: Memory requirement in MB
        disk_req: Disk I/O requirement in MB/s
        selected_rows: Selected row indices from process table
        process_data: Current list of processes
        current_log: Current kernel log
    
    Returns:
        Updated process data, kernel log, and selected rows
    """
    # Determine what triggered this callback
    triggered_action = ctx.triggered_id
    
    # Initialize data structures
    processes = process_data or []
    kernel_log = current_log or ""
    selected_processes = selected_rows or []
    timestamp = datetime.now().strftime("%H:%M:%S")

    # ====== HANDLE CLOCK TICK: Decrement timers and remove finished processes ======
    if triggered_action == 'clock-tick':
        alive_processes = []
        for process in processes:
            process['Time Left (s)'] -= 1
            
            # Check if process has completed its lifecycle
            if process['Time Left (s)'] > 0:
                alive_processes.append(process)
            else:
                # Log process completion
                kernel_log = f"[{timestamp}] [EXIT] PID {process['PID']} completed naturally.\n" + kernel_log
        
        processes = alive_processes

    # ====== HANDLE SPAWN BUTTON: Create new process ======
    elif triggered_action == 'spawn-btn' and proc_name:
        new_pid = random.randint(RESOURCE_LIMITS['pid_min'], RESOURCE_LIMITS['pid_max'])
        process_lifetime = random.randint(
            RESOURCE_LIMITS['process_lifetime_min'],
            RESOURCE_LIMITS['process_lifetime_max']
        )
        
        new_process = {
            'PID': new_pid,
            'Name': proc_name,
            'CPU (%)': cpu_req,
            'RAM (MB)': mem_req,
            'Disk I/O': disk_req,
            'Time Left (s)': process_lifetime
        }
        
        processes.append(new_process)
        kernel_log = f"[{timestamp}] [FORK] PID {new_pid} ({proc_name}) spawned.\n" + kernel_log

    # ====== HANDLE KILL BUTTON: Terminate selected process ======
    elif triggered_action == 'kill-btn' and selected_rows:
        # Remove processes in reverse order to maintain correct indices
        for row_index in sorted(selected_rows, reverse=True):
            if row_index < len(processes):
                terminated_process = processes.pop(row_index)
                kernel_log = f"[{timestamp}] [KILL] PID {terminated_process['PID']} terminated by Admin.\n" + kernel_log
        
        # Clear selection after killing
        selected_processes = []

    # ====== LIMIT LOG SIZE ======
    log_lines = kernel_log.split('\n')
    if len(log_lines) > RESOURCE_LIMITS['max_log_lines']:
        kernel_log = '\n'.join(log_lines[:RESOURCE_LIMITS['max_log_lines']])

    return processes, kernel_log, selected_processes


@app.callback(
    Output('process-table', 'data'),
    Output('cpu-gauge', 'figure'),
    Output('mem-bar', 'figure'),
    Output('disk-bar', 'figure'),
    Input('state-store', 'data')
)
def render_system_metrics(process_data):
    """
    Update all system metrics and process table based on current process list.
    
    Calculates aggregate resource usage (CPU, RAM, Disk I/O) and generates
    visualizations for each metric.
    
    Args:
        process_data: List of active processes
    
    Returns:
        Tuple of (process_table_data, cpu_gauge_figure, memory_bar_figure, disk_bar_figure)
    """
    # Convert process data to DataFrame for analysis
    if process_data:
        df = pd.DataFrame(process_data)
        cpu_total = df['CPU (%)'].sum()
        memory_total = df['RAM (MB)'].sum()
        disk_total = df['Disk I/O'].sum()
    else:
        df = pd.DataFrame(columns=['CPU (%)', 'RAM (MB)', 'Disk I/O'])
        cpu_total = 0
        memory_total = 0
        disk_total = 0

    # ====== CPU GAUGE CHART ======
    cpu_figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=cpu_total,
            title={'text': "CPU %", 'font': {'color': COLORS['text_primary'], 'size': 14}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': COLORS['text_accent_cyan']},
                'bgcolor': '#222',
                'steps': [{'range': [85, 100], 'color': COLORS['text_accent_red']}]  # Red zone for high usage
            }
        )
    )
    cpu_figure.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fff'},
        height=150
    )

    # ====== MEMORY BAR CHART ======
    mem_figure = go.Figure(
        go.Bar(
            x=[memory_total],
            y=['RAM'],
            orientation='h',
            marker_color=COLORS['text_accent_yellow']
        )
    )
    mem_figure.update_layout(
        xaxis=dict(range=[0, RESOURCE_LIMITS['memory_max_system']], title="MB"),
        margin=dict(l=10, r=20, t=10, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fff'},
        height=100
    )

    # ====== DISK I/O BAR CHART ======
    disk_figure = go.Figure(
        go.Bar(
            x=[disk_total],
            y=['Disk'],
            orientation='h',
            marker_color=COLORS['text_accent_red']
        )
    )
    disk_figure.update_layout(
        xaxis=dict(range=[0, RESOURCE_LIMITS['disk_max_system']], title="MB/s"),
        margin=dict(l=10, r=20, t=10, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fff'},
        height=100
    )

    return process_data, cpu_figure, mem_figure, disk_figure


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