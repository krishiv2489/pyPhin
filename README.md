<div align="center">

```
██████╗ ██╗   ██╗██████╗ ██╗  ██╗██╗███╗   ██╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██║  ██║██║████╗  ██║
██████╔╝ ╚████╔╝ ██████╔╝███████║██║██╔██╗ ██║
██╔═══╝   ╚██╔╝  ██╔═══╝ ██╔══██║██║██║╚██╗██║
██║        ██║   ██║     ██║  ██║██║██║ ╚████║
╚═╝        ╚═╝   ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
```

**A minimal, keyboard-driven file explorer for the terminal.**  
_Built with Python and Textual — fast, clean, no bloat._

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Textual](https://img.shields.io/badge/Textual-TUI-purple?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/pyphin?style=flat-square&color=b4befe)

</div>

---

## What is pyPhin?

pyPhin is a terminal-based file explorer built with Python. It follows the philosophy that a file manager should stay out of your way — no mouse required, no heavy dependencies, just keyboard bindings and a clean two-panel layout. The left panel shows the current directory and the right panel previews whatever is highlighted, giving you instant context as you move through your filesystem.

It is designed to be readable as a codebase too — a learning project that doesn't hide complexity behind abstractions, making it easy to extend and modify.

---

## Screenshots

| Main View                          | Properties Panel                          |
| ---------------------------------- | ----------------------------------------- |
| ![Main View](screenshots/main.png) | ![Properties](screenshots/properties.png) |

---

## Features

- **Two-panel layout** — directory tree on the left, live preview on the right
- **Instant preview** — right panel updates as you highlight items, powered by background worker threads so the UI never freezes
- **File metadata** — press `a` to inspect any file or folder: size, path, permissions, timestamps
- **Recursive folder size** — actual disk usage calculated for directories, not just the entry size
- **Permission display** — Unix-style permission strings (`drwxr-xr-x`) for every entry
- **Keyboard-first** — everything reachable without touching the mouse
- **Error handling** — permission denied, unreadable directories, and empty folders are all handled gracefully
- **Hidden file filtering** — dotfiles are hidden by default, keeping the view clean
- **Capped directory reads** — limits entries to 1000 per folder to keep I/O fast even in massive directories

---

## Keybindings

| Key | Action                        |
| --- | ----------------------------- |
| `s` | Enter highlighted directory   |
| `w` | Go up to parent directory     |
| `a` | Show file / folder properties |
| `q` | Quit                          |

---

## Installation

pyPhin requires **Python 3.10 or higher**. Pick the method that matches your system below.

---

### Ubuntu / Debian / Linux Mint

The recommended way on Debian-based systems is `pipx`, which automatically manages an isolated environment for CLI tools so it never conflicts with your system Python.

```bash
sudo apt install pipx
pipx install pyphin
pyphin
```

If you don't want to use `pipx`, you can install directly with pip — just be aware this goes into your system Python:

```bash
pip install pyphin
```

---

### Arch Linux / EndeavourOS / Manjaro

Arch marks its system Python as externally managed (PEP 668), meaning plain `pip install` will be blocked by default. The cleanest solution is `pipx`, which is available directly from pacman:

```bash
sudo pacman -S python-pipx
pipx install pyphin
pyphin
```

If you prefer pip and understand the risk of bypassing the system protection:

```bash
pip install pyphin --break-system-packages
```

---

### Fedora / RHEL / CentOS

```bash
pip install pyphin
```

If pip is blocked on your system:

```bash
pipx install pyphin
```

---

### macOS

macOS ships with a system Python that should not be touched. Use `pipx` via Homebrew:

```bash
brew install pipx
pipx install pyphin
pyphin
```

---

### Termux (Android)

pyPhin works on Termux since Textual renders correctly in its terminal emulator. Make sure your Termux is up to date first:

```bash
pkg update && pkg upgrade
pkg install python
pip install pyphin
pyphin
```

> Note: Folder size calculation (`a` key) may be slower on Termux for large directories since Android storage I/O is slower than desktop Linux. Everything else works normally.

---

### Windows (WSL)

pyPhin is currently Linux-only. The recommended way to run it on Windows is through WSL (Windows Subsystem for Linux). Once you have a WSL distribution set up, follow the Ubuntu instructions above inside your WSL terminal.

Native Windows support is on the roadmap.

---

### Manual Installation from Source

If you want to run the latest development version directly from the repository, or want to contribute to the project:

```bash
# 1. Clone the repository
git clone https://github.com/krishiv2489/pyPhin.git
cd pyPhin

# 2. Create an isolated virtual environment (keeps your system Python clean)
python -m venv .venv
source .venv/bin/activate

# 3. Install in editable mode — changes to the source are reflected immediately
pip install -e .

# 4. Run
pyphin
```

Editable mode (`-e`) is useful for development because you can edit `main.py` or `pyath.py` and the changes take effect the next time you run `pyphin` without reinstalling.

---

## Project Structure

```
pyPhin/
├── pyphin/
│   ├── __init__.py       # Package init
│   ├── main.py           # Textual app, UI logic, keybindings
│   ├── pyath.py          # Backend: path traversal, metadata, filesystem ops
│   └── file.tcss         # Textual CSS — layout and styling
├── pyproject.toml        # Build config and entry point
├── LICENSE
└── README.md
```

The project is intentionally split into two layers. `pyath.py` is pure filesystem logic with no UI knowledge — it can be tested or run in isolation. `main.py` is pure UI that calls into `pyath.py` and never does filesystem work directly. Keeping these two concerns separate is what makes the codebase easy to extend.

---

## How It Works

pyPhin uses **Textual worker threads** to keep the UI responsive. When you navigate into a folder or request metadata, the work is dispatched to a background thread via `@work(thread=True)`. The result is sent back to the main thread through Textual's `Worker.StateChanged` event, which then updates the panel. This means a slow filesystem or a large directory will never cause the interface to freeze or drop inputs.

The backend uses only Python's standard library — `pathlib` for cross-platform path handling, `stat` for permission formatting, and `datetime` for human-readable timestamps. No third-party filesystem libraries.

---

## Roadmap

These are features planned or under consideration:

- [ ] File preview — render the first N lines of text files in the right panel
- [ ] Hidden file toggle — press `h` to show/hide dotfiles
- [ ] Search and filter — filter the left panel by filename in real time
- [ ] Bookmarks — save and jump to favourite paths
- [ ] Sort modes — cycle between name, size, and modified date ordering
- [ ] Rename and delete — with a confirmation modal
- [ ] Windows support — native support without WSL

---

## Contributing

Contributions are welcome. If you have a bug fix, feature idea, or improvement to the code structure, feel free to open an issue or a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a pull request

Please keep the two-layer architecture intact — filesystem logic stays in `pyath.py`, UI logic stays in `main.py`.

---

## Author

**Krishiv Patel**  
GitHub: [@krishiv2489](https://github.com/krishiv2489)

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.

---

<div align="center">
<sub>Built with Python · Powered by Textual · Made for the terminal</sub>
</div>
