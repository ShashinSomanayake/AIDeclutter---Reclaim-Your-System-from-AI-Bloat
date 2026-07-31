#!/usr/bin/env python3
"""
AI Tool Manager - System Scanner & Uninstaller
==============================================
Detects installed AI/ML tools, shows paths/sizes/launch commands,
and provides safe uninstallation.

Requirements: PySide6 (pip install pyside6)
Standard library only otherwise.

Usage: python ai_tool_manager.py
"""

import sys
import os
import subprocess
import shutil
import json
import re
import platform
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from functools import lru_cache
import traceback

# Check PySide6 availability
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTableView, QLabel, QPushButton, QLineEdit, QTextEdit,
        QSplitter, QMessageBox, QProgressBar, QHeaderView, QMenu,
        QFileDialog, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
        QAbstractItemView, QStyledItemDelegate, QStyle, QFrame, QGroupBox,
        QFormLayout, QComboBox, QCheckBox, QTreeWidget, QTreeWidgetItem,
        QTabWidget, QSizePolicy, QToolButton
    )
    from PySide6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, QThreadPool, QRunnable,
        Signal as pyqtSignal, QObject, QSize, QSortFilterProxyModel, 
        QTimer, QSettings
    )
    from PySide6.QtGui import QAction, QFont, QDesktopServices, QPalette, QColor
except ImportError:
    print("ERROR: PySide6 is not installed.")
    print("Install it with: pip install pyside6")
    sys.exit(1)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    try:
        import winreg
    except ImportError:
        winreg = None

# =============================================================================
# CONFIGURATION
# =============================================================================

AI_KEYWORDS = [
    # LLMs & Inference
    "ollama", "llama", "llamacpp", "llama.cpp", "llama-swap", "llamaswap",
    "unsloth", "vllm", "text-generation-webui", "oobabooga", "kobold",
    "koboldcpp", "lm-studio", "lmstudio", "gpt4all", "jan", "msty",
    "enchanted", "localai", "dalai", "petals", "llamafile", "mistral",
    "mixtral", "qwen", "gemma", "phi", "codellama", "deepseek",
    "deepseek-coder", "starcoder", "santacoder", "wizardlm", "vicuna",
    "alpaca", "openorca", "nous", "phind", "replit", "stablelm",
    "command-r", "dbrx", "falcon", "mpt", "gpt-neo", "gpt-j",
    "bloom", "opt", "pythia", "gpt2", "exllama", "exllamav2",
    "auto-gptq", "awq", "gguf", "ggml", "tensorrt-llm", "onnxruntime",
    "openvino", "bigdl", "ipex",

    # Python ML Ecosystem
    "torch", "pytorch", "tensorflow", "keras", "jax", "flax", "mlx",
    "transformers", "huggingface", "tokenizers", "datasets", "accelerate",
    "peft", "bitsandbytes", "trl", "trlx", "xformers", "flash-attn",
    "deepspeed", "fairscale", "megatron", "colossalai", "alpaca-lora",
    "qlora", "lora", "adapters", "diffusers", "stable-diffusion",
    "controlnet", "t2i", "compel", "safetensors",

    # AI Coding Assistants
    "codeium", "continue", "cursor", "aider", "codewhisperer", "tabnine",
    "kite", "github-copilot", "copilot", "open-interpreter", "interpreter",
    "devin", "supermaven", "cody", "sourcegraph", "codegpt", "chatgpt",
    "claude-dev", "claude-code", "anthropic", "openai",

    # Frameworks & Runtimes
    "langchain", "langgraph", "crewai", "autogen", "agentgpt", "babyagi",
    "gpt-engineer", "meta-gpt", "camel", "llama-index", "haystack",
    "semantic-kernel", "guidance", "outlines", "instructor", "marvin",
    "litellm", "portkey", "llamaindex",

    # Vector DBs & Storage
    "chromadb", "chroma", "weaviate", "qdrant", "pinecone", "milvus",
    "faiss", "lancedb", "pgvector", "vectordb", "redis-stack", "memgraph",

    # Training & Fine-tuning UI
    "kohya", "kohya_ss", "dreambooth", " textual-inversion", "lycoris",
    "comfyui", "invokeai", "automatic1111", "stable-diffusion-webui",
    "fooocus", "ruinedfooocus", "focus", "midjourney", "dall-e",

    # Media/Codecs (user mentioned)
    "codec", "ffmpeg", "gstreamer", "opencv", "opengl", "mesa", "vulkan",
    "cuda", "cudnn", "cutlass", "cub", "nccl", "nvidia", "amd-gpu",
    "directml", "webgpu", "webnn",

    # Conda/Env managers
    "conda", "anaconda", "miniconda", "mamba", "micromamba", "pipenv",
    "poetry", "virtualenv", "venv", "pyenv", "pixi",

    # Jupyter/IDE
    "jupyter", "notebook", "lab", "hub", "voila", "panel", "streamlit",
    "gradio", "chainlit", "mesop", "stlite", "vscode", "code", "cursor",
    "windsurf", "zed", "trae",

    # Misc AI tools
    "whisper", "faster-whisper", "insanely-fast-whisper", "bark", "tortoise",
    "coqui", "piper", "speechbrain", "wav2lip", "rvc", "so-vits",
    "edge-tts", "gpt-sovits", "fishspeech", "parler",
]

