# 💓 Contributing to HyperCode

## Welcome Home

If you're neurodivergent, you belong here. If you're not, you're welcome here too.

HyperCode is built **by neurodivergent developers, for neurodivergent minds**—and for everyone who wants code to be more accessible, more inclusive, and more human.

---

## 🧠 What We Value

- **Neurodivergent-first thinking** — We celebrate how our brains actually work
- **Clear communication** — No hidden meanings, no jargon, no assumptions
- **Accessibility** — Everything should be usable by everyone
- **Community over perfection** — Done together beats done alone
- **Respect** — We listen, we learn, we grow together

---

## 🚀 How to Contribute

### **Want to Report a Bug?**

1. Go to [Issues](https://github.com/welshDog/HYPERcode-V2/issues)
2. Click "New Issue"
3. Select "Bug Report"
4. Fill in:
   - What you were trying to do
   - What happened
   - What you expected
   - Steps to reproduce

**Example:**
```
Title: Print statement breaks with special characters

What I was doing:
  print "Hello & goodbye";

What happened:
  Error: unexpected character &

What I expected:
  Output: Hello & goodbye

How to reproduce:
  1. Create file with that code
  2. Run: python hypercode_interpreter.py filename
  3. See error
```

### **Want to Suggest a Feature?**

1. Go to [Issues](https://github.com/welshDog/HYPERcode-V2/issues)
2. Click "New Issue"
3. Select "Feature Request"
4. Describe:
   - What you want HyperCode to do
   - Why it matters
   - How you'd use it

**Example:**
```
Title: Add support for arrays

What I want:
  let list = [1, 2, 3];
  print list[0];  // Output: 1

Why it matters:
  Many programs need to work with lists of data
  This is fundamental programming capability

How I'd use it:
  I want to write a program that tracks multiple values
  Then access them by index
```

### **Want to Code a Fix?**

1. **Fork the repo** (click Fork)
2. **Create a branch**:
   ```bash
   git checkout -b fix/issue-name
   ```
3. **Make changes** in small, clear commits
4. **Write tests** for your fix
5. **Test locally**:
   ```bash
   python -m pytest tests/
   ```
6. **Push to your fork**:
   ```bash
   git push origin fix/issue-name
   ```
7. **Create Pull Request** with clear description

---

## 💻 Code Style Guide

### **Python Style (PEP 8 + Accessibility)**

```python
# ✅ GOOD: Clear, explicit, minimal cognitive load
def execute_print(ast_node, variables):
    """Execute a print statement"""
    value = eval_expr(ast_node['value'], variables)
    print(value)
    return value

# ❌ BAD: Cryptic, assumes knowledge
def exec_p(n, v):
    val = e(n['v'], v)
    print(val)
    return val
```

### **Key Rules**

1. **Descriptive names** — `print_value` not `pv`
2. **Comments for why** — Code shows what, comments show why
3. **Early returns** — Reduce nesting, improve readability
4. **Single responsibility** — One function, one job
5. **Consistent formatting** — 4 spaces, not tabs

### **Docstring Example**

```python
def tokenize(code):
    """
    Convert HyperCode source into tokens.
    
    Args:
        code (str): HyperCode source code
    
    Returns:
        list: Tokens (strings like 'PRINT', 'IDENTIFIER', etc)
    
    Example:
        >>> tokenize('print "hello";')
        ['PRINT', 'STRING', ';']
    """
    # Implementation...
```

---

## 🧪 Testing

### **When to Write Tests**

- **Always** when fixing a bug
- **Always** when adding a feature
- **Every function** that affects output

### **Test Structure**

```python
def test_feature_name():
    """Clear description of what we're testing"""
    # ARRANGE: Set up test data
    code = 'let x = 5;'
    variables = {}
    
    # ACT: Do the thing
    result = execute(code, variables)
    
    # ASSERT: Check the result
    assert variables['x'] == 5
    print("✅ test passed")
```

### **Run Tests**

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_tokenizer.py::test_print_statement

# Run with verbose output
python -m pytest tests/ -v
```

---

## 📝 Commit Messages

**Format:**
```
[emoji] Brief description (under 50 chars)

Optional detailed explanation of what and why (not how).

Fixes: #123 (if fixing an issue)
```

**Examples:**
```
🐛 Fix tokenizer crash on special characters

The tokenizer was throwing on '&' in strings.
Now properly handles all ASCII special chars.

Fixes: #42

✨ Add array support

Users can now use [1, 2, 3] syntax.
Implements indexing and basic operations.

📚 Improve docs for REPL usage

Added examples and clarified command syntax.
```

---

## 🎯 PR Guidelines

### **Before You Start**

- Check [Open Issues](https://github.com/welshDog/HYPERcode-V2/issues)
- Comment on issue: "I'll work on this"
- Wait for green light (avoids duplicates)

### **Your PR Description**

```markdown
## What
Brief description of what this PR does

## Why
Why this matters, what problem it solves

## How
How you solved it (high level, not code walkthrough)

## Testing
How you tested it, what cases you covered

Fixes: #123
```

### **PR Checklist**

- [ ] Tests pass locally (`pytest tests/`)
- [ ] New tests added for new features
- [ ] Code follows style guide
- [ ] Docstrings added/updated
- [ ] No commented-out code
- [ ] Commit messages are clear

---

## 🤝 Code Review

**When reviewing:**
- Be kind and constructive
- Ask questions, don't demand
- Celebrate good code
- Suggest improvements, don't mandate

**When receiving feedback:**
- Listen openly
- Ask clarifying questions
- It's about the code, not you
- You're learning together

---

## 💡 Common First Contributions

### **Great for Beginners:**
1. **Documentation** — Fix typos, clarify examples, improve readability
2. **Tests** — Add test cases for uncovered scenarios
3. **Examples** — Create new example programs (.hc files)
4. **Comments** — Improve code documentation
5. **Error Messages** — Make error messages clearer

### **Growing Your Skill:**
1. **Small Bugs** — Fix tokenizer edge cases
2. **Minor Features** — Add single operations
3. **Refactoring** — Improve existing code structure
4. **Performance** — Optimize slow operations
5. **Accessibility** — Improve IDE usability

---

## 🚀 Getting Help

**Have questions?**
- Create "Question" issue
- Check existing discussions
- Ask in comment on related issue
- Ping @welshDog on GitHub

**Stuck?**
- Break it into smaller pieces
- Write what you know
- Ask for help (seriously, we help)
- No question is stupid

---

## 📖 Resources

- [Git Guide](https://guides.github.com/)
- [Python Style (PEP 8)](https://pep8.org/)
- [Testing Best Practices](https://docs.pytest.org/)
- [HyperCode Syntax Reference](./docs/SYNTAX_REFERENCE.md)
- [HyperCode Architecture](./docs/ARCHITECTURE.md)

---

## 🎉 Contributors

Every contribution matters. You'll be:
- Added to [CONTRIBUTORS.md](./CONTRIBUTORS.md)
- Celebrated in release notes
- Thanked publicly
- Part of something bigger

---

## 💓 Final Words

**You belong here.**

If you're neurodivergent and coding feels hard in traditional languages, HyperCode is FOR YOU.

If you're building HyperCode and it feels overwhelming, that's normal. Take breaks. Ask for help. Go at your pace.

**We're building the future together.**

Neurodivergent minds have changed the world.
Now let's change how we code.

---

**Thanks for being part of this movement.** 💓🚀
