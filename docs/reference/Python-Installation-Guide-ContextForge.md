# Optimal Python Environment Installation Guide

# ContextForge Triangle Foundation - Sacred Geometry Framework

# Agent: GitHub Copilot | Date: 2025-08-07 | Shape: Triangle (Stable Foundation)

## 🔺 Foundation Phase: Python Installation Strategy

### Step 1: Download Official Python

```powershell
# Navigate to https://www.python.org/downloads/
# Download Python 3.12.x (latest stable) for Windows x86-64
# CRITICAL: Use python.org version, NOT Microsoft Store
```

**Download URL**: <https://www.python.org/downloads/windows/>
**Recommended Version**: Python 3.12.x (latest stable)
**Architecture**: Windows x86-64 executable installer

### Step 2: Installation Configuration

When running the installer:

1. ✅ **Check "Add Python to PATH"** (CRITICAL)
2. ✅ **Check "Install for all users"** (Recommended)
3. ✅ **Choose "Customize installation"**
4. ✅ **Advanced Options**:
   - Install for all users
   - Add Python to environment variables
   - Precompile standard library
   - Download debugging symbols

### Step 3: Verification Script

```powershell
# Run this after installation to verify
python --version
python -m pip --version
python -c "import sys; print(f'Python executable: {sys.executable}')"
python -c "import sys; print(f'Python version: {sys.version}')"
```

## 🔵 Circle Phase: Jupyter Ecosystem Installation

### Step 4: Upgrade pip and Install Core Packages

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install Jupyter ecosystem
python -m pip install jupyter jupyterlab qtconsole ipykernel

# Install additional packages for tool testing
python -m pip install python-dotenv requests pandas numpy matplotlib tqdm
```

### Step 5: Configure Jupyter Kernels

```powershell
# Register Python kernel with Jupyter
python -m ipykernel install --user --name=python3 --display-name="Python 3"

# Verify kernel installation
jupyter kernelspec list
```

### Step 6: Test Jupyter Installation

```powershell
# Test Jupyter Lab (will open in browser)
jupyter lab --version

# Test Jupyter Notebook
jupyter notebook --version

# Test qtconsole
jupyter qtconsole --version
```

## 🌀 Spiral Phase: VS Code Integration

### Step 7: VS Code Python Extension Verification

- Ensure Python extension is installed in VS Code
- Reload VS Code after Python installation
- Verify Python interpreter is detected

### Step 8: Environment Validation Script

```powershell
# Create comprehensive validation script
python -c "
import sys
import subprocess
import pkg_resources

print('=== Python Environment Validation ===')
print(f'Python Version: {sys.version}')
print(f'Python Executable: {sys.executable}')
print(f'Python Path: {sys.path[:3]}...')

try:
    import jupyter
    print(f'Jupyter: ✅ Available')
except ImportError:
    print(f'Jupyter: ❌ Missing')

try:
    import IPython
    print(f'IPython: ✅ Available')
except ImportError:
    print(f'IPython: ❌ Missing')

# List installed packages
installed_packages = [pkg.project_name for pkg in pkg_resources.working_set]
critical_packages = ['jupyter', 'jupyterlab', 'qtconsole', 'ipykernel', 'pip']
for package in critical_packages:
    if package in installed_packages:
        print(f'{package}: ✅ Installed')
    else:
        print(f'{package}: ❌ Missing')
"
```

## 💠 Pentagon Phase: Quality & Performance

### Step 9: Install Development & Testing Packages

```powershell
# Install packages for code quality and testing
python -m pip install black flake8 pytest mypy

# Install packages for enhanced notebook experience
python -m pip install nb_conda_kernels jupyter_contrib_nbextensions
```

### Step 10: Configure Environment Variables (Optional)

```powershell
# Set PYTHONPATH if needed (usually not required)
# $env:PYTHONPATH = "C:\path\to\your\python\modules"

# Verify environment
python -c "import os; print('PYTHONPATH:', os.environ.get('PYTHONPATH', 'Not set'))"
```

## 🔷 Dodecahedron Phase: Full Integration Testing

### Step 11: Execute Complete Tool Testing

```powershell
# Navigate to workspace
cd "c:\Users\james.e.hardy\OneDrive - Avanade\PowerShell Projects"

# Launch Jupyter Lab to run Complete-Tool-Capability-Assessment.ipynb
jupyter lab Complete-Tool-Capability-Assessment.ipynb
```

### Step 12: Validation Checklist

- [ ] Python interpreter responds to `python --version`
- [ ] Pip package manager functional with `python -m pip --version`
- [ ] Jupyter Lab launches with `jupyter lab`
- [ ] Jupyter Notebook launches with `jupyter notebook`
- [ ] QtConsole launches with `jupyter qtconsole`
- [ ] VS Code detects Python interpreter
- [ ] Can execute .ipynb files in VS Code
- [ ] Complete-Tool-Capability-Assessment.ipynb can be opened

## 🛡️ Trust-but-Verify Protocol

### Post-Installation Verification Script

```powershell
# Create and run this verification script
$verificationScript = @"
import sys
import subprocess
import json
from datetime import datetime

verification_results = {
    'timestamp': datetime.now().isoformat(),
    'python_version': sys.version,
    'python_executable': sys.executable,
    'verification_status': {}
}

# Test basic Python functionality
try:
    verification_results['verification_status']['python_basic'] = 'PASS'
except Exception as e:
    verification_results['verification_status']['python_basic'] = f'FAIL: {e}'

# Test pip functionality
try:
    import pip
    verification_results['verification_status']['pip'] = 'PASS'
except Exception as e:
    verification_results['verification_status']['pip'] = f'FAIL: {e}'

# Test Jupyter
try:
    import jupyter
    verification_results['verification_status']['jupyter'] = 'PASS'
except Exception as e:
    verification_results['verification_status']['jupyter'] = f'FAIL: {e}'

# Test IPython/QtConsole
try:
    import IPython
    verification_results['verification_status']['ipython'] = 'PASS'
except Exception as e:
    verification_results['verification_status']['ipython'] = f'FAIL: {e}'

print(json.dumps(verification_results, indent=2))
"@

# Save and execute verification
$verificationScript | Out-File -FilePath "python_verification.py" -Encoding UTF8
python python_verification.py
```

## 📋 ContextForge Compliance

- **Shape**: Triangle (Stable Foundation) → Circle (Complete Lifecycle) → Spiral (Iterative Enhancement)
- **Logging**: All steps logged with timestamps and validation
- **Sacred Tree**: Roots (Python) → Trunk (Jupyter) → Branches (Extensions) → Leaves (Notebooks)
- **Trust-but-Verify**: Every component validated after installation

## 🚀 Next Steps After Installation

1. **Execute Complete-Tool-Capability-Assessment.ipynb**
2. **Test all 119 GitHub Copilot tools systematically**
3. **Generate comprehensive AAR with verified results**
4. **Update P002 verification logs with Python success status**
