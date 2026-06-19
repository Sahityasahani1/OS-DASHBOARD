# OS Resource Dashboard v3.0 — Quick Start Guide

## 🎯 What is This?

The **OS Resource Dashboard** is an interactive simulator that mimics an operating system's process management and scheduling system. It lets you:
- Monitor CPU, Memory, and Disk I/O in real-time with history graphs
- Spawn processes using preset templates or custom configurations
- Choose from 6 scheduling algorithms and watch them execute
- Terminate processes manually or kill all at once
- View color-coded kernel event logs
- Pause, resume, and adjust simulation speed

---

## ⚡ Quick Start

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Start the Dashboard
```bash
python OSdashbord.py
```

### 3️⃣ Open in Browser
Go to: `http://localhost:8050/`

---

## 🎮 How to Use

### Creating a Process

**Quick Way — Use a Preset:**
1. Click one of the preset buttons at the top of the Process Injector:
   - 🌐 **Browser** (CPU: 25%, RAM: 512 MB, Disk: 30 MB/s)
   - 🎮 **Game** (CPU: 60%, RAM: 1024 MB, Disk: 100 MB/s)
   - 📝 **Editor** (CPU: 3%, RAM: 64 MB, Disk: 5 MB/s)
   - 🗄️ **Database** (CPU: 15%, RAM: 256 MB, Disk: 200 MB/s)
   - 🔬 **Compiler** (CPU: 40%, RAM: 512 MB, Disk: 80 MB/s)
2. The form auto-fills with resource values
3. Click **"⚡ Spawn Process"**

**Custom Way:**
1. Type a name in the "Process Name" field
2. Adjust the CPU, RAM, and Disk I/O sliders
3. Click **"⚡ Spawn Process"**

### Terminating Processes

- **Kill selected**: Click one or more rows in the table → Click **"☠️ SIGKILL"**
- **Kill all**: Click **"💀 Kill All Processes"** to terminate everything

### Choosing a Scheduling Algorithm

1. Select from the **Scheduling Algorithm** dropdown
2. Read the info card that appears — it explains how the algorithm works
3. Watch the **Gantt Timeline** to see which process runs at each tick

### Controlling the Simulation

- **⏸ Pause**: Freezes the scheduler clock (becomes **▶ Resume**)
- **Speed slider**: Drag between 0.5× (slow) and 4× (fast)

---

## 📊 Understanding the Dashboard

### Stats Ribbon (top)
```
⏱ UPTIME │ 🚀 SPAWNED │ ✅ COMPLETED │ ☠️ KILLED │ 📊 ACTIVE
  01:23   │     5      │      2       │     1     │     2
```

### Three-Column Layout
```
┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│ ⚡ System    │  │ 🚀 Process   │  │ 📟 Kernel   │
│ Load         │  │ Injector     │  │ Logs        │
│              │  │              │  │             │
│ CPU ◕ 45%   │  │ [Presets]    │  │ [APPROVED]  │
│ RAM ████ 30% │  │ [Algorithm]  │  │ [EXIT]      │
│ Disk ██ 15%  │  │ [Sliders]    │  │ [KILL]      │
│              │  │ [Spawn ⚡]   │  │ [Clear]     │
└──────────────┘  └──────────────┘  └─────────────┘
```

### Resource History
- 60-second sliding window graph
- Three colored lines: CPU% (cyan), RAM% (yellow), Disk% (red)

### Process Table
```
┌──────────────────────────────────────────────────────────┐
│ PID  │ Name      │ State   │ CPU │ RAM  │ Disk │Time│Prio│
│ 1234 │ Browser   │ RUNNING │ 25  │ 512  │  30  │ 12 │  1 │
│ 5678 │ Editor    │ READY   │  3  │  64  │   5  │ 28 │  2 │
└──────────────────────────────────────────────────────────┘
```
- **RUNNING** row glows cyan
- **Time Left** turns yellow < 10s, red < 5s

