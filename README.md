# 🧹 AIDeclutter

> **Reclaim your system from AI bloat – one click at a time.**

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📖 Overview

**AIDeclutter** is a cross-platform desktop application that gives you a single, unified view of every AI/ML tool installed on your machine.

It scans Python packages, PATH executables, Docker images, Homebrew formulas, APT/Snap/Flatpak packages, NPM globals, Windows Registry entries, VS Code/Cursor extensions, and common install directories—then displays everything in a sortable table with real disk usage, paths, versions, and launch commands.

With one click you can:

- 🚀 Launch a tool
- 📂 Open its folder
- 📋 Copy its uninstall command
- 🗑️ Safely remove it (delegating to the native package manager or deleting orphaned files)

> **Stop guessing what's installed and where — see everything at a glance and clean with confidence.**

---

# ✨ Features

- 🔍 **Comprehensive Scanning**
  - Detects AI tools across **15+ sources** (pip, conda, brew, apt, snap, flatpak, docker, npm, Windows Registry, and more).

- 📊 **Rich Table View**
  - Displays name, version, type, install path, total size, and launch command for each tool.

- 🗑️ **Safe Uninstallation**
  - Shows exactly what will be removed.
  - Confirms before deletion.
  - Uses native package managers whenever possible.

- 🚀 **Quick Actions**
  - Launch a tool
  - Open its folder
  - Copy any command
  - Right-click context menu

- 📈 **Storage Analysis**
  - See which categories (Python, containers, formulae, etc.) consume the most space.

- 🎨 **Modern UI**
  - Dark-themed
  - Responsive
  - Built with **PySide6**

- ⚡ **Asynchronous Scanning**
  - Background scanning keeps the UI responsive.

- 🔎 **Live Filtering**
  - Narrow results instantly as you type.

- 🌐 **Cross-Platform**
  - Works on **Windows**, **macOS**, and **Linux**.

---

# 🖥️ Supported Platforms & Sources

| Platform | Detection Sources |
|----------|-------------------|
| **Windows** | Python packages, PATH executables, Windows Registry, Scoop, WinGet, VS Code extensions, common directories (`Program Files`, `AppData`, etc.) |
| **macOS** | Python packages, PATH executables, Homebrew (formulae & casks), macOS Applications folder, VS Code/Cursor extensions |
| **Linux** | Python packages, PATH executables, APT, Flatpak, Snap, NPM global packages, Docker images, common directories (`/opt`, `/usr/local`, `~/.local`) |

---

# 📦 Requirements

- Python **3.8** or newer
- **PySide6** *(installed automatically via pip — see below)*
- Uses only the Python standard library for system interactions

---

# 🚀 Installation & Usage

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/AIDeclutter.git
cd AIDeclutter
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, simply run:

```bash
pip install pyside6
```

---

## 3️⃣ Run the Application

```bash
python aideclutter.py
```

On first launch, the application automatically begins scanning your system.

The scan runs in the background, allowing you to interact with the interface immediately.

---

# 🛠️ How It Works

AIDeclutter matches tool names against a curated list of AI/ML keywords, including:

- `torch`
- `ollama`
- `tensorflow`
- `transformers`
- `docker`
- `llama`
- ...and many more.

For every detected item, AIDeclutter:

1. Determines the installation path and calculates its total size on disk.
2. Extracts the version (when available).
3. Identifies the appropriate launch and uninstall commands.
4. Groups the tool into a category (Python Package, Homebrew Formula, Docker Image, etc.).

> **The scan is completely non-invasive.**
>
> It only reads file metadata and package lists. Your system is **never modified** unless you explicitly confirm an uninstallation.

---

# 🗑️ Uninstallation Process

When you select a tool and click **Uninstall**:

1. A **confirmation dialog** appears listing:
   - Every file and directory that will be removed
   - The exact uninstall command

2. You must check the confirmation box before continuing.

3. If the tool is managed by a package manager (pip, brew, apt, winget, etc.), AIDeclutter executes that package manager's uninstall command.

4. Any leftover files or directories associated with the tool are removed.

5. A success message is displayed after completion.

> ⚠️ **Important**
>
> Uninstallation is **never automatic**. Every removal requires explicit user approval.

---

# 🎮 Usage Guide

### 🔍 Scanning

Click the **🔍 Scan System** button anytime to perform a fresh scan.

---

### 🔎 Filtering

Type into the filter bar to instantly show only tools whose:

- Name
- Type
- Path

contain your search text.

---

### 📊 Sorting

Click any table column header to sort by that attribute.

Examples:

- Size
- Name
- Version
- Type

---

### 📄 Selection

Click a row to display detailed information in the right-hand panel.

---

### 🚀 Actions

Right-click any row to access:

- Launch
- Open Folder
- Copy Commands
- Uninstall

---

### ▶ Launch

Double-click a row or select one and press the **▶ Launch** button.

---

### 🗑 Uninstall

Select a tool and click **🗑 Uninstall**.

The application guides you through the confirmation process before anything is removed.

---

# 📁 Repository Structure

```text
AIDeclutter/
├── aideclutter.py          # Main application script
├── README.md               # This file
├── LICENSE                 # MIT License
└── requirements.txt        # Dependencies (PySide6)
```

---

# 🤝 Contributing

Contributions are welcome!

Whether it's:

- Adding support for new package managers
- Improving the UI
- Fixing bugs

please open an issue or submit a pull request.

### Guidelines

- Keep the code compatible with **Python 3.8+**
- Follow **PEP 8**
- Test on at least one platform before submitting
- Update the README when adding new features

---

# ❓ FAQ

### Q: The scan found a tool I don't want to remove — is it safe to leave it?

**A:** Yes.

The application only displays what it finds. You remain in full control of what gets removed.

---

### Q: Can I use this to only scan without removing anything?

**A:** Absolutely.

You can scan, browse, filter, and copy commands without making any changes to your system.

---

### Q: Why is the uninstall command disabled for some items?

**A:** For plain executables or unmanaged folders, the uninstall action still deletes the file or directory directly.

The button remains enabled as long as a tool is selected.

---

### Q: Does it support Conda environments?

**A:** Currently it scans pip packages, but Conda environments are not yet detected.

This feature is planned for a future release.

---

### Q: How can I add more AI keywords?

**A:** Edit the `AI_KEYWORDS` list near the top of the script.

---

# 🔧 Troubleshooting

### Missing PySide6

Install it with:

```bash
pip install pyside6
```

---

### Scan hangs or takes too long

The scanner includes built-in timeouts.

You can also click the **Stop** button to cancel the scan.

---

### Permission errors during uninstall

Run the application with administrator or root privileges if necessary.

---

# 📄 License

This project is licensed under the **MIT License**.

See the **LICENSE** file for details.

---

# 📧 Contact & Support

For questions, suggestions, or bug reports, please open an issue on GitHub:

https://github.com/yourusername/AIDeclutter/issues

---

<div align="center">

## 🧹 Take control. Declutter with confidence.

### **AIDeclutter**
### *The AI environment cleaner you didn't know you needed.*

</div>
