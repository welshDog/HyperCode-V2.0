# 📖 HyperCode Syntax Reference

Complete reference for all HyperCode operations. **All features tested and working.**

---

## 📜 Basics

### **Comments**

```hypercode
# Single-line comment
let x = 5;  # Inline comment

/* Multi-line
   comment
   spanning lines */
```

### **Semicolons**

Every statement ends with `;` (semicolon)

```hypercode
print "hello";    ✅ Correct
print "hello"     ❌ Wrong (missing ;)
```

---

## 💰 Output (Printing)

### **print**

Output text or values to console.

```hypercode
print "Hello, World!";
print 42;
print 3.14;

let name = "Alex";
print name;
print "Name: ";
print name;
```

**Output:**
```
Hello, World!
42
3.14
Alex
Name: 
Alex
```

---

## 🖱 Variables

### **let (Create Variable)**

Declare and initialize a variable.

```hypercode
let x = 10;              # Number
let message = "hello";   # String
let pi = 3.14;           # Decimal
let count = 0;           # Start with zero
```

### **Using Variables**

```hypercode
let age = 25;
print age;               # Output: 25

let new_age = age + 1;
print new_age;           # Output: 26
```

### **Variable Naming Rules**

```
✅ VALID:                  ❌ INVALID:
x                          123x (starts with number)
my_variable                 my-variable (uses dash)
VARIABLE                    variable! (has special char)
var123                      let (reserved keyword)
```

---

## 🗣 Data Types

### **Numbers**

```hypercode
let integer = 42;         # Whole number
let decimal = 3.14;       # With decimal point
let negative = -10;       # Negative numbers
```

### **Strings**

Text enclosed in quotes:

```hypercode
let name = "Alex";
let message = "Hello, World!";
let empty = "";
```

**String Operations:**

```hypercode
let first = "Hello";
let second = "World";
let combined = first + second;  # Concatenation
print combined;                 # Output: HelloWorld
```

### **Booleans**

```hypercode
let is_active = true;
let is_closed = false;
let check = 5 > 3;   # Results in true
```

### **Type Conversion**

```hypercode
let num = 42;
let text = "42";

# Numbers and strings are different
let sum1 = 10 + 5;       # 15 (math)
let sum2 = "10" + "5";   # "105" (concatenation)
```

---

## 📍 Arithmetic

### **Basic Operations**

```hypercode
let a = 10;
let b = 3;

let add = a + b;         # Addition: 13
let subtract = a - b;    # Subtraction: 7
let multiply = a * b;    # Multiplication: 30
let divide = a / b;      # Division: 3.333...
let modulo = a % b;      # Remainder: 1
```

### **Order of Operations**

```hypercode
let result = 2 + 3 * 4;  # 14 (multiply first, then add)
let correct = (2 + 3) * 4;  # 20 (parentheses first)
```

### **Operators**

```
+   Addition
-   Subtraction
*   Multiplication
/   Division
%   Modulo (remainder)
```

---

## 🔍 Comparisons

Compare values and get true/false results.

```hypercode
let x = 10;
let y = 5;

if x > y print "greater";      # true
if x < y print "less";         # false
if x == y print "equal";       # false
if x != y print "not equal";   # true
if x >= y print ">=";         # true
if x <= y print "<=";         # false
```

### **Comparison Operators**

```
>      Greater than
<      Less than
==     Equal to
!=     Not equal to
>=     Greater than or equal
<=     Less than or equal
```

---

## 🔄 Conditionals (if)

### **Single Statement**

```hypercode
let age = 20;

if age >= 18 print "Adult";
if age < 18 print "Minor";
```

### **Multiple Statements (Block)**

```hypercode
let score = 85;

if score >= 90 {
  print "A";
  print "Excellent!";
}

if score >= 80 {
  print "B";
}
```

### **Nested Conditionals**

```hypercode
let age = 25;
let license = true;

if age >= 18 {
  if license == true {
    print "Can drive";
  }
}
```

---

## 🔁 Loops

### **Basic Loop**

Repeat code N times.

```hypercode
loop(5) {
  print "Hello!";
}

# Output:
# Hello!
# Hello!
# Hello!
# Hello!
# Hello!
```

