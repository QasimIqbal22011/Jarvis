# 🚀 How to Run Jarvis

## Prerequisites

Before running Jarvis, ensure you have the following installed:

### 1. **Python 3.9 or Higher**
   ```bash
   python --version
   ```
   Download from: https://www.python.org/downloads/

### 2. **Ollama (Required for LLM)**
   Download and install from: https://ollama.ai
   
   After installation, start Ollama:
   ```bash
   ollama serve
   ```
   
   Then pull a model (in another terminal):
   ```bash
   ollama pull llama2
   # or
   ollama pull llama3.1:8b
   ```

### 3. **Dependencies**
   Install Python packages from the `venv` folder or create a new environment:
   
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

## Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd C:\Jarvis
```

### Step 2: Activate Virtual Environment (if not already active)
```bash
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

Or manually install key packages:
```bash
pip install ollama
pip install pyttsx3
pip install pyaudio
pip install sounddevice
pip install openwakeword
pip install faster-whisper
pip install webrtcvad
pip install pystray
pip install pillow
pip install pywebview
pip install send2trash
pip install psutil
```

### Step 4: Ensure Ollama is Running
```bash
# In a separate terminal/command prompt:
ollama serve
```

## Running Jarvis

### **Method 1: Direct Python (Recommended for Development)**

```bash
cd C:\Jarvis
venv\Scripts\activate
python tray_app.py
```

**What happens:**
- Jarvis will start in the system tray (bottom right of taskbar)
- A popup window will appear with the blue sphere UI
- Say "Hey Jarvis" to wake it up
- The GUI will light up and respond to your commands

### **Method 2: Run from Python Directly (Alternative)**

```bash
python C:\Jarvis\tray_app.py
```

### **Method 3: Run as Admin (Recommended for Full Access)**

If you need full admin access for file operations:

```powershell
# Using PowerShell as Administrator
cd C:\Jarvis
venv\Scripts\activate
python tray_app.py
```

Or create a batch file (`run_jarvis.bat`):
```batch
@echo off
cd C:\Jarvis
venv\Scripts\activate
python tray_app.py
pause
```

Then right-click → "Run as administrator"

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution:** Install missing package
```bash
pip install [package_name]
```

### Issue: "Ollama is not responding"
**Solution:** 
1. Make sure Ollama is running in another terminal
2. Verify the model is downloaded:
   ```bash
   ollama list
   ```
3. If needed, pull a model:
   ```bash
   ollama pull llama3.1:8b
   ```

### Issue: "Microphone not found"
**Solution:**
1. Check if microphone is plugged in
2. Check Windows audio settings
3. Allow Jarvis microphone access in Windows privacy settings

### Issue: "No module named 'wake'" or other core modules
**Solution:**
1. Make sure you're in the correct directory: `C:\Jarvis`
2. Verify virtual environment is activated
3. Check that all Python files are in the correct folders

### Issue: "Permission denied" or "Access denied"
**Solution:**
Run as administrator (see Method 3 above)

## Testing Installation

Test if everything is installed correctly:

```bash
python -c "import ollama; print('✓ Ollama module OK')"
python -c "import pyttsx3; print('✓ Text-to-speech OK')"
python -c "import sounddevice; print('✓ Sound device OK')"
python -c "import faster_whisper; print('✓ Whisper OK')"
python -c "import pywebview; print('✓ Web view OK')"
```

## First Time Setup

When you run Jarvis for the first time:

1. **Model Downloads**: Whisper model (~500MB) will download automatically
2. **OpenWakeWord**: Wake word detection model will download
3. **Memory Creation**: `~/.jarvis/conversation_memory.json` will be created
4. **Logs**: `~/jarvis_log.txt` will be created

This may take a few minutes on first run.

## Usage

Once running:

1. **Wake Word**: Say "Hey Jarvis" to activate
2. **Commands**: Give voice commands like:
   - "Open Chrome"
   - "Search for files named document"
   - "Close notepad"
   - "What time is it?"
   - "Open YouTube in Chrome"

3. **Exit**: Click "Exit" in the system tray icon

## Advanced: Building Executable

To create a standalone `.exe` file:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller Jarvis.spec

# The .exe will be in the dist/Jarvis folder
```

Then run:
```bash
dist\Jarvis\Jarvis.exe
```

## Environment Variables (Optional)

Set these if you want to customize behavior:

```bash
# Use a specific model
set OLLAMA_MODEL=llama3.1:8b

# Set listen port
set OLLAMA_PORT=11434
```

## Logs

Jarvis creates a log file for debugging:
- **Location**: `~/jarvis_log.txt`
- **Contains**: All print statements, errors, and debug info

View the log:
```bash
type %USERPROFILE%\jarvis_log.txt
```

Or in PowerShell:
```powershell
Get-Content $env:USERPROFILE\jarvis_log.txt
```

## Performance Tips

1. **Keep Ollama warm**: Set `keep_alive: "30m"` in the code to keep the model in RAM
2. **Use faster models**: `mistral:7b` or `neural-chat:7b` are faster than `llama2`
3. **Reduce context**: Lower `num_ctx` if running on limited memory
4. **Close other apps**: Free up RAM for smooth operation

## System Requirements

- **OS**: Windows 10 or Windows 11
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 20GB+ (for models)
- **Microphone**: Required for wake word detection
- **Speakers**: Required for voice output

## Getting Help

Check these files for more info:
- `IMPROVEMENTS_IMPLEMENTED.md` - Recent improvements
- `IMPROVEMENTS_QUICK_REFERENCE.md` - Quick start guide
- `KIMI_IMPROVEMENTS_REPORT.md` - Detailed analysis

---

**Quick Start Summary:**
```bash
cd C:\Jarvis
venv\Scripts\activate
ollama serve  # In separate terminal
python tray_app.py
```

Say "Hey Jarvis" and enjoy! 🎤