# Normalize keywords for matching
AI_KEYWORDS_SET = set(k.lower() for k in AI_KEYWORDS)

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DetectedTool:
    name: str
    version: str
    tool_type: str  # Python, System, Brew, NPM, Docker, etc.
    path: str
    size_bytes: int = 0
    size_str: str = "Calculating..."
    launch_cmd: str = ""
    uninstall_cmd: str = ""
    description: str = ""
    files: List[str] = field(default_factory=list)
    confirmed: bool = False  # Whether detection is confirmed/exists

    def __post_init__(self):
        if self.size_bytes > 0:
            self.size_str = self._format_size(self.size_bytes)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        size = float(size_bytes)
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024
            idx += 1
        return f"{size:.2f} {units[idx]}"


# =============================================================================
# SYSTEM SCANNER
# =============================================================================

class SystemScanner(QObject):
    progress = pyqtSignal(str, int)  # message, percent
    tool_found = pyqtSignal(DetectedTool)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run_scan(self):
        """Main scan entry point."""
        try:
            self.progress.emit("Starting system scan...", 0)

            # 1. Python packages (usually biggest storage hog)
            if not self._cancelled:
                self.progress.emit("Scanning Python packages...", 5)
                self._scan_python_packages()

            # 2. System executables in PATH
            if not self._cancelled:
                self.progress.emit("Scanning PATH executables...", 20)
                self._scan_path_executables()

            # 3. Platform-specific package managers
            if IS_WINDOWS and not self._cancelled:
                self.progress.emit("Scanning Windows registry...", 35)
                self._scan_windows_registry()
                self.progress.emit("Scanning Scoop/WinGet...", 45)
                self._scan_scoop()
                self._scan_winget()

            if IS_MACOS and not self._cancelled:
                self.progress.emit("Scanning Homebrew...", 35)
                self._scan_brew()
                self.progress.emit("Scanning macOS Applications...", 45)
                self._scan_macos_apps()

            if IS_LINUX and not self._cancelled:
                self.progress.emit("Scanning APT packages...", 35)
                self._scan_apt()
                self.progress.emit("Scanning Flatpak/Snap...", 45)
                self._scan_flatpak()
                self._scan_snap()

            # 4. NPM global packages
            if not self._cancelled:
                self.progress.emit("Scanning NPM global packages...", 55)
                self._scan_npm_global()

            # 5. Docker images
            if not self._cancelled:
                self.progress.emit("Scanning Docker images...", 65)
                self._scan_docker()

            # 6. Common installation directories
            if not self._cancelled:
                self.progress.emit("Scanning common directories...", 75)
                self._scan_common_dirs()

            # 7. VS Code/Cursor extensions
            if not self._cancelled:
                self.progress.emit("Scanning editor extensions...", 85)
                self._scan_vscode_extensions()

            if not self._cancelled:
                self.progress.emit("Scan complete!", 100)

        except Exception as e:
            self.progress.emit(f"Error during scan: {str(e)}", 100)
        finally:
            self.finished.emit()

    def _is_ai_related(self, name: str) -> bool:
        """Check if a name matches AI keywords."""
        name_lower = name.lower().replace("_", "").replace("-", "").replace(".", "")
        for keyword in AI_KEYWORDS_SET:
            kw = keyword.replace("_", "").replace("-", "").replace(".", "")
            if kw in name_lower or name_lower in kw:
                return True
        return False

    def _safe_run(self, cmd: List[str], timeout: int = 15) -> Optional[str]:
        """Safely run a command and return stdout."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                encoding="utf-8", errors="ignore"
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None

    def _get_dir_size(self, path: str) -> int:
        """Calculate total size of a directory."""
        total = 0
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            for dirpath, dirnames, filenames in os.walk(path):
                if self._cancelled:
                    break
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp) and not os.path.islink(fp):
                        total += os.path.getsize(fp)
        except Exception:
            pass
        return total

    def _scan_python_packages(self):
        """Scan pip-installed packages."""
        # Get pip list
        output = self._safe_run([sys.executable, "-m", "pip", "list", "--format=json"], timeout=30)
        if not output:
            return

        try:
            packages = json.loads(output)
        except json.JSONDecodeError:
            return

        # Get site-packages locations
        site_paths = []
        try:
            import site
            site_paths = site.getsitepackages()
            if hasattr(site, "getusersitepackages"):
                user_site = site.getusersitepackages()
                if user_site:
                    site_paths.append(user_site)
        except Exception:
            pass

        for pkg in packages:
            if self._cancelled:
                break
            name = pkg.get("name", "")
            version = pkg.get("version", "unknown")

            if not self._is_ai_related(name):
                continue

            # Find installation path
            pkg_path = ""
            files = []
            for sp in site_paths:
                candidates = [
                    os.path.join(sp, name),
                    os.path.join(sp, name.lower()),
                    os.path.join(sp, name.replace("-", "_")),
                    os.path.join(sp, name.replace("_", "-")),
                    os.path.join(sp, name + ".dist-info"),
                    os.path.join(sp, name + ".egg-info"),
                ]
                for cand in candidates:
                    if os.path.exists(cand):
                        pkg_path = cand
                        files.append(cand)
                        break
                if pkg_path:
                    break

            if not pkg_path:
                pkg_path = site_paths[0] if site_paths else "Unknown"

            size = self._get_dir_size(pkg_path) if pkg_path and os.path.exists(pkg_path) else 0

            tool = DetectedTool(
                name=name,
                version=version,
                tool_type="Python Package",
                path=pkg_path,
                size_bytes=size,
                launch_cmd=f'python -c "import {name.replace("-", "_")}"',
                uninstall_cmd=f"{sys.executable} -m pip uninstall -y {name}",
                description=f"Python package installed via pip",
                files=files,
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_path_executables(self):
        """Scan executables in PATH."""
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        found_names = set()

        for directory in path_dirs:
            if self._cancelled:
                break
            if not os.path.isdir(directory):
                continue

            try:
                entries = os.listdir(directory)
            except Exception:
                continue

            for entry in entries:
                if self._cancelled:
                    break

                name = entry
                if IS_WINDOWS:
                    name = os.path.splitext(entry)[0]

                if name.lower() in found_names:
                    continue

                if not self._is_ai_related(name):
                    continue

                found_names.add(name.lower())
                full_path = os.path.join(directory, entry)

                if not os.path.isfile(full_path):
                    continue

                size = os.path.getsize(full_path)

                # Try to get version
                version = "unknown"
                try:
                    ver_output = self._safe_run([full_path, "--version"], timeout=5)
                    if ver_output:
                        version = ver_output.strip().split()[0][:50]
                except Exception:
                    pass

                tool = DetectedTool(
                    name=name,
                    version=version,
                    tool_type="Executable",
                    path=full_path,
                    size_bytes=size,
                    launch_cmd=full_path,
                    uninstall_cmd=f"Remove file: {full_path}",
                    description=f"Executable found in PATH",
                    files=[full_path],
                    confirmed=True
                )
                self.tool_found.emit(tool)

    def _scan_windows_registry(self):
        """Scan Windows registry for installed programs."""
        if not winreg:
            return

        keys_to_check = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]

        found_names = set()

        for hkey, subkey in keys_to_check:
            if self._cancelled:
                break
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        if self._cancelled:
                            break
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as item_key:
                                def get_val(name):
                                    try:
                                        return winreg.QueryValueEx(item_key, name)[0]
                                    except Exception:
                                        return ""

                                display_name = get_val("DisplayName")
                                if not display_name:
                                    continue

                                name_lower = display_name.lower()
                                if name_lower in found_names:
                                    continue

                                if not self._is_ai_related(display_name):
                                    continue

                                found_names.add(name_lower)

                                install_loc = get_val("InstallLocation") or get_val("InstallDir") or ""
                                version = get_val("DisplayVersion") or "unknown"
                                uninstall_str = get_val("UninstallString") or ""
                                publisher = get_val("Publisher") or ""

                                size = 0
                                if install_loc and os.path.exists(install_loc):
                                    size = self._get_dir_size(install_loc)

                                tool = DetectedTool(
                                    name=display_name,
                                    version=version,
                                    tool_type="Windows Program",
                                    path=install_loc or "Unknown",
                                    size_bytes=size,
                                    launch_cmd=install_loc if install_loc else "",
                                    uninstall_cmd=uninstall_str if uninstall_str else f"Windows Settings > Apps > {display_name}",
                                    description=f"Publisher: {publisher}" if publisher else "Windows installed program",
                                    files=[install_loc] if install_loc else [],
                                    confirmed=True
                                )
                                self.tool_found.emit(tool)
                        except Exception:
                            continue
            except Exception:
                continue

    def _scan_scoop(self):
        """Scan Scoop packages."""
        scoop_dir = os.path.join(os.path.expanduser("~"), "scoop", "apps")
        if not os.path.exists(scoop_dir):
            return

        for app_name in os.listdir(scoop_dir):
            if self._cancelled:
                break
            if not self._is_ai_related(app_name):
                continue

            app_path = os.path.join(scoop_dir, app_name)
            if not os.path.isdir(app_path):
                continue

            # Get current version dir
            versions = [d for d in os.listdir(app_path) if os.path.isdir(os.path.join(app_path, d))]
            version = versions[0] if versions else "unknown"

            size = self._get_dir_size(app_path)

            tool = DetectedTool(
                name=app_name,
                version=version,
                tool_type="Scoop Package",
                path=app_path,
                size_bytes=size,
                launch_cmd=f"scoop run {app_name}",
                uninstall_cmd=f"scoop uninstall {app_name}",
                description="Installed via Scoop",
                files=[app_path],
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_winget(self):
        """Scan WinGet packages."""
        output = self._safe_run(["winget", "list", "--accept-source-agreements"], timeout=30)
        if not output:
            return

        lines = output.strip().split("\n")
        for line in lines[2:]:  # Skip headers
            if self._cancelled:
                break
            parts = line.split()
            if len(parts) < 2:
                continue

            name = parts[0]
            if not self._is_ai_related(name):
                continue

            tool = DetectedTool(
                name=name,
                version=parts[1] if len(parts) > 1 else "unknown",
                tool_type="WinGet Package",
                path="Managed by WinGet",
                size_bytes=0,
                launch_cmd=f"winget run {name}",
                uninstall_cmd=f"winget uninstall {name}",
                description="Installed via WinGet",
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_brew(self):
        """Scan Homebrew packages."""
        # Formulae
        output = self._safe_run(["brew", "list", "--formula"], timeout=15)
        if output:
            for line in output.strip().split("\n"):
                if self._cancelled:
                    break
                name = line.strip()
                if not name or not self._is_ai_related(name):
                    continue

                # Get info
                info_output = self._safe_run(["brew", "info", "--json=v2", name], timeout=10)
                path = f"/usr/local/Cellar/{name}" if os.path.exists(f"/usr/local/Cellar/{name}") else f"/opt/homebrew/Cellar/{name}"
                version = "unknown"

                if info_output:
                    try:
                        data = json.loads(info_output)
                        if "formulae" in data and data["formulae"]:
                            version = data["formulae"][0].get("versions", {}).get("stable", "unknown")
                            path = data["formulae"][0].get("installed", [{}])[0].get("installed_as_dependency", path)
                    except Exception:
                        pass

                size = self._get_dir_size(path) if os.path.exists(path) else 0

                tool = DetectedTool(
                    name=name,
                    version=version,
                    tool_type="Homebrew Formula",
                    path=path,
                    size_bytes=size,
                    launch_cmd=f"brew run {name}" if os.path.exists("/usr/local/bin/" + name) or os.path.exists("/opt/homebrew/bin/" + name) else name,
                    uninstall_cmd=f"brew uninstall {name}",
                    description="Installed via Homebrew",
                    files=[path] if os.path.exists(path) else [],
                    confirmed=True
                )
                self.tool_found.emit(tool)

        # Casks
        output = self._safe_run(["brew", "list", "--cask"], timeout=15)
        if output:
            for line in output.strip().split("\n"):
                if self._cancelled:
                    break
                name = line.strip()
                if not name or not self._is_ai_related(name):
                    continue

                path = f"/Applications/{name}.app"
                if not os.path.exists(path):
                    path = f"~/Applications/{name}.app"

                tool = DetectedTool(
                    name=name,
                    version="unknown",
                    tool_type="Homebrew Cask",
                    path=path,
                    size_bytes=self._get_dir_size(path) if os.path.exists(path) else 0,
                    launch_cmd=f"open {path}" if os.path.exists(path) else name,
                    uninstall_cmd=f"brew uninstall --cask {name}",
                    description="Installed via Homebrew Cask",
                    files=[path] if os.path.exists(path) else [],
                    confirmed=True
                )
                self.tool_found.emit(tool)

    def _scan_macos_apps(self):
        """Scan macOS Applications folders."""
        app_dirs = ["/Applications", os.path.expanduser("~/Applications")]

        for app_dir in app_dirs:
            if not os.path.exists(app_dir):
                continue
            for entry in os.listdir(app_dir):
                if self._cancelled:
                    break
                if not entry.endswith(".app"):
                    continue

                name = entry[:-4]
                if not self._is_ai_related(name):
                    continue

                path = os.path.join(app_dir, entry)
                size = self._get_dir_size(path)

                tool = DetectedTool(
                    name=name,
                    version="unknown",
                    tool_type="macOS App",
                    path=path,
                    size_bytes=size,
                    launch_cmd=f'open "{path}"',
                    uninstall_cmd=f'rm -rf "{path}"',
                    description=f"macOS Application in {app_dir}",
                    files=[path],
                    confirmed=True
                )
                self.tool_found.emit(tool)

    def _scan_apt(self):
        """Scan APT packages on Linux."""
        output = self._safe_run(["dpkg", "-l"], timeout=20)
        if not output:
            return

        for line in output.strip().split("\n"):
            if self._cancelled:
                break
            if not line.startswith("ii"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            name = parts[1]
            version = parts[2] if len(parts) > 2 else "unknown"

            if not self._is_ai_related(name):
                continue

            # Get path info
            path_output = self._safe_run(["dpkg", "-L", name], timeout=10)
            files = []
            if path_output:
                files = [l.strip() for l in path_output.strip().split("\n") if l.strip().startswith("/")]

            tool = DetectedTool(
                name=name,
                version=version,
                tool_type="APT Package",
                path=files[0] if files else "/usr",
                size_bytes=0,
                launch_cmd=name,
                uninstall_cmd=f"sudo apt remove --purge {name}",
                description="Installed via APT",
                files=files[:10],
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_flatpak(self):
        """Scan Flatpak packages."""
        output = self._safe_run(["flatpak", "list", "--app"], timeout=15)
        if not output:
            return

        for line in output.strip().split("\n"):
            if self._cancelled:
                break
            parts = line.split("\t")
            if len(parts) < 3:
                continue

            name = parts[0]
            app_id = parts[1] if len(parts) > 1 else ""
            version = parts[2] if len(parts) > 2 else "unknown"

            if not self._is_ai_related(name) and not self._is_ai_related(app_id):
                continue

            tool = DetectedTool(
                name=name,
                version=version,
                tool_type="Flatpak",
                path=f"flatpak app: {app_id}",
                size_bytes=0,
                launch_cmd=f"flatpak run {app_id}",
                uninstall_cmd=f"flatpak uninstall {app_id}",
                description=f"Flatpak application ({app_id})",
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_snap(self):
        """Scan Snap packages."""
        output = self._safe_run(["snap", "list"], timeout=15)
        if not output:
            return

        for line in output.strip().split("\n")[1:]:
            if self._cancelled:
                break
            parts = line.split()
            if len(parts) < 1:
                continue

            name = parts[0]
            version = parts[1] if len(parts) > 1 else "unknown"

            if not self._is_ai_related(name):
                continue

            tool = DetectedTool(
                name=name,
                version=version,
                tool_type="Snap",
                path=f"/snap/{name}",
                size_bytes=0,
                launch_cmd=f"snap run {name}",
                uninstall_cmd=f"sudo snap remove {name}",
                description="Installed via Snap",
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_npm_global(self):
        """Scan globally installed NPM packages."""
        output = self._safe_run(["npm", "list", "-g", "--depth=0", "--json"], timeout=15)
        if not output:
            return

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return

        deps = data.get("dependencies", {})
        for name, info in deps.items():
            if self._cancelled:
                break
            if not self._is_ai_related(name):
                continue

            version = info.get("version", "unknown")
            path = info.get("path", "")

            size = self._get_dir_size(path) if path and os.path.exists(path) else 0

            tool = DetectedTool(
                name=name,
                version=version,
                tool_type="NPM Global",
                path=path or "Unknown",
                size_bytes=size,
                launch_cmd=f"npx {name}" if path else name,
                uninstall_cmd=f"npm uninstall -g {name}",
                description="Globally installed NPM package",
                files=[path] if path else [],
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_docker(self):
        """Scan Docker images."""
        output = self._safe_run(["docker", "images", "--format", "json"], timeout=15)
        if not output:
            return

        for line in output.strip().split("\n"):
            if self._cancelled:
                break
            try:
                image = json.loads(line)
            except json.JSONDecodeError:
                continue

            repo = image.get("Repository", "")
            tag = image.get("Tag", "")
            name = f"{repo}:{tag}" if tag else repo

            if not self._is_ai_related(repo):
                continue

            size_str = image.get("Size", "0B")
            # Parse size string like "1.23GB"
            size_bytes = 0
            try:
                size_val = float(re.match(r"[0-9.]+", size_str).group())
                if "GB" in size_str:
                    size_bytes = int(size_val * 1024**3)
                elif "MB" in size_str:
                    size_bytes = int(size_val * 1024**2)
                elif "KB" in size_str:
                    size_bytes = int(size_val * 1024)
            except Exception:
                pass

            tool = DetectedTool(
                name=name,
                version=tag or "latest",
                tool_type="Docker Image",
                path=f"docker image: {repo}",
                size_bytes=size_bytes,
                size_str=size_str,
                launch_cmd=f"docker run {name}",
                uninstall_cmd=f"docker rmi {image.get('ID', name)}",
                description=f"Docker image ({image.get('ID', '')})",
                confirmed=True
            )
            self.tool_found.emit(tool)

    def _scan_common_dirs(self):
        """Scan common installation directories for AI tools."""
        common_dirs = []

        if IS_WINDOWS:
            pf = os.environ.get("ProgramFiles", "C:\\Program Files")
            pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            local = os.environ.get("LOCALAPPDATA", "")
            roaming = os.environ.get("APPDATA", "")
            common_dirs = [
                pf, pf86, local, roaming,
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs"),
                "C:\\tools", "C:\\ProgramData",
            ]
        elif IS_MACOS:
            common_dirs = [
                "/usr/local", "/opt", "/opt/homebrew",
                os.path.expanduser("~/Applications"),
                os.path.expanduser("~/.local"),
            ]
        else:
            common_dirs = [
                "/opt", "/usr/local", "/usr/share",
                os.path.expanduser("~/.local"),
                os.path.expanduser("~/Applications"),
                "/var/lib",
            ]

        for base_dir in common_dirs:
            if not base_dir or not os.path.exists(base_dir):
                continue
            try:
                entries = os.listdir(base_dir)
            except Exception:
                continue

            for entry in entries:
                if self._cancelled:
                    break

                name = entry
                if not self._is_ai_related(name):
                    continue

                full_path = os.path.join(base_dir, entry)
                if not os.path.isdir(full_path):
                    continue

                # Skip if already found by other scanners
                size = self._get_dir_size(full_path)

                tool = DetectedTool(
                    name=name,
                    version="unknown",
                    tool_type="Directory",
                    path=full_path,
                    size_bytes=size,
                    launch_cmd=full_path,
                    uninstall_cmd=f"Remove directory: {full_path}",
                    description=f"Directory found in {base_dir}",
                    files=[full_path],
                    confirmed=True
                )
                self.tool_found.emit(tool)

    def _scan_vscode_extensions(self):
        """Scan VS Code and Cursor extensions."""
        ext_dirs = []

        if IS_WINDOWS:
            base = os.path.join(os.path.expanduser("~"), ".vscode", "extensions")
            cursor_base = os.path.join(os.path.expanduser("~"), ".cursor", "extensions")
            ext_dirs = [(base, "VS Code"), (cursor_base, "Cursor")]
        elif IS_MACOS:
            base = os.path.expanduser("~/.vscode/extensions")
            cursor_base = os.path.expanduser("~/.cursor/extensions")
            ext_dirs = [(base, "VS Code"), (cursor_base, "Cursor")]
        else:
            base = os.path.expanduser("~/.vscode/extensions")
            cursor_base = os.path.expanduser("~/.cursor/extensions")
            ext_dirs = [(base, "VS Code"), (cursor_base, "Cursor")]

        for ext_dir, editor in ext_dirs:
            if not os.path.exists(ext_dir):
                continue

            try:
                entries = os.listdir(ext_dir)
            except Exception:
                continue

            for entry in entries:
                if self._cancelled:
                    break

                # Extensions are named like publisher.name-version
                match = re.match(r"([^.]+\.[^-]+)-(.+)", entry)
                if not match:
                    continue

                ext_name = match.group(1)
                version = match.group(2)

                if not self._is_ai_related(ext_name):
                    continue

                full_path = os.path.join(ext_dir, entry)
                size = self._get_dir_size(full_path)

                tool = DetectedTool(
                    name=ext_name,
                    version=version,
                    tool_type=f"{editor} Extension",
                    path=full_path,
                    size_bytes=size,
                    launch_cmd=f"{editor.lower()}: extension installed",
                    uninstall_cmd=f"Remove directory: {full_path}",
                    description=f"{editor} extension",
                    files=[full_path],
                    confirmed=True
                )
                self.tool_found.emit(tool)


# =============================================================================
# TABLE MODEL
# =============================================================================

class ToolTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tools: List[DetectedTool] = []
        self.headers = ["Name", "Version", "Type", "Path", "Size", "Launch"]

    def set_tools(self, tools: List[DetectedTool]):
        self.beginResetModel()
        self.tools = tools
        self.endResetModel()

    def add_tool(self, tool: DetectedTool):
        # Check for duplicates by name+type
        for i, existing in enumerate(self.tools):
            if existing.name == tool.name and existing.tool_type == tool.tool_type:
                # Update if new one has more info
                if tool.size_bytes > existing.size_bytes:
                    self.tools[i] = tool
                    self.dataChanged.emit(self.index(i, 0), self.index(i, len(self.headers)-1))
                return

        row = len(self.tools)
        self.beginInsertRows(QModelIndex(), row, row)
        self.tools.append(tool)
        self.endInsertRows()

    def remove_tool(self, row: int):
        if 0 <= row < len(self.tools):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.tools[row]
            self.endRemoveRows()

    def get_tool(self, row: int) -> Optional[DetectedTool]:
        if 0 <= row < len(self.tools):
            return self.tools[row]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self.tools)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.tools):
            return None

        tool = self.tools[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return tool.name
            elif col == 1:
                return tool.version
            elif col == 2:
                return tool.tool_type
            elif col == 3:
                return tool.path[:60] + "..." if len(tool.path) > 60 else tool.path
            elif col == 4:
                return tool.size_str
            elif col == 5:
                return tool.launch_cmd[:50] + "..." if len(tool.launch_cmd) > 50 else tool.launch_cmd

        if role == Qt.ToolTipRole:
            return f"{tool.name}\n{tool.path}\n{tool.description}"

        if role == Qt.TextAlignmentRole:
            if col == 4:
                return Qt.AlignRight
            return Qt.AlignLeft

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        if column < 0 or column >= len(self.headers):
            return

        self.layoutAboutToBeChanged.emit()

        if column == 4:  # Size
            self.tools.sort(key=lambda x: x.size_bytes, reverse=(order == Qt.DescendingOrder))
        else:
            self.tools.sort(key=lambda x: str(self.data(self.index(self.tools.index(x), column), Qt.DisplayRole) or "").lower(),
                          reverse=(order == Qt.DescendingOrder))

        self.layoutChanged.emit()


# =============================================================================
# WORKER THREAD
# =============================================================================

class ScanWorker(QRunnable):
    def __init__(self, scanner: SystemScanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        self.scanner.run_scan()


# =============================================================================
# UNINSTALL DIALOG
# =============================================================================

class UninstallDialog(QDialog):
    def __init__(self, tool: DetectedTool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setWindowTitle(f"Uninstall {tool.name}")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Warning
        warn = QLabel("⚠️ WARNING: This action will remove the following from your system:")
        warn.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        layout.addWidget(warn)

        # Details
        form = QFormLayout()
        form.addRow("Name:", QLabel(tool.name))
        form.addRow("Type:", QLabel(tool.tool_type))
        form.addRow("Path:", QLabel(tool.path))
        form.addRow("Size:", QLabel(tool.size_str))
        form.addRow("Uninstall Command:", QLabel(tool.uninstall_cmd))
        layout.addLayout(form)

        # Files to remove
        if tool.files:
            layout.addWidget(QLabel("Files/Directories to be removed:"))
            list_widget = QListWidget()
            for f in tool.files:
                QListWidgetItem(f, list_widget)
            layout.addWidget(list_widget)

        # Confirmation
        self.confirm_check = QCheckBox("I understand this cannot be undone and want to proceed")
        layout.addWidget(self.confirm_check)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Ok).setText("Uninstall")
        buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.confirm_check.stateChanged.connect(
            lambda: buttons.button(QDialogButtonBox.Ok).setEnabled(self.confirm_check.isChecked())
        )
        layout.addWidget(buttons)


# =============================================================================
# MAIN WINDOW
# =============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Tool Manager - System Scanner & Uninstaller")
        self.setMinimumSize(1200, 800)

        self.tools: List[DetectedTool] = []
        self.scanner = SystemScanner()
        self.scanner.tool_found.connect(self._on_tool_found)
        self.scanner.progress.connect(self._on_progress)
        self.scanner.finished.connect(self._on_scan_finished)

        self._setup_ui()
        self._apply_styles()

        # Auto-scan on startup
        QTimer.singleShot(500, self.start_scan)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ===== TOP TOOLBAR =====
        toolbar = QHBoxLayout()

        self.scan_btn = QPushButton("🔍 Scan System")
        self.scan_btn.setMinimumHeight(36)
        self.scan_btn.clicked.connect(self.start_scan)
        toolbar.addWidget(self.scan_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(36)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        toolbar.addWidget(self.stop_btn)

        toolbar.addSpacing(20)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter tools...")
        self.filter_edit.setMinimumHeight(36)
        self.filter_edit.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.filter_edit, stretch=2)

        toolbar.addStretch()

        self.total_size_label = QLabel("Total: 0 B")
        self.total_size_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        toolbar.addWidget(self.total_size_label)

        main_layout.addLayout(toolbar)

        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(24)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        # ===== SPLITTER: TABLE + DETAILS =====
        splitter = QSplitter(Qt.Horizontal)

        # Left: Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.model = ToolTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # All columns

        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_double_click)

        left_layout.addWidget(self.table)

        # Quick action buttons below table
        btn_layout = QHBoxLayout()

        self.launch_btn = QPushButton("▶ Launch")
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self._launch_selected)
        btn_layout.addWidget(self.launch_btn)

        self.folder_btn = QPushButton("📁 Open Folder")
        self.folder_btn.setEnabled(False)
        self.folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.folder_btn)

        self.uninstall_btn = QPushButton("🗑 Uninstall")
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        self.uninstall_btn.clicked.connect(self._uninstall_selected)
        btn_layout.addWidget(self.uninstall_btn)

        btn_layout.addStretch()

        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        # Right: Details panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        details_title = QLabel("Tool Details")
        details_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(details_title)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumWidth(350)
        right_layout.addWidget(self.details_text)

        # Storage summary
        storage_group = QGroupBox("Storage Analysis")
        storage_layout = QVBoxLayout(storage_group)
        self.storage_tree = QTreeWidget()
        self.storage_tree.setHeaderLabels(["Category", "Count", "Size"])
        self.storage_tree.setColumnWidth(0, 150)
        storage_layout.addWidget(self.storage_tree)
        right_layout.addWidget(storage_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([750, 450])

        main_layout.addWidget(splitter, stretch=1)

        # ===== BOTTOM BAR =====
        bottom = QHBoxLayout()
        self.count_label = QLabel("Tools found: 0")
        bottom.addWidget(self.count_label)

        bottom.addStretch()

        platform_label = QLabel(f"Platform: {platform.system()} {platform.release()}")
        bottom.addWidget(platform_label)

        main_layout.addLayout(bottom)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', 'SF Pro', sans-serif;
                font-size: 13px;
            }
            QTableView {
                background-color: #313244;
                alternate-background-color: #2a2a3e;
                border: 1px solid #45475a;
                border-radius: 6px;
                gridline-color: #45475a;
                selection-background-color: #585b70;
                selection-color: #cdd6f4;
            }
            QTableView::item {
                padding: 6px;
                border-bottom: 1px solid #45475a;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #cdd6f4;
                padding: 8px;
                border: none;
                border-right: 1px solid #45475a;
                font-weight: bold;
            }
            QPushButton {
                background-color: #585b70;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #6c7086;
            }
            QPushButton:pressed {
                background-color: #45475a;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QTextEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px;
                color: #cdd6f4;
            }
            QProgressBar {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 6px;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTreeWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
            QTreeWidget::header {
                background-color: #181825;
                padding: 6px;
            }
            QListWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #45475a;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
            }
            QLabel {
                color: #cdd6f4;
            }
        """)

    def start_scan(self):
        self.model.set_tools([])
        self.tools = []
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning...")
        self.storage_tree.clear()

        worker = ScanWorker(self.scanner)
        QThreadPool.globalInstance().start(worker)

    def stop_scan(self):
        self.scanner.cancel()
        self.status_label.setText("Scan cancelled")
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_tool_found(self, tool: DetectedTool):
        self.model.add_tool(tool)
        self.tools = self.model.tools
        self._update_stats()

    def _on_progress(self, message: str, percent: int):
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)

    def _on_scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Scan complete. Found {len(self.tools)} AI-related tools.")
        self.progress_bar.setValue(100)
        self._update_stats()
        self._update_storage_tree()

    def _update_stats(self):
        total_size = sum(t.size_bytes for t in self.tools)
        self.total_size_label.setText(f"Total Size: {DetectedTool._format_size(total_size)}")
        self.count_label.setText(f"Tools found: {len(self.tools)}")

    def _update_storage_tree(self):
        self.storage_tree.clear()

        categories = {}
        for tool in self.tools:
            cat = tool.tool_type
            if cat not in categories:
                categories[cat] = {"count": 0, "size": 0}
            categories[cat]["count"] += 1
            categories[cat]["size"] += tool.size_bytes

        for cat, data in sorted(categories.items(), key=lambda x: x[1]["size"], reverse=True):
            item = QTreeWidgetItem(self.storage_tree)
            item.setText(0, cat)
            item.setText(1, str(data["count"]))
            item.setText(2, DetectedTool._format_size(data["size"]))
            item.setTextAlignment(1, Qt.AlignRight)
            item.setTextAlignment(2, Qt.AlignRight)

    def _apply_filter(self, text: str):
        self.proxy_model.setFilterFixedString(text)

    def _get_selected_tool(self) -> Optional[DetectedTool]:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        proxy_index = indexes[0]
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self.model.get_tool(source_index.row())

    def _on_selection_changed(self):
        tool = self._get_selected_tool()
        has_selection = tool is not None

        self.launch_btn.setEnabled(has_selection and bool(tool.launch_cmd))
        self.folder_btn.setEnabled(has_selection and tool.path and tool.path != "Unknown")
        self.uninstall_btn.setEnabled(has_selection)

        if tool:
            details = f"""
<b>Name:</b> {tool.name}<br>
<b>Version:</b> {tool.version}<br>
<b>Type:</b> {tool.tool_type}<br>
<b>Path:</b> {tool.path}<br>
<b>Size:</b> {tool.size_str}<br>
<b>Description:</b> {tool.description}<br><br>
<b>Launch Command:</b><br>
<code style="background:#181825;padding:4px;border-radius:4px;">{tool.launch_cmd or "N/A"}</code><br><br>
<b>Uninstall Command:</b><br>
<code style="background:#181825;padding:4px;border-radius:4px;">{tool.uninstall_cmd or "N/A"}</code><br><br>
<b>Files:</b><br>
{"<br>".join(tool.files) if tool.files else "None detected"}
"""
            self.details_text.setHtml(details)
        else:
            self.details_text.clear()

    def _on_double_click(self):
        self._launch_selected()

    def _show_context_menu(self, position):
        tool = self._get_selected_tool()
        if not tool:
            return

        menu = QMenu(self)

        launch_action = QAction("▶ Launch", self)
        launch_action.triggered.connect(self._launch_selected)
        menu.addAction(launch_action)

        folder_action = QAction("📁 Open Folder", self)
        folder_action.triggered.connect(self._open_folder)
        menu.addAction(folder_action)

        menu.addSeparator()

        copy_cmd = QAction("📋 Copy Launch Command", self)
        copy_cmd.triggered.connect(lambda: QApplication.clipboard().setText(tool.launch_cmd))
        menu.addAction(copy_cmd)

        copy_uninstall = QAction("📋 Copy Uninstall Command", self)
        copy_uninstall.triggered.connect(lambda: QApplication.clipboard().setText(tool.uninstall_cmd))
        menu.addAction(copy_uninstall)

        menu.addSeparator()

        uninstall_action = QAction("🗑 Uninstall", self)
        uninstall_action.triggered.connect(self._uninstall_selected)
        menu.addAction(uninstall_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _launch_selected(self):
        tool = self._get_selected_tool()
        if not tool or not tool.launch_cmd:
            return

        try:
            if IS_WINDOWS:
                subprocess.Popen(tool.launch_cmd, shell=True)
            else:
                subprocess.Popen(tool.launch_cmd, shell=True, 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status_label.setText(f"Launched: {tool.name}")
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch: {str(e)}")

    def _open_folder(self):
        tool = self._get_selected_tool()
        if not tool or not tool.path or tool.path == "Unknown":
            return

        path = tool.path
        if os.path.isfile(path):
            path = os.path.dirname(path)

        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "Not Found", f"Path does not exist: {path}")

    def _uninstall_selected(self):
        tool = self._get_selected_tool()
        if not tool:
            return

        dialog = UninstallDialog(tool, self)
        if dialog.exec() != QDialog.Accepted:
            return

        self.status_label.setText(f"Uninstalling {tool.name}...")

        try:
            success = self._perform_uninstall(tool)
            if success:
                # Remove from model
                indexes = self.table.selectionModel().selectedRows()
                if indexes:
                    proxy_index = indexes[0]
                    source_index = self.proxy_model.mapToSource(proxy_index)
                    self.model.remove_tool(source_index.row())
                    self.tools = self.model.tools

                self._update_stats()
                self._update_storage_tree()
                self.status_label.setText(f"Uninstalled: {tool.name}")
                QMessageBox.information(self, "Success", f"{tool.name} has been removed successfully.")
            else:
                QMessageBox.warning(self, "Partial Success", 
                    "Some components may not have been fully removed. Check details panel for manual commands.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Uninstall failed: {str(e)}\n\n{traceback.format_exc()}")

    def _perform_uninstall(self, tool: DetectedTool) -> bool:
        """Execute uninstallation logic."""
        success = True

        # 1. Run uninstall command if it's a known package manager command
        if tool.uninstall_cmd:
            if tool.tool_type in ["Python Package", "NPM Global", "Homebrew Formula", 
                                  "Homebrew Cask", "Scoop Package", "APT Package",
                                  "Flatpak", "Snap", "WinGet Package"]:
                try:
                    result = subprocess.run(
                        tool.uninstall_cmd, shell=True, capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        print(f"Uninstall command failed: {result.stderr}")
                        success = False
                except Exception as e:
                    print(f"Error running uninstall: {e}")
                    success = False

        # 2. Remove files/directories
        for file_path in tool.files:
            if not os.path.exists(file_path):
                continue
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
                success = False

        # 3. If path is a directory and still exists, try removing it
        if tool.path and os.path.exists(tool.path) and tool.path != "Unknown":
            try:
                if os.path.isdir(tool.path):
                    shutil.rmtree(tool.path)
                else:
                    os.remove(tool.path)
            except Exception:
                pass

        return success

    def closeEvent(self, event):
        self.scanner.cancel()
        event.accept()


# =============================================================================
# ENTRY POINT
# =============================================================================

from PySide6.QtCore import QUrl

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI Tool Manager")
    app.setOrganizationName("AIToolManager")

    # Set application font
    font = QFont("Segoe UI", 10)
    if IS_MACOS:
        font = QFont("SF Pro", 11)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
