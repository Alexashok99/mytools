# 🛠️ MyTools - Developer's Swiss Army Knife

<p align="center">
  <img src="https://img.shields.io/pypi/v/mytools?color=blue&style=flat-square" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/mytools?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/github/license/yourusername/mytools?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/yourusername/mytools?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/github/issues/yourusername/mytools?style=flat-square" alt="Issues">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome">
</p>

<p align="center">
  <b>A powerful collection of CLI tools for Python developers</b><br>
  Clean cache, manage Django projects, handle virtual environments, and more - all in one place!
</p>

---

## ✨ Features

| 🧹 **Clean Python Cache** | Remove all `__pycache__` folders recursively with space calculation |
|---------------------------|---------------------------------------------------------------------|
| 🚀 **Django Manager** | Create projects, apps, run migrations and server interactively |
| 🐍 **Environment Manager** | Create/delete virtual environments, manage `.env` files |
| 📁 **File Operations** | Copy, move, delete, and list files with beautiful output |
| 📊 **File Statistics** | Count files by extension, analyze project structure |
| 📄 **AI Context Generator** | Generate optimized project context for AI assistants |

---

## 🚀 Quick Installation

### **Install from PyPI (Recommended)**
```bash
pip install mytools
```

### **Install from GitHub**
```bash
pip install git+https://github.com/Alexashok99/mytools.git
```

### **Development Installation**
```bash
git clone https://github.com/Alexashok99/mytools.git
cd mytools
pip install -e .
```

---

## 🎮 Basic Usage

### **See all available tools**
```bash
$ mytools list
🔧 Available tools:
  • clean-pycache – Remove all __pycache__ folders recursively
  • django – Interactive Django project manager
  • env – Virtual environment and .env helper
  ...
```

### **Get help**
```bash
mytools --help
mytools clean-pycache --help
```

### **Clean Python cache**
```bash
cd your-project-directory
mytools clean-pycache
```
```
🔍 Cleaning in: E:\projects\myproject
✅ Deleted: __pycache__ (1.25 MB)
✅ Deleted: src\__pycache__ (0.50 MB)
🎯 Summary: 2 folders deleted, 1.75 MB freed
```

### **Start Django manager**
```bash
mytools django
```
```
DJANGO MANAGER
1. Create Django Project
2. Check Django Installation
3. Create Django App
...
```

---

## 📚 Detailed Documentation

### Plugins & Extensions

MyTools is designed to be extendable. Third‑party or custom tools can be
registered using [Python entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
under the `mytools.plugins` group. The package dynamically loads every
tool listed there when it starts.

There is also a `src/mytools/plugins/` package included for convenience —
it's empty by default but you may drop local plugin modules in there
and add corresponding entry points during development.

---

### 🧹 **Clean Python Cache**
Removes all `__pycache__` directories recursively from current path.

```bash
mytools clean-pycache --yes          # skip confirmation prompt
mytools clean-pycache --no-pause     # run without waiting at end
```

```bash
mytools clean-pycache
```
- Shows folder size before deletion
- Displays total space freed
- Safe - asks for confirmation

### 🚀 **Django Manager**
Interactive Django project and app management.

```bash
mytools django
```
**Features:**
- Create new Django projects
- Check Django installation
- Create Django apps
- Make and apply migrations
- Run development server

### 🐍 **Environment Manager**
Virtual environment and `.env` file management.

```bash
mytools env
```
**Features:**
- Create virtual environments (.venv, venv, custom)
- Delete virtual environments
- Create `.env` file with templates
- Delete `.env` files
- List environment variables
- Check Python environment

### 📁 **File Operations**
Comprehensive file and folder management.

```bash
mytools file-ops
```
**Features:**
- List all files with sizes
- Copy files/folders
- Move files/folders
- Delete files/folders
- File information
- Create folders and files
- Export file lists

### 📊 **File Statistics**
Analyze your project structure.

```bash
mytools file-counter
```
**Output:**
```
📁 Project: myproject
📍 Path: E:/projects/myproject

📈 Statistics:
   • Total folders: 42
   • Total files: 156

📄 Files by extension:
   • .py: 89
   • .md: 23
   • .json: 12
   • .txt: 8
   • .yml: 5
   • [no extension]: 19
```

### 📄 **AI Context Generator**
Generate optimized context for AI assistants.

```bash
mytools context
```
**Features:**
- Smart file selection (prioritizes important files)
- Custom ignore patterns
- Project tree visualization
- File content extraction
- Size limits to prevent overflow

---

## ⚙️ Configuration

Create `.env` file in your project directory:

```env
# MyTools Configuration
MYTOOLS_LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
MYTOOLS_MAX_FILE_SIZE=100000    # Max file size to read (bytes)
MYTOOLS_MAX_TOTAL_SIZE=500000   # Max total context size (bytes)
```

Or set environment variables directly:

```bash
# Windows
set MYTOOLS_LOG_LEVEL=DEBUG

# Linux/Mac
export MYTOOLS_LOG_LEVEL=DEBUG
```

---

## 🧪 Development Setup

```bash
# Clone repository
git clone https://github.com/Alexashok99/mytools.git
cd mytools

# Create virtual environment
python -m venv .venv
# Activate it:
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest tests/ --cov=mytools

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

---

## 📁 Project Structure

```
mytools/
├── src/
│   └── mytools/
│       ├── __init__.py          # Package version
│       ├── __main__.py          # python -m support
│       ├── cli.py              # Typer CLI application
│       ├── config.py           # Pydantic settings
│       ├── utils.py            # Helper functions
│       └── tools/              # All CLI tools
│           ├── base.py         # BaseTool abstract class
│           ├── clean_pycache.py
│           ├── django_manager.py
│           ├── env_manager.py
│           ├── file_ops.py
│           ├── file_counter.py
│           └── context_generator.py
├── tests/                      # Unit tests
│   ├── test_cli.py
│   └── test_tools/
├── pyproject.toml             # Package configuration
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **🐛 Report bugs** - Open an issue
2. **✨ Suggest features** - Open an issue with `enhancement` tag
3. **📝 Improve docs** - Fix typos, add examples
4. **🔧 Submit PRs** - Fix bugs, add features

**Development workflow:**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Use Black formatter
- Run Ruff linter

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@Alexashok99](https://github.com/Alexashok99)
- Email: alexashok999@gmail.com

---

## ⭐ Support

If you find this project useful, please consider:

- Giving a ⭐ star on GitHub
- 📤 Sharing with fellow developers
- 🐛 Reporting issues
- 🔧 Contributing code

---

<p align="center">
  Made with ❤️ for Python developers
</p>