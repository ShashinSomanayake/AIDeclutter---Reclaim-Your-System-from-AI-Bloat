```markdown
# AIDeclutter

**AI Tool Manager** is a cross-platform desktop application that scans your system for installed AI/ML tools, displays their paths, sizes, and launch commands, and provides a safe, user‑friendly interface to uninstall them.

It helps you reclaim disk space, understand what AI tools are installed, and manage your development environment with ease.

![Screenshot Placeholder](screenshot.png)

---

## ✨ Features

- 🔍 **Comprehensive Scanning** – Detects AI tools across multiple package managers, runtimes, and directories.
- 📊 **Detailed View** – Displays name, version, type, install path, total size, and launch command for each tool.
- 🗑️ **Safe Uninstallation** – Removes packages via native package managers or by deleting files; requires explicit confirmation.
- 📂 **Quick Actions** – Launch a tool, open its folder, or copy uninstall commands with a right‑click.
- 📈 **Storage Analysis** – Shows how much space each category (Python packages, Docker images, Homebrew formulas, etc.) consumes.
- 🎨 **Modern UI** – Built with PySide6, featuring a dark theme and responsive layout.
- ⚡ **Fast & Asynchronous** – Scanning runs in the background so the UI stays responsive.
- 🔎 **Live Filtering** – Quickly narrow down results by typing in the filter bar.

---

## 🖥️ Supported Platforms

- **Windows** – Detects Python packages, executables, Windows Registry, Scoop, WinGet, VS Code extensions, and common directories.
- **macOS** – Detects Python packages, executables, Homebrew (formulae & casks), macOS applications, and VS Code extensions.
- **Linux** – Detects Python packages, executables, APT, Flatpak, Snap, NPM global, Docker, and common directories.

---

## 📦 Requirements

- Python 3.8 or newer
- [PySide6](https://pypi.org/project/PySide6/) (installed automatically via pip)

The script uses only the standard library aside from PySide6.

---

## 🚀 Installation & Usage

### 1. Clone the repository or download the script

```bash
git clone https://github.com/yourusername/ai-tool-manager.git
cd ai-tool-manager
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, just run:

```bash
pip install pyside6
```

### 3. Run the application

```bash
python ai_tool_manager.py
```

On first launch, it will automatically start scanning your system. The scan runs in the background and you can use the interface immediately.

---

## 🛠️ How It Works

The scanner looks for AI‑related tools by matching names against a large list of known AI/ML keywords (e.g., `torch`, `ollama`, `tensorflow`, `vllm`, `transformers`, `docker`, etc.).

### Detection Sources

| Source | Description |
|--------|-------------|
| **Python packages** | Installed via `pip`, read from site‑packages. |
| **PATH executables** | Any executable in your `PATH` that matches AI keywords. |
| **Windows Registry** | Installed programs with AI‑related names. |
| **Homebrew** | Formulae and casks on macOS. |
| **APT / Flatpak / Snap** | Linux package managers. |
| **NPM global** | Globally installed Node.js packages. |
| **Docker images** | Local Docker images with AI‑related repository names. |
| **Common directories** | Scans `/opt`, `/usr/local`, `~/Applications`, etc. |
| **VS Code / Cursor extensions** | Extensions from AI‑related publishers. |

---

## 🗑️ Uninstallation

When you select a tool and click **Uninstall**, the application will:

1. Show a confirmation dialog listing all files/directories to be removed.
2. Run the native uninstall command (e.g., `pip uninstall`, `brew uninstall`, `winget uninstall`) if applicable.
3. Delete any leftover files/directories associated with the tool.

> **Note:** Some tools may not support full automated removal. In such cases, the dialog provides the exact command you can run manually.

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start scan | `Ctrl + S` (not implemented, but button available) |
| Launch selected | `Enter` (double‑click) |
| Open folder | `Ctrl + O` (context menu) |

---

## 📁 Repository Structure

```
ai-tool-manager/
├── ai_tool_manager.py   # Main application script
├── README.md            # This file
├── LICENSE              # MIT License
└── requirements.txt     # Dependencies (PySide6)
```

---

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to add support for more package managers, please open an issue or submit a pull request.

**Guidelines**:
- Keep the code compatible with Python 3.8+.
- Follow the existing style.
- Test on at least one platform before submitting.

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## ❓ FAQ

**Q: The scan found a tool that I don't want to remove. Is it safe?**  
A: Yes, the tool only lists what it finds; uninstallation requires your explicit confirmation.

**Q: Can I scan without uninstalling?**  
A: Absolutely. The scan runs automatically on startup, and you can use the filter, view details, and copy commands without any risk.

**Q: Does it support other AI tools?**  
A: The keyword list is extensive but not exhaustive. You can edit `AI_KEYWORDS` in the script to add your own terms.

**Q: Why is the uninstall command disabled for some items?**  
A: For tools that are not managed by a known package manager (e.g., plain executables), the uninstall command is "Remove file: <path>". The application will still attempt to delete the file if you confirm, but it cannot use a package manager to do so.

---

## 🔧 Troubleshooting

- **Missing PySide6**: Run `pip install pyside6`.
- **Scan hangs or takes too long**: The scanner has timeouts on subprocesses. You can also click **Stop** to cancel.
- **Permission errors during uninstall**: Run the application with administrator/root privileges if needed.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

*Happy cleaning!* 🧹
```