### **Loop with Variable Counter**

```hypercode
let i = 0;
loop(3) {
  print i;
  let i = i + 1;
}

# Output:
# 0
# 1
# 2
```

### **Loop with Conditional**

```hypercode
let i = 1;
loop(5) {
  if i % 2 == 0 print "even";
  if i % 2 != 0 print "odd";
  let i = i + 1;
}
```

### **Nested Loops**

```hypercode
loop(3) {
  loop(2) {
    print "*";
  }
  print "\n";
}
```

---

## 🌟 Functions

### **Function Definition**

```hypercode
function greet(name) {
  print "Hello, ";
  print name;
  print "!";
}
```

### **Function Call**

```hypercode
greet("Alex");
greet("Jordan");
greet("Sam");

# Output:
# Hello, Alex!
# Hello, Jordan!
# Hello, Sam!
```

### **Multiple Parameters**

```hypercode
function add(a, b) {
  let sum = a + b;
  print sum;
}

add(5, 3);     # Output: 8
add(10, 20);   # Output: 30
```

### **Return Statement**

```hypercode
function multiply(x, y) {
  let product = x * y;
  return product;
}

let result = multiply(4, 5);  # result = 20
print result;
```

### **Function Scope**

Variables inside functions are local:

```hypercode
let global_var = 10;

function test() {
  let local_var = 5;
  print local_var;  # Works inside function
}

test();                  # Output: 5
print local_var;         # Error: not defined outside
```

---

## 💫 Putting It Together

### **Example 1: FizzBuzz**

```hypercode
let i = 1;
loop(15) {
  if i % 15 == 0 print "FizzBuzz";
  if i % 3 == 0 print "Fizz";
  if i % 5 == 0 print "Buzz";
  if i % 3 != 0 print i;
  if i % 5 != 0 print i;
  let i = i + 1;
}
```

### **Example 2: Times Table**

```hypercode
function times_table(n) {
  let i = 1;
  loop(10) {
    let result = n * i;
    print result;
    let i = i + 1;
  }
}

times_table(3);
```

### **Example 3: Factorial**

```hypercode
function factorial(n) {
  if n <= 1 return 1;
  return n * factorial(n - 1);
}

print factorial(5);  # Output: 120
```

---

## 🚰 Error Messages

HyperCode errors are designed to help:

```
❌ Syntax Error: Expected semicolon at line 2
   Tip: Check your brackets, quotes, and semicolons

❌ Name Error: Variable 'x' is not defined
   Tip: Use 'let x = value;' to create a variable

❌ Type Error: Cannot add string and number
   Tip: Make sure both values are the same type

❌ Division by zero
   Tip: Check your division operation
```

---

## 🚫 Reserved Keywords

These words are special and can't be variable names:

```
let        print      if         function   loop
return     true       false      and        or
not        elif       else       class      quantum
ai         dna        for        while
```

---

## 🜟 Tips & Tricks

### **Debug with Print**

```hypercode
let x = 10;
print "x is: ";
print x;  # Output: x is: 10
```

### **Clear Variable Names**

```hypercode
let student_age = 20;  # ✅ Clear
let a = 20;            # ❌ Not clear
```

### **Add Comments**

```hypercode
# Check if person can vote
if age >= 18 print "Eligible";
```

### **Use Functions for Reusable Code**

```hypercode
function add(a, b) {
  return a + b;
}

let sum1 = add(5, 3);    # 8
let sum2 = add(10, 20);  # 30
```

### **Test with Loop**

```hypercode
loop(10) {
  print "Testing...";
}
```

---

## 📁 Coming Soon

Phase 2 (Q1 2026):
- Arrays: `let arr = [1, 2, 3];`
- Objects: `let person = { name: "Alex", age: 25 };`
- More string operations
- Error handling (try/catch)

Phase 3 (Q2 2026):
- AI Integration (Claude, GPT-4)
- Advanced patterns
- Async operations

Phase 4 (Q3-Q4 2026):
- Quantum computing
- DNA/molecular computing
- Full ecosystem

---

**Next:** Check [GETTING_STARTED.md](./GETTING_STARTED.md) for tutorials!
