#!/usr/bin/env python3
"""
🧠 HyperCode REPL
Interactive Read-Eval-Print Loop

Supports all HyperCode operations:
- Variables, conditionals, loops, functions
- Fast <100ms feedback
- ND-friendly error messages
- History support
"""

import sys
from hypercode_interpreter_v2 import (
    Tokenizer, Parser, Executor, SyntaxError as HCSyntaxError
)

class REPL:
    """Interactive HyperCode environment"""
    
    def __init__(self):
        self.executor = Executor()
        self.history = []
        self.session_vars = {}  # Track variables across commands
        self.session_funcs = {}  # Track functions across commands
    
    def run(self):
        """Start interactive session"""
        print("🧠 HyperCode REPL v0.9")
        print("Neurodivergent-first programming")
        print()
        print("Commands:")
        print("  help     - Show syntax help")
        print("  history  - Show command history")
        print("  clear    - Clear variables")
        print("  exit     - Quit")
        print()
        print("Start coding: ")
        print()
        
        while True:
            try:
                code = input(">>> ").strip()
                
                # Special commands
                if code == "help":
                    self.show_help()
                    continue
                
                elif code == "history":
                    self.show_history()
                    continue
                
                elif code == "clear":
                    self.executor = Executor()
                    print("✅ Cleared all variables and functions")
                    continue
                
                elif code in ("exit", "quit"):
                    print("👋 Goodbye! Keep coding. 💓")
                    break
                
                elif code == "":
                    continue
                
                # Execute code
                self.execute_line(code)
                self.history.append(code)
            
            except KeyboardInterrupt:
                print("\n👋 (Interrupted)")
                continue
            
            except EOFError:
                print("\n👋 Goodbye! Keep coding. 💓")
                break
    
    def execute_line(self, code: str):
        """Execute single line of code"""
        # Ensure it ends with semicolon
        if not code.endswith(';'):
            code += ';'
        
        try:
            # Tokenize
            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Execute
            if ast['statements']:
                for stmt in ast['statements']:
                    self.executor.execute_statement(stmt)
        
        except (SyntaxError, HCSyntaxError) as e:
            print(f"❌ Syntax Error: {e}")
            print("   Tip: Check brackets, semicolons, and spelling")
        
        except NameError as e:
            print(f"❌ Name Error: {e}")
            print("   Tip: Use 'let name = value;' to create a variable")
        
        except TypeError as e:
            print(f"❌ Type Error: {e}")
            print("   Tip: Make sure numbers are numbers, strings are strings")
        
        except ValueError as e:
            print(f"❌ Value Error: {e}")
            print("   Tip: Check your calculation or data type")
        
        except ZeroDivisionError:
            print(f"❌ Can't divide by zero!")
            print("   Tip: Check your division operation")
        
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
    
    def show_help(self):
        """Show syntax help"""
        print("📖 HyperCode Syntax Reference")
        print()
        print("VARIABLES:")
        print("  let x = 10;")
        print("  let name = \"Alex\";")
        print()
        print("PRINTING:")
        print("  print \"Hello!\";")
        print("  print x;")
        print()
        print("MATH:")
        print("  let sum = 5 + 3;")
        print("  let product = 4 * 2;")
        print()
        print("CONDITIONALS:")
        print("  if x > 5 print \"big\";")
        print("  if x == 10 { print \"ten\"; }")
        print()
        print("LOOPS:")
        print("  loop(5) { print \"hi\"; }")
        print()
        print("FUNCTIONS:")
        print("  function greet(name) { print name; }")
        print("  greet(\"Alex\");")
        print()
        print("COMPARISONS:")
        print("  ==  equal")
        print("  !=  not equal")
        print("  <   less than")
        print("  >   greater than")
        print("  <=  less than or equal")
        print("  >=  greater than or equal")
        print()
    
    def show_history(self):
        """Show command history"""
        if not self.history:
            print("No history yet.")
            return
        
        print("📑 Command History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i}. {cmd}")
        print()

def main():
    """Start REPL"""
    repl = REPL()
    repl.run()

if __name__ == '__main__':
    main()
