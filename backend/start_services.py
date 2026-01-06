"""
Unified startup script for Backend + LightRAG services
Works on Windows and Linux (Render deployment ready)
"""
import os
import sys
import subprocess
import platform
import time
import signal
from pathlib import Path

# Fix Windows console encoding issues
if platform.system() == "Windows":
    # Set UTF-8 encoding for Windows console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # Set environment variable for subprocesses
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Colors for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text, color=Colors.CYAN):
    print(f"\n{color}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{Colors.END}\n")

def print_info(text):
    print(f"{Colors.CYAN}[INFO]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}[ERROR]{Colors.END} {text}")

# Get script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR
LIGHTRAG_DIR = SCRIPT_DIR / "lightrag" / "Lightrag_main"

# Detect OS
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

# Process list to track
processes = []

def cleanup(signum=None, frame=None):
    """Cleanup function to kill all child processes"""
    print_warning("\nShutting down services...")
    for process in processes:
        try:
            if IS_WINDOWS:
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                             capture_output=True)
            else:
                process.terminate()
                process.wait(timeout=5)
        except Exception as e:
            print_error(f"Error stopping process {process.pid}: {e}")
    print_success("All services stopped")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_port(port):
    """Check if a port is in use (excluding TIME_WAIT)"""
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True
            )
            # Ignore TIME_WAIT state (port will be available soon)
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    return True
            return False
        else:
            result = subprocess.run(
                ['ss', '-tuln'], 
                capture_output=True, 
                text=True
            )
            return f":{port}" in result.stdout
    except:
        return False

def kill_process_on_port(port):
    """Kill process using a specific port"""
    try:
        if IS_WINDOWS:
            # Find the process using the port
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True
            )
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    print_info(f"Killing process {pid} on port {port}...")
                    subprocess.run(['taskkill', '/F', '/PID', pid], 
                                 capture_output=True)
                    time.sleep(1)
                    return True
        else:
            # Linux/Mac
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'], 
                capture_output=True, 
                text=True
            )
            if result.stdout:
                pid = result.stdout.strip()
                print_info(f"Killing process {pid} on port {port}...")
                subprocess.run(['kill', '-9', pid], capture_output=True)
                time.sleep(1)
                return True
    except Exception as e:
        print_warning(f"Could not kill process on port {port}: {e}")
    return False

def copy_env_file():
    """Copy .env file from backend to LightRAG directory (optional for Render)"""
    backend_env = BACKEND_DIR / ".env"
    lightrag_env = LIGHTRAG_DIR / ".env"
    
    if backend_env.exists():
        print_info("Copying shared .env file to LightRAG directory...")
        import shutil
        shutil.copy(backend_env, lightrag_env)
        print_success(".env file synchronized")
    else:
        # On Render, create .env from environment variables
        if os.getenv("RENDER"):
            print_info("Running on Render - creating .env from environment variables")
            env_content = f"""# Auto-generated for LightRAG on Render
GEMINI_API_KEY={os.getenv('GEMINI_API_KEY', '')}
LLM_BINDING={os.getenv('LLM_BINDING', 'gemini')}
LLM_MODEL={os.getenv('LLM_MODEL', 'gemini-2.0-flash-lite')}
LLM_BINDING_HOST={os.getenv('LLM_BINDING_HOST', 'https://generativelanguage.googleapis.com')}
LLM_BINDING_API_KEY={os.getenv('LLM_BINDING_API_KEY', os.getenv('GEMINI_API_KEY', ''))}
EMBEDDING_BINDING={os.getenv('EMBEDDING_BINDING', 'gemini')}
EMBEDDING_MODEL={os.getenv('EMBEDDING_MODEL', 'gemini-embedding-001')}
EMBEDDING_BINDING_HOST={os.getenv('EMBEDDING_BINDING_HOST', 'https://generativelanguage.googleapis.com')}
EMBEDDING_BINDING_API_KEY={os.getenv('EMBEDDING_BINDING_API_KEY', os.getenv('GEMINI_API_KEY', ''))}
EMBEDDING_DIM={os.getenv('EMBEDDING_DIM', '768')}
EMBEDDING_TOKEN_LIMIT={os.getenv('EMBEDDING_TOKEN_LIMIT', '2048')}
HOST=0.0.0.0
PORT=9621
"""
            try:
                with open(lightrag_env, 'w') as f:
                    f.write(env_content)
                print_success(f".env created at {lightrag_env}")
            except Exception as e:
                print_warning(f"Failed to create .env: {e}")
        else:
            print_warning(f"No .env file found at: {backend_env}")
            print_warning("Please create a .env file in the backend/ directory")
            print_warning("See .env.example for reference")

