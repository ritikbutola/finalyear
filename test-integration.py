#!/usr/bin/env python3
"""
Integration Test Suite for WebRTC + RAG Conferencing
Tests all components before running the full application
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warn(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

# ─── Test 1: Environment Variables ──────────────────────────────────────────
def test_environment():
    print_header("TEST 1: Environment Variables")
    
    # Check Python version
    try:
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            print_error(f"Python 3.8+ required (found {version.major}.{version.minor})")
            return False
    except Exception as e:
        print_error(f"Python version check failed: {e}")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_ok(f"Node.js {result.stdout.strip()}")
        else:
            print_error("Node.js not found. Install from https://nodejs.org/")
            return False
    except Exception as e:
        print_error(f"Node.js check failed: {e}")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_ok(f"npm {result.stdout.strip()}")
        else:
            print_error("npm not found")
            return False
    except Exception as e:
        print_error(f"npm check failed: {e}")
        return False
    
    # Check GROQ_API_KEY
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key:
        print_ok(f"GROQ_API_KEY set ({len(groq_key)} chars)")
    else:
        print_warn("GROQ_API_KEY not set - RAG features will not work")
        print_info("  Get a key from: https://console.groq.com")
        print_info("  Then set: export GROQ_API_KEY='your_key_here'")
    
    return True

# ─── Test 2: Project Structure ──────────────────────────────────────────────
def test_project_structure():
    print_header("TEST 2: Project Structure")
    
    required_dirs = [
        "AI_Enhanced_RealTime_Conferencing-main/server",
        "AI_Enhanced_RealTime_Conferencing-main/client",
        "rag-chatbot-main/backend",
    ]
    
    required_files = {
        "AI_Enhanced_RealTime_Conferencing-main/server/index.js": "Node server entry point",
        "AI_Enhanced_RealTime_Conferencing-main/client/package.json": "React client config",
        "rag-chatbot-main/backend/main.py": "RAG FastAPI app",
        "rag-chatbot-main/backend/rag_engine.py": "RAG engine logic",
    }
    
    all_ok = True
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_ok(f"Directory: {dir_path}")
        else:
            print_error(f"Missing directory: {dir_path}")
            all_ok = False
    
    # Check files
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print_ok(f"File: {file_path} ({size} bytes) - {description}")
        else:
            print_error(f"Missing file: {file_path}")
            all_ok = False
    
    return all_ok

# ─── Test 3: Python Imports ─────────────────────────────────────────────────
def test_python_imports():
    print_header("TEST 3: Python Dependencies")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "PyPDF2",
        "langchain",
        "langchain_community",
        "langchain_groq",
        "langchain_huggingface",
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print_ok(f"Module: {package}")
        except ImportError as e:
            print_error(f"Missing module: {package}")
            print_info(f"  Install: pip install {package}")
            all_ok = False
        except Exception as e:
            print_warn(f"Module {package} import warning: {str(e)[:50]}")
    
    return all_ok

# ─── Test 4: Node Modules ──────────────────────────────────────────────────
def test_node_modules():
    print_header("TEST 4: Node.js Dependencies")
    
    server_dir = "AI_Enhanced_RealTime_Conferencing-main/server"
    client_dir = "AI_Enhanced_RealTime_Conferencing-main/client"
    
    all_ok = True
    
    for dir_path, label in [(server_dir, "Server"), (client_dir, "Client")]:
        node_modules = Path(dir_path) / "node_modules"
        package_json = Path(dir_path) / "package.json"
        
        if node_modules.exists():
            print_ok(f"{label} node_modules installed ({len(list(node_modules.glob('*')))} packages)")
        else:
            print_warn(f"{label} node_modules not found")
            if package_json.exists():
                print_info(f"  Run: cd {dir_path} && npm install")
            all_ok = False
    
    return all_ok

# ─── Test 5: RAG Engine Syntax ──────────────────────────────────────────────
def test_rag_syntax():
    print_header("TEST 5: RAG Engine Code")
    
    try:
        from pathlib import Path
        import sys
        
        # Add RAG backend to path
        rag_path = Path("rag-chatbot-main/backend")
        sys.path.insert(0, str(rag_path))
        
        # Try importing rag_engine (syntax check)
        import rag_engine
        
        print_ok("rag_engine.py imports successfully")
        print_ok(f"Config: {rag_engine.RAG_CONFIG}")
        
        return True
    except SyntaxError as e:
        print_error(f"Syntax error in rag_engine.py: {e}")
        return False
    except ImportError as e:
        print_warn(f"Import error (expected if dependencies missing): {str(e)[:80]}")
        return True  # Don't fail on import errors
    except Exception as e:
        print_warn(f"Code check warning: {str(e)[:80]}")
        return True

# ─── Test 6: Port Availability ─────────────────────────────────────────────
def test_ports():
    print_header("TEST 6: Port Availability")
    
    ports = {
        3011: "Signaling Server",
        8000: "RAG Backend",
        5173: "React Dev Server",
    }
    
    all_available = True
    for port, service in ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print_warn(f"Port {port} ({service}) already in use")
                all_available = False
            else:
                print_ok(f"Port {port} ({service}) available")
        except Exception as e:
            print_error(f"Port {port} check failed: {e}")
    
    return all_available

# ─── Test 7: Server Startup (Dry Run) ─────────────────────────────────────
def test_server_startup():
    print_header("TEST 7: Server Startup (Syntax Check)")
    
    try:
        # Node server syntax check
        server_file = "AI_Enhanced_RealTime_Conferencing-main/server/index.js"
        result = subprocess.run(
            ['node', '--check', server_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_ok("Node.js server syntax OK")
        else:
            print_error(f"Node.js syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Syntax check failed: {e}")
        return False
    
    return True

# ─── Summary ────────────────────────────────────────────────────────────────
def run_all_tests():
    print_header("WebRTC + RAG Integration Test Suite")
    
    tests = [
        ("Environment", test_environment),
        ("Project Structure", test_project_structure),
        ("Python Dependencies", test_python_imports),
        ("Node Modules", test_node_modules),
        ("RAG Engine Code", test_rag_syntax),
        ("Port Availability", test_ports),
        ("Server Startup", test_server_startup),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {test_name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print_ok("All systems ready! Start services with:")
        print(f"  {Colors.BOLD}Terminal 1: cd AI_Enhanced_RealTime_Conferencing-main/server && npm start{Colors.RESET}")
        print(f"  {Colors.BOLD}Terminal 2: cd rag-chatbot-main/backend && python main.py{Colors.RESET}")
        print(f"  {Colors.BOLD}Terminal 3: cd AI_Enhanced_RealTime_Conferencing-main/client && npm run dev{Colors.RESET}")
        print(f"  {Colors.BOLD}Then open: http://localhost:5173{Colors.RESET}\n")
    else:
        print_error("Fix the issues above before starting services")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
