# OS Resource Dashboard - Quick Start Guide

## 🎯 What is This?

The **OS Resource Dashboard** is an interactive simulator that mimics an operating system's process management system. It allows you to:
- Monitor CPU, Memory, and Disk I/O usage in real-time
- Create (spawn) virtual processes with custom resource requirements
- Terminate processes manually
- View system events in a kernel log

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
**Step-by-step instructions:**

1. **Name Your Process**
   - Type a name in the "Process Name" field
   - Example: "worker", "backup", "server"

2. **Set CPU Requirement**
   - Drag the CPU slider (left = low, right = high)
   - Range: 1% to 100%

3. **Set Memory Requirement**
   - Drag the RAM slider
   - Range: 16 MB to 2048 MB
   - Start with 256 MB for testing

4. **Set Disk I/O Requirement**
   - Drag the Disk I/O slider
   - Range: 0 to 500 MB/s

5. **Click "Spawn Process"**
   - Process is created and appears in the table
   - Metrics update automatically

### Terminating a Process

1. **Click a row** in the process table (it turns red)
2. **Click "SIGKILL (Force Stop)"** button
3. Process is immediately killed

---

## 📊 Understanding the Dashboard

### Left Panel: System Load
```
┌─────────────────────┐
│ CPU Gauge           │  <- Shows total CPU usage (red = high)
├─────────────────────┤
│ RAM Bar             │  <- Shows total memory used
├─────────────────────┤
│ Disk Bar            │  <- Shows disk I/O activity
└─────────────────────┘
```

### Middle Panel: Process Injector
```
┌─────────────────────┐
│ Process Name Input  │  <- Enter name here
├─────────────────────┤
│ CPU Slider          │  <- Set CPU %
├─────────────────────┤
│ RAM Slider          │  <- Set Memory
├─────────────────────┤
│ Disk I/O Slider     │  <- Set Disk usage
├─────────────────────┤
│ Spawn Process Btn   │  <- Create process
└─────────────────────┘
```

### Right Panel: Kernel Logs
```
┌─────────────────────────────────┐
│ [HH:MM:SS] [FORK] PID 5234...  │
│ [HH:MM:SS] [EXIT] PID 4891...  │
│ [HH:MM:SS] [KILL] PID 5234...  │
└─────────────────────────────────┘
```

### Bottom: Process Table
```
┌─────────────────────────────────────────────┐
│ PID | Name | CPU (%) | RAM (MB) | Time Left │
│ 1234| app1 |   25    |   512    |    12     │
│ 5678| srv2 |   45    |   256    |    28     │
└─────────────────────────────────────────────┘
```

---

## 🔍 Reading the Kernel Log

Log entries show what's happening in the system:

| Event | Meaning |
|-------|---------|
| `[FORK]` | New process created |
| `[EXIT]` | Process finished naturally |
| `[KILL]` | Process terminated by user |
| `[SYS]` | System information |

**Example:**
```
[14:23:45] [FORK] PID 5234 (worker) spawned.
[14:23:50] [EXIT] PID 4891 completed naturally.
[14:23:52] [KILL] PID 5234 terminated by Admin.
```

---

## 💡 Tips & Tricks

### Create Multiple Processes
- Spawn several processes to see metrics increase
- Watch how CPU and memory stack up
- Try to exceed 100% CPU to see the gauge turn red

### Experiment with Resources
- Low values: processes run fast, use less resources
- High values: processes demand more system resources
- All resources are optional (0 is valid for Disk I/O)

### Monitor the Log
- Check the kernel log to track what happened
- Useful for debugging or learning process management

### Reset Everything
- Simply restart the app (Ctrl+C in terminal, then `python OSdashbord.py`)
- All processes and logs will be reset

---

## 🚨 Common Issues

### "Address already in use" Error
**Problem:** Port 8050 is already being used  
**Solution:** Close other apps using that port or restart your app

### Dashboard Not Loading
**Problem:** Browser shows blank page  
**Solution:**
1. Check the terminal for error messages
2. Try refreshing the page (Ctrl+R or F5)
3. Clear browser cache

### Processes Not Updating
**Problem:** Metrics aren't changing  
**Solution:**
1. Try spawning a new process
2. Check if there are any browser errors (F12)
3. Refresh the page

---

## 📚 Key Concepts

### PID (Process ID)
- Unique number assigned to each process
- Range: 1000-9999 in this simulator
- Used to identify and track processes

### Resource Requirements
- **CPU**: How much processing power (percentage of available CPU)
- **Memory**: How much RAM the process needs (in MB)
- **Disk I/O**: How much disk read/write activity (in MB/s)

### Process Lifetime
- Each process automatically terminates after 15-45 seconds
- Seen as "Time Left (s)" in the table
- Counts down every second
- Shows as [EXIT] in kernel log when complete

---

## 🎓 Learning Objectives

This dashboard teaches:
- ✅ How processes use system resources
- ✅ Process lifecycle (spawn → run → exit)
- ✅ Resource management concepts
- ✅ Event logging and tracking
- ✅ Real-time system monitoring
- ✅ Process termination (signals)

---

## ℹ️ Need Help?

Check out these resources:
- **Dashboard Code**: Look at `OSdashbord.py`
- **Full Documentation**: Read `README.md`
- **Requirements**: See `requirements.txt`

---

**Happy monitoring! 🚀**