def start_lightrag():
    """Start LightRAG server"""
    print_info("Starting LightRAG Server (port 9621)...")
    
    # Check if LightRAG venv exists
    if IS_WINDOWS:
        venv_python = LIGHTRAG_DIR / ".venv" / "Scripts" / "python.exe"
        lightrag_cmd = LIGHTRAG_DIR / ".venv" / "Scripts" / "lightrag-server.exe"
    else:
        venv_python = LIGHTRAG_DIR / ".venv" / "bin" / "python"
        lightrag_cmd = LIGHTRAG_DIR / ".venv" / "bin" / "lightrag-server"
    
    if not venv_python.exists():
        print_error(f"LightRAG virtual environment not found at: {venv_python}")
        print_error("Please run: cd lightrag/Lightrag_main && uv sync --extra api")
        
        # On Render, try installing it now
        if os.getenv("RENDER"):
            print_info("Attempting to install LightRAG dependencies...")
            os.chdir(LIGHTRAG_DIR)
            try:
                subprocess.run(["pip", "install", "uv"], check=True)
                subprocess.run(["uv", "sync", "--extra", "api", "--no-cache"], check=True)
                print_success("LightRAG dependencies installed")
                # Re-check if command exists now
                if not lightrag_cmd.exists():
                    print_error("lightrag-server command still not found after installation")
                    sys.exit(1)
            except Exception as e:
                print_error(f"Failed to install dependencies: {e}")
                sys.exit(1)
            os.chdir(BACKEND_DIR)
        else:
            sys.exit(1)
    
    # Start LightRAG server
    os.chdir(LIGHTRAG_DIR)
    
    # Set UTF-8 encoding for subprocess to handle Unicode characters
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # Create log files for debugging
    log_file = LIGHTRAG_DIR / "lightrag_startup.log"
    error_file = LIGHTRAG_DIR / "lightrag_error.log"
    
    # Start with log files to capture startup errors
    with open(log_file, 'w') as log_out, open(error_file, 'w') as log_err:
        process = subprocess.Popen(
            [str(lightrag_cmd)],
            stdout=log_out,
            stderr=log_err,
            env=env
        )
    
    processes.append(process)
    print_success(f"LightRAG server started (PID: {process.pid})")
    print_info(f"LightRAG logs: {log_file}")
    
    # Check if process is still alive after a moment
    time.sleep(2)
    if process.poll() is not None:
        print_error("LightRAG failed to start! Check logs:")
        print_error(f"  Log: {log_file}")
        print_error(f"  Error: {error_file}")
        # Print error contents
        try:
            with open(error_file, 'r') as f:
                error_content = f.read()
                if error_content:
                    print_error(f"Error output:\n{error_content}")
        except:
            pass
        sys.exit(1)
    
    # Go back to backend directory
    os.chdir(BACKEND_DIR)
    return process

def start_backend():
    """Start Backend API server"""
    # Get port from environment or use default
    port = os.getenv("PORT", "8000")
    print_info(f"Starting Backend API Server (port {port})...")
    
    # On Render, use system Python (dependencies already installed)
    # On local, use venv
    if os.getenv("RENDER"):
        python_cmd = sys.executable  # Use current Python
    else:
        # Check if backend venv exists
        if IS_WINDOWS:
            venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
        else:
            venv_python = BACKEND_DIR / "venv" / "bin" / "python"
        
        if not venv_python.exists():
            print_error(f"Backend virtual environment not found at: {venv_python}")
            print_error("Please run: python -m venv venv && pip install -r requirements.txt")
            sys.exit(1)
        
        python_cmd = str(venv_python)
    
    # Start backend server
    os.chdir(BACKEND_DIR)
    
    # Set UTF-8 encoding for subprocess to handle Unicode characters
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # Start with direct output to avoid buffering issues
    process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "app.main:app", 
         "--host", "0.0.0.0", "--port", port,
         "--timeout-graceful-shutdown", "1"],  # Fast shutdown to free port quickly
        stdout=None,  # Direct output to terminal (no buffering)
        stderr=None,  # Direct error output to terminal
        env=env
    )
    
    processes.append(process)
    print_success(f"Backend server started (PID: {process.pid}) on port {port}")
    return process