### Gantt Timeline
- Color-coded blocks showing which PID executed at each tick
- Gray = IDLE (no process running)

---

## 🔍 Reading the Kernel Log

Log entries are color-coded by type:

| Color | Event | Meaning |
|-------|-------|---------|
| 🟢 Cyan | `[APPROVED]` | Process spawned successfully |
| 🔴 Red | `[DENIED]` | Spawn rejected (insufficient resources) |
| 🔴 Red | `[KILL]` | Process terminated by user |
| ⚫ Gray | `[EXIT]` | Process finished naturally |
| 🔵 Blue | `[SCHEDULER]` | Periodic scheduler info |
| 🔴 Flash | `[DEADLOCK]` | Resources over-allocated — scheduler halted |
| 🟡 Yellow | `[WARN]` | Warnings (e.g., no process name) |

**Example log:**
```
[14:23:45] [APPROVED] PID 5234 (WebBrowser) spawned — Lifetime: 28s
[14:23:50] [EXIT] PID 4891 (TextEditor) completed.
[14:23:52] [KILL] PID 5234 (WebBrowser) terminated by Admin.
[14:23:55] [SCHEDULER] Algorithm: Round-Robin (TQ=10s) | Active: 3 processes
```

---

## 💡 Tips & Tricks

### Try Different Algorithms
- **FIFO**: Watch how short processes wait behind long ones (convoy effect)
- **Round-Robin**: See fair CPU distribution with time quantum rotation
- **SJF/SRTN**: Observe how short jobs get priority
- **Priority**: Notice how low-CPU processes execute first
- **Random**: Watch unpredictable execution patterns

### Trigger a Deadlock
1. Spawn processes until total CPU > 100% or RAM > 8192 MB
2. Watch the deadlock warning appear in the kernel log
3. The scheduler halts — you must kill a process to recover

### Study Algorithms Step-by-Step
1. Spawn several processes
2. Click **⏸ Pause** to freeze
3. Set speed to **0.5×**
4. Click **▶ Resume** and watch tick-by-tick execution

### Watch the Gantt Chart
- Each color represents a different PID
- Compare how different algorithms distribute CPU time

---

## 🚨 Common Issues

### "Address already in use" Error
**Problem:** Port 8050 is already in use
**Solution:** Close other apps using that port, or restart your terminal

### Dashboard Not Loading
**Solution:**
1. Check terminal for error messages
2. Refresh the page (Ctrl+R or F5)
3. Clear browser cache

### Processes Not Updating
**Solution:**
1. Check if the scheduler is **paused** (click ▶ Resume)
2. Spawn a new process to trigger updates
3. Check browser console (F12) for errors

---

## 📚 Key Concepts

### PID (Process ID)
- Unique number (1000–9999) assigned to each process
- Displayed in the table and kernel log

### Scheduling Algorithms
- **Non-Preemptive**: Running process can't be interrupted
- **Preemptive**: Running process can be swapped out for a higher-priority one

### Deadlock
- Occurs when total resource demand exceeds system capacity
- Scheduler halts until resources are freed (kill a process)

### Admission Control
- New processes are rejected if they would exceed system limits
- Logged as `[DENIED]` in the kernel log

---

## 🎓 Learning Objectives

This dashboard teaches:
- ✅ Process lifecycle (spawn → schedule → run → exit)
- ✅ 6 CPU scheduling algorithms and their tradeoffs
- ✅ Resource management and admission control
- ✅ Deadlock detection and recovery
- ✅ Process state transitions (READY ↔ RUNNING)
- ✅ Real-time system monitoring
- ✅ Process priority and queue ordering

---

## ℹ️ Need Help?

- **Dashboard Code**: See `OSdashbord.py`
- **Full Documentation**: Read `README.md`
- **Code Architecture**: See `CODE_STRUCTURE.md`
- **Dash Docs**: https://dash.plotly.com/
- **Plotly Docs**: https://plotly.com/python/

---

**Happy monitoring! 🚀**
