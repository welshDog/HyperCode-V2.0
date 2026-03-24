# 🚀 HyperCode: Professional Setup Guide (Enhanced)

## Production-Ready Development Environment Setup

**Last Updated**: November 11, 2025 **Status**: ✅ Professional Grade **Target**: All
operating systems (Windows, macOS, Linux)

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.10+** → [Download](https://www.python.org/downloads/)
- **Git 2.30+** → [Download](https://git-scm.com/)
- **Terminal/Command Prompt** (built-in on all systems)
- **Text editor or IDE** (VS Code, PyCharm, etc.)

**Verify installation:**

```bash
python --version    # Should output: Python 3.10+
git --version       # Should output: git version 2.30+
pip --version       # Should output: pip version X.X.X
```

---

## 🎯 Step 1: Clone the Repository

```bash
# Clone your HyperCode repository
git clone https://github.com/welshDog/hypercode.git

# Navigate into the project directory
cd hypercode

# Verify you're in the right place
pwd  # Unix/Mac: shows /path/to/hypercode
# or
cd   # Windows: shows C:\path\to\hypercode
```

---

## 🔧 Step 2: Setup Local Environment (Virtual Environment)

**Why**: Virtual environments isolate project dependencies and prevent conflicts with
system Python.

### 2.1 Create Virtual Environment

```bash
# Create a new virtual environment named .venv
python -m venv .venv
```

**What this does:**

- Creates a `.venv/` directory containing an isolated Python installation
- Includes pip and setuptools pre-installed
- All packages you install will be local to this project

### 2.2 Activate Virtual Environment

**Windows (Command Prompt):**

```bash
.venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash/Zsh):**

```bash
source .venv/bin/activate
```

**Verify activation:** Your terminal prompt should now show `(.venv)` prefix:

```
(.venv) user@machine:~/hypercode $
```

✅ **You're in the virtual environment!**

---

## 🏗️ Step 3: Automated Project Scaffolding

Instead of manually creating directories, use the automated scaffolder.

### 3.1 Run the Scaffolder Script

```bash
# Make sure you're in the hypercode directory
cd hypercode

# Run the scaffolder (cross-platform compatible)
python scaffold.py
```

**Expected output:**

```
🚀 HyperCode Project Scaffolder
============================================================

📁 Creating directories...
   ✓ core/
   ✓ backends/
   ✓ ai_gateway/
   [... more directories ...]

📝 Creating Python files...
   ✓ core/__init__.py
   ✓ core/lexer.py
   [... more files ...]

📚 Creating example programs...
   ✓ examples/hello_world.hc
   ✓ examples/fibonacci.hc

⚙️  Creating root configuration files...
   ✓ Dockerfile
   ✓ requirements.txt
   [... more files ...]

🏥 Creating healthcheck script...
   ✓ healthcheck.sh

============================================================
✅ PROJECT STRUCTURE CREATED SUCCESSFULLY!
============================================================
```

### 3.2 Verify Project Structure

```bash
# List directories (Unix/Mac/PowerShell)
ls -la

# List directories (Windows cmd)
dir

# You should see:
# core/
# backends/
# ai_gateway/
# accessibility/
# tests/
# examples/
# docs/
# .github/
# requirements.txt
# setup.py
# Dockerfile
# ... and more
```

✅ **Project structure is ready!**

---

## 📦 Step 4: Install Dependencies and Tools

### 4.1 Install Python Packages (Production)

```bash
# Install production dependencies
pip install -r requirements.txt

# Expected: "Successfully installed X packages"
```

### 4.2 Install Development Tools

```bash
# Install all development + testing tools
pip install -r requirements-dev.txt

# This includes:
# - pytest (testing)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
# - pre-commit (git hooks)
```

### 4.3 Verify Installation

```bash
# Check key packages
pip list | grep -E "pytest|black|flake8|mypy|pre-commit"

# Expected output:
# black                          23.12.1
# flake8                         6.1.0
# mypy                           1.7.1
# pre-commit                     3.5.0
# pytest                         7.4.3
```

✅ **All dependencies installed!**

---

## 🔗 Step 5: Setup Git Hooks (Pre-commit)

Pre-commit hooks automatically run code quality checks before each commit, preventing
bad code from being committed.

### 5.1 Install Pre-commit Hooks

```bash
# Install the git hooks
pre-commit install

# Expected output:
# pre-commit installed at .git/hooks/pre-commit
```

### 5.2 Test Pre-commit Hooks

```bash
# Run hooks on all files (optional, for testing)
pre-commit run --all-files

# This will:
# - Format code with black
# - Check linting with flake8
# - Validate types with mypy
# - Check YAML/JSON syntax
# - Run security scan with bandit
```

✅ **Git hooks are active!**

---

## ⚙️ Step 6: Configure Environment Variables

### 6.1 Create .env File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

### 6.2 Fill in Your Secrets

Open `.env` and add:

```
# OpenAI
OPENAI_API_KEY=sk-YOUR_KEY_HERE

# Anthropic
PERPLEXITY_API_KEY=sk-ant-YOUR_KEY_HERE

# Mistral
MISTRAL_API_KEY=YOUR_KEY_HERE

# GitHub (optional, for auto-commits)
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE

# Ollama (for local AI)
OLLAMA_BASE_URL=http://localhost:11434
```

⚠️ **Important**: Never commit `.env` to Git! It's in `.gitignore`.

✅ **Environment configured!**

---

## 🧪 Step 7: Verify Everything Works

### 7.1 Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Expected: All tests PASSED ✅

# Run with coverage
pytest tests/ -v --cov=core --cov-report=html
```

### 7.2 Run Code Quality Checks

```bash
# Format code
black core/ tests/

# Check linting
flake8 core/ tests/

# Type checking
mypy core/

# All should complete without errors ✅
```

### 7.3 Test the Lexer (HyperCode)

```bash
# Run the lexer
python core/lexer.py

# Should show:
# Token types available: [list of tokens]

# Or run it directly:
python -c "from core.lexer import HyperCodeLexer; lexer = HyperCodeLexer(); print('✅ Lexer works!')"
```

✅ **Everything works!**

---

## 🐳 Step 8: Docker Setup (Optional)

If you want to containerize HyperCode:

### 8.1 Build Docker Image

```bash
# Build the Docker image
docker build -t hypercode:latest .

# Expected: "Successfully tagged hypercode:latest"
```

### 8.2 Run Docker Container

```bash
# Run the container
docker run -it hypercode:latest

# Should execute the HyperCode CLI
```

✅ **Docker ready!**

---

## 📝 Step 9: Make Your First Commit

```bash
# Add all files to git
git add .

# Verify what you're adding
git status

# Commit with a meaningful message
git commit -m "🚀 chore: initialize HyperCode project structure

- Setup complete project structure via scaffold.py
- Installed all dependencies (production + dev)
- Configured virtual environment
- Setup pre-commit hooks for code quality
- All tests passing ✅
- Ready for development"

# Push to GitHub
git push origin main
```

✅ **First commit done!**

---

## 🎯 Development Workflow

Now that everything is setup, here's your daily workflow:

### Day-to-Day Development

```bash
# 1. Activate virtual environment (if not already active)
source .venv/bin/activate

# 2. Make your changes
# (edit files, write code, etc.)

# 3. Run tests before committing
pytest tests/ -v

# 4. Format code
black core/ tests/

# 5. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: your feature description"

# 6. Push to GitHub
git push origin main
```

### Installing New Packages

```bash
# Install a new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Commit the change
git add requirements.txt
git commit -m "chore: add package-name dependency"
git push origin main
```

---

## 🚨 Troubleshooting

### Problem: "Python 3.10+ not found"

```bash
# Check installed Python versions
python --version
python3 --version
python3.11 --version

# Use the correct version
python3.11 -m venv .venv
```

### Problem: "Virtual environment won't activate"

```bash
# Recreate the virtual environment
rm -rf .venv  # or rmdir /s .venv on Windows
python3 -m venv .venv
source .venv/bin/activate
```

### Problem: "Permission denied" on pre-commit

```bash
# Make the script executable
chmod +x .git/hooks/pre-commit

# Then reinstall
pre-commit install --install-hooks
```

### Problem: "Module not found" errors

```bash
# Make sure venv is activated
which python  # Should show path to .venv/bin/python

# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Problem: Tests failing after setup

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Run tests again
pytest tests/ -v
```

---

## 📚 Quick Reference Commands

```bash
# Activate/Deactivate venv
source .venv/bin/activate      # Activate (Unix/Mac)
.venv\Scripts\activate          # Activate (Windows)
deactivate                      # Deactivate (all systems)

# Run tests
pytest tests/ -v                # All tests verbose
pytest tests/test_lexer.py -v   # Single test file
pytest-watch tests/             # Watch mode (auto-rerun)

# Code quality
black core/ tests/              # Format
flake8 core/ tests/             # Lint
mypy core/                      # Type check
pre-commit run --all-files      # All checks

# Project management
git status                      # Check status
git add .                       # Stage changes
git commit -m "message"         # Commit
git push origin main            # Push
git log --oneline -5            # View recent commits

# Dependencies
pip install -r requirements.txt         # Install
pip freeze > requirements.txt           # Update
pip list                                # List installed
pip uninstall package-name              # Remove
```

---

## ✅ Setup Verification Checklist

Before moving forward, verify all of these:

- [ ] Python 3.10+ installed
- [ ] Git installed and configured
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Project scaffolded with `python scaffold.py`
- [ ] `pip install -r requirements.txt` completed
- [ ] `pip install -r requirements-dev.txt` completed
- [ ] Pre-commit hooks installed with `pre-commit install`
- [ ] `.env` file created and configured
- [ ] All tests pass with `pytest tests/ -v`
- [ ] Code quality checks pass (`black`, `flake8`, `mypy`)
- [ ] Docker image builds (optional): `docker build -t hypercode:latest .`
- [ ] First commit pushed to GitHub

---

## 🚀 You're Ready!

Your HyperCode development environment is now: ✅ Professional-grade ✅ Cross-platform
compatible ✅ Automated (scaffolding, pre-commit, testing) ✅ Production-ready ✅ CI/CD
integrated

**Now go build something LEGENDARY!** 👊

---

## 📞 Need Help?

- **Setup Issues**: Check [Troubleshooting](#-troubleshooting) section
- **GitHub Issues**: Create an issue with "setup" tag
- **Discord**: Ask in #setup-help channel
- **Email**: hello@hypercode.dev

---

**Happy coding, broski!** 🔥♾️

_Created_: November 11, 2025 _Version_: 2.0 (Enhanced) _Status_: Production-ready
