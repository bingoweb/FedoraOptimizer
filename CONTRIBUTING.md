# Contributing to Fedora Optimizer

Thank you for your interest in contributing to Fedora Optimizer! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/FedoraOptimizer.git
cd FedoraOptimizer
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Development Tools** (Recommended)
```bash
pip install pylint pre-commit
```

---

## 📋 Code Standards

### Python Style Guide

- **PEP 8:** Follow Python's official style guide
- **Pylint:** Run `pylint src/modules/optimizer/*.py` before committing
- **Target Score:** Maintain Pylint score above 8.5/10
- **Encoding:** Always use `encoding="utf-8"` in `open()` calls
- **Type Hints:** Use type hints for all public methods
- **Docstrings:** Required for all public and private methods

**Example:**
```python
def analyze_feature(self, current_values: Dict[str, str]) -> List[OptimizationProposal]:
    """
    Analyze feature and generate optimization proposals.
    
    Args:
        current_values: Current sysctl values
        
    Returns:
        List of optimization proposals
    """
    # Implementation
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(engine): add analyze_io_scheduler method
fix(facade): resolve AttributeError in analyze_usage_persona
docs(memory): update AI_MEMORY.md with latest changes
refactor(sysctl): remove redundant _detect_disk_type method
test(optimizer): add unit tests for SysctlOptimizer
```

---

## 🧪 Testing

### Manual Testing

**Syntax Check:**
```bash
python3 -m py_compile src/modules/optimizer/*.py
```

**Import Test:**
```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from modules.optimizer import *"
```

**TUI Test** (requires root):**
```bash
sudo ./run.sh
# Test each menu option 1-8
```

### Automated Tests (TODO)

```bash
pytest tests/  # Coming soon
```

---

## 📝 Documentation Requirements

### CRITICAL: AI_MEMORY.md

**Every significant change MUST update `docs/AI_MEMORY.md`!**

This file is the project's "single source of truth" and contains:
- Architecture overview
- Class responsibilities
- Recent changes
- Known issues
- Development guidelines

**When to update:**
- Adding new methods
- Changing architecture
- Fixing critical bugs
- Adding new features

### Other Documentation

- **README.md:** User-facing features only
- **CHANGELOG.md:** Follow "Keep a Changelog" format
- **Code Comments:** For complex logic only

---

## 🔄 Pull Request Process

### Before Creating PR

1. **Update Documentation**
   - [ ] Update `docs/AI_MEMORY.md` with changes
   - [ ] Update `CHANGELOG.md` in "Unreleased" section
   - [ ] Update `README.md` if user-facing changes

2. **Test Your Changes**
   - [ ] Run syntax check
   - [ ] Run import tests
   - [ ] Manual TUI testing (all menu options)
   - [ ] Check Pylint score

3. **Clean Code**
   - [ ] Remove debug print statements
   - [ ] Remove commented code
   - [ ] Fix all Pylint warnings (or document why ignored)

### Creating Pull Request

1. **Create Feature Branch**
```bash
git checkout -b feature/amazing-feature
```

2. **Make Changes and Commit**
```bash
git add .
git commit -m "feat: add amazing feature"
```

3. **Push to Fork**
```bash
git push origin feature/amazing-feature
```

4. **Open Pull Request**
- Use a clear, descriptive title
- Fill out the PR template
- Reference any related issues

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation updated (`AI_MEMORY.md`, `CHANGELOG.md`)
- [ ] Commit messages follow Conventional Commits
- [ ] No merge conflicts
- [ ] Changes are focused and atomic

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Test with latest version
3. Ensure it's reproducible

### Bug Report Template

```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**System Information:**
- OS: Fedora [version]
- Python: [version]
- Fedora Optimizer: [version]

**Additional Context:**
Screenshots, logs, etc.
```

---

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if already requested
2. Describe the use case
3. Explain expected behavior
4. Consider implementation complexity

---

## 🏗️ Project Structure

```
fedoraclean/
├── src/modules/optimizer/  # Core optimization package
│   ├── facade.py          # Main interface
│   ├── engine.py          # AI proposals
│   ├── hardware.py        # Hardware detection
│   ├── sysctl.py          # Kernel parameters
│   ├── io_scheduler.py    # I/O optimization
│   ├── transaction.py     # Rollback system
│   ├── backup.py          # Snapshots
│   └── models.py          # Data classes
├── src/ui/                # TUI components
├── docs/                  # Documentation
└── tests/                 # Test suite (TODO)
```

---

## 📚 Resources

- **Project Documentation:** `docs/AI_MEMORY.md`
- **Architecture:** See AI_MEMORY.md
- **Sysctl Reference:** https://www.kernel.org/doc/Documentation/sysctl/
- **I/O Schedulers:** https://www.kernel.org/doc/html/latest/block/

---

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

---

## 📞 Getting Help

- **Issues:** For bug reports and feature requests
- **Discussions:** For questions and general discussions
- **Documentation:** Check `docs/AI_MEMORY.md` first

---

## 🎓 Learning Path

New to the project? Start here:

1. Read `README.md` for overview
2. Read `docs/AI_MEMORY.md` for architecture
3. Run the application locally
4. Try making a small documentation fix
5. Tackle a "good first issue"

---

Thank you for contributing to Fedora Optimizer! 🚀
