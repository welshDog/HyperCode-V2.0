# 🚀 Getting Started with HyperCode

Welcome! You're about to code in a language built **for how your brain actually thinks**.

---

## 🎩 What is HyperCode?

A programming language designed for neurodivergent brains:
- **ADHD:** Quick feedback, clear structure, minimal overwhelm
- **Autism:** Literal syntax, explicit behavior, no hidden meanings
- **Dyslexia:** Visual IDE, accessible fonts, high contrast
- **Everyone:** Accessible, intuitive, powerful

---

## ⬛ Installing HyperCode

### **On Mac/Linux:**

```bash
# Clone the repo
git clone https://github.com/welshDog/HYPERcode-V2.git
cd HYPERcode-V2

# That's it! You have Python 3.8+, you're good
```

### **On Windows:**

```bash
# Same as above
git clone https://github.com/welshDog/HYPERcode-V2.git
cd HYPERcode-V2

# Need Python? Download from python.org
```

### **Check It Works:**

```bash
python hypercode_interpreter.py hello_world
# Should output: Hello, World!
```

---

## 📑 Your First Program (2 minutes)

### **The Simplest Possible Program:**

Create a file called `myprogram.hc`:

```hypercode
print "Hello, Neurodivergent Future!";
```

### **Run It:**

```bash
python hypercode_interpreter.py myprogram.hc
```

### **You Should See:**

```
Hello, Neurodivergent Future!
```

**Boom. You're a HyperCode programmer.** 🚀

---

## 🌟 Five More Programs (Learn the Basics)

### **Program 1: Variables**

File: `variables.hc`

```hypercode
let name = "Alex";
let age = 25;

print "Name: ";
print name;
print "Age: ";
print age;
```

**Run:**
```bash
python hypercode_interpreter.py variables.hc
```

**Output:**
```
Name: 
Alex
Age: 
25
```

### **Program 2: Math**

File: `math.hc`

```hypercode
let x = 10;
let y = 5;

let sum = x + y;
let difference = x - y;
let product = x * y;

print "Sum: ";
print sum;
print "Difference: ";
print difference;
print "Product: ";
print product;
```

### **Program 3: Conditionals**

File: `conditional.hc`

```hypercode
let age = 20;

if age >= 18 print "You can vote!";
if age < 18 print "Wait a few more years";
```

### **Program 4: Using the REPL**

Interactive mode (great for experiments):

```bash
python hypercode_repl.py
```

You'll see:
```
============================================================
🧠 HyperCode REPL v0.9-beta
============================================================
✨ Neurodivergent-first interactive programming

Commands:
  help      → Show all commands
  vars      → List all variables
  funcs     → List all functions
  clear     → Clear all variables
  history   → Show command history
  exit      → Quit REPL

Start typing HyperCode:
============================================================

>>>
```

Try this:
```
>>> print "Hello from REPL";
Hello from REPL
>>> let x = 42;
>>> print x;
42
>>> vars

📊 Variables:
  x = 42

>>> exit
👋 Goodbye! Keep coding. 💓
```

### **Program 5: The Classic FizzBuzz**

File: `fizzbuzz.hc` (already included, but try modifying it!)

```hypercode
let i = 1;
let output = "";

if i % 15 == 0 print "FizzBuzz";
if i % 3 == 0 print "Fizz";
if i % 5 == 0 print "Buzz";
if i % 3 != 0 if i % 5 != 0 print i;
```

---

## 😛 Syntax Cheat Sheet

### **Output**
```hypercode
print "text";
print 42;
print x;  # Variable
```

### **Variables**
```hypercode
let x = 10;           # Create
let name = "Alex";    # String
let pi = 3.14;        # Decimal
```

### **Math**
```hypercode
let sum = 5 + 3;           # Add
let diff = 10 - 3;         # Subtract
let prod = 4 * 5;          # Multiply
let quotient = 20 / 4;     # Divide
let remainder = 10 % 3;    # Modulo
```

### **Comparisons**
```hypercode
if x > 5 print "greater";
if x < 5 print "less";
if x == 5 print "equal";
if x != 5 print "not equal";
if x >= 5 print "greater or equal";
if x <= 5 print "less or equal";
```

### **Comments**
```hypercode
# This is a comment
let x = 10;  # Inline comment

/* Multi-line
   comment
   here */
```

---

## 📚 Next Steps

### **Learn More:**
- Read [SYNTAX_REFERENCE.md](./SYNTAX_REFERENCE.md) → All operations
- Check [EXAMPLES](../examples/) → Real programs
- Read [ARCHITECTURE.md](./ARCHITECTURE.md) → How it works

### **Try Things:**
- Modify the examples
- Write your own programs
- Break things (that's learning!)
- Use the REPL to experiment

### **Join the Community:**
- GitHub Issues → Ask questions
- [CONTRIBUTING.md](../CONTRIBUTING.md) → Help build HyperCode
- Discussions → Chat with other devs

---

## 🚘 Common Questions

### **Q: I got an error. What do I do?**

A: Read the error message carefully. HyperCode errors are designed to be helpful:
```
❌ Syntax Error: Expected semicolon at line 2
   Tip: Check your brackets, quotes, and semicolons
```

Fix:
1. Check line 2
2. Look for missing semicolon
3. Try running again

### **Q: How do I debug my program?**

A: Use `print` statements!

```hypercode
let x = 10;
print "x is:";
print x;
```

You can see what's happening at each step.

### **Q: Can I use HyperCode for real projects?**

A: Right now, it's great for learning and experiments. We're building quantum and AI features for bigger projects.

### **Q: What if I think of a feature?**

A: [Open an Issue!](https://github.com/welshDog/HYPERcode-V2/issues) Seriously, we want to hear your ideas.

---

## 👋 Getting Help

**Stuck?**
- Check examples: `hello_world`, `fizzbuzz`
- Use REPL to experiment
- Read error messages (they help!)
- Ask a question: [New Issue](https://github.com/welshDog/HYPERcode-V2/issues)

**Want to contribute?**
- Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- Pick a small task
- Get help anytime

**Found a bug?**
- Report it: [New Issue](https://github.com/welshDog/HYPERcode-V2/issues)
- Include:
  - What you were doing
  - What happened
  - What you expected

---

## 🌟 You've Got This

You're learning a language **built for you**.

Take your time.
Break things.
Ask questions.
Celebrate small wins.

**Welcome to HyperCode.**

**Welcome home.** 💓

---

**Next:** Read [SYNTAX_REFERENCE.md](./SYNTAX_REFERENCE.md) to learn all operations.