def main():
    """Main function"""
    print_header("Starting Farm Vaidya Services")
    
    # Validate required environment variables on Render
    if os.getenv("RENDER"):
        required_vars = ["GEMINI_API_KEY", "MONGO_URI", "JWT_SECRET"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            print_error(f"Missing required environment variables: {', '.join(missing)}")
            print_error("Please set these in Render's Environment tab")
            sys.exit(1)
    
    # On Render, skip port checks (Render manages ports)
    if not os.getenv("RENDER"):
        # Check and handle ports with retry for TIME_WAIT
        max_retries = 3
        for retry in range(max_retries):
            if check_port(8000):
                if retry == 0:
                    print_warning("Port 8000 is already in use.")
                    print_info("Attempting to free port 8000...")
                    if kill_process_on_port(8000):
                        print_success("Port 8000 freed successfully")
                        time.sleep(2)
                        break
                    else:
                        print_info("Port may be in TIME_WAIT state, waiting...")
                        time.sleep(3)
                else:
                    print_info(f"Retry {retry}/{max_retries-1}: Waiting for port 8000...")
                    time.sleep(3)
            else:
                break
        else:
            print_error("Port 8000 still in use after retries. Please wait a moment and try again.")
            sys.exit(1)
        
        if check_port(9621):
            print_warning("Port 9621 is already in use.")
            print_info("Attempting to free port 9621...")
            if kill_process_on_port(9621):
                print_success("Port 9621 freed successfully")
            else:
                print_error("Could not free port 9621. Please stop the service manually.")
                sys.exit(1)
    
    # Copy .env file
    copy_env_file()
    
    print()
    
    # Start LightRAG first
    lightrag_process = start_lightrag()
    
    # Wait for LightRAG to initialize and monitor for crashes
    print_info("Waiting for LightRAG to initialize...")
    for i in range(10):  # Check for 10 seconds
        time.sleep(1)
        if lightrag_process.poll() is not None:
            print_error("LightRAG crashed during initialization!")
            # Print log files
            log_file = LIGHTRAG_DIR / "lightrag_startup.log"
            error_file = LIGHTRAG_DIR / "lightrag_error.log"
            
            print_error(f"\n=== LightRAG Startup Log ===")
            try:
                with open(log_file, 'r') as f:
                    print(f.read())
            except:
                print_error("Could not read startup log")
            
            print_error(f"\n=== LightRAG Error Log ===")
            try:
                with open(error_file, 'r') as f:
                    print(f.read())
            except:
                print_error("Could not read error log")
            
            sys.exit(1)
    
    print_success("LightRAG initialization complete")
    
    # Start Backend
    backend_process = start_backend()
    
    # Wait for backend to initialize
    time.sleep(3)
    
    # Get port for display
    port = os.getenv("PORT", "8000")
    
    # Print success info
    print_header("Services Started Successfully!", Colors.GREEN)
    print(f"{Colors.CYAN}Backend API:{Colors.END}     http://localhost:{port}")
    print(f"{Colors.CYAN}Backend Docs:{Colors.END}    http://localhost:{port}/docs")
    print(f"{Colors.CYAN}LightRAG API:{Colors.END}    http://localhost:9621")
    print(f"{Colors.CYAN}LightRAG WebUI:{Colors.END}  http://localhost:9621/webui")
    print(f"{Colors.CYAN}LightRAG Docs:{Colors.END}   http://localhost:9621/docs")
    print()
    print_info("Press Ctrl+C to stop all services")
    print()
    
    # Keep script running and monitor processes
    try:
        while True:
            # Check if processes are still alive
            if lightrag_process.poll() is not None:
                print_error("LightRAG process died unexpectedly!")
                cleanup()
            if backend_process.poll() is not None:
                print_error("Backend process died unexpectedly!")
                cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print_error(f"Error: {e}")
        cleanup()
        sys.exit(1)
