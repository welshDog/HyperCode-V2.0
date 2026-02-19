#!/usr/bin/env python3
"""
🧠 HyperCode Interpreter v0.9
Neurodivergent-first programming language

Supports:
- Variables (let x = value)
- Conditionals (if condition statement)
- Loops (loop(n) { ... })
- Functions (function name(args) { ... })
- Arithmetic & comparisons
- Print output
"""

import sys
import re
from typing import Any, Dict, List, Optional

class Token:
    """Represent a single token"""
    def __init__(self, type: str, value: Any, line: int = 1):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.type == other or self.value == other
        return self.type == other.type and self.value == other.value

class Tokenizer:
    """Convert source code into tokens"""
    
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
    
    def error(self, msg: str):
        raise SyntaxError(f"{msg} at line {self.line}")
    
    def peek(self, offset=0):
        """Look at character without consuming"""
        pos = self.pos + offset
        if pos < len(self.code):
            return self.code[pos]
        return None
    
    def advance(self):
        """Consume and return current character"""
        if self.pos < len(self.code):
            char = self.code[self.pos]
            if char == '\n':
                self.line += 1
            self.pos += 1
            return char
        return None
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines"""
        while self.peek() in (' ', '\t', '\n', '\r'):
            self.advance()
    
    def skip_comment(self):
        """Skip # comments"""
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
            if self.peek() == '\n':
                self.advance()
            return True
        return False
    
    def read_string(self, quote: str):
        """Read string literal"""
        value = ""
        self.advance()  # consume opening quote
        
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                escaped = self.peek()
                if escaped == 'n':
                    value += '\n'
                elif escaped == 't':
                    value += '\t'
                elif escaped == 'r':
                    value += '\r'
                elif escaped == '\\':
                    value += '\\'
                elif escaped == quote:
                    value += quote
                else:
                    value += escaped or ''
                self.advance()
            else:
                value += self.advance()
        
        if self.peek() != quote:
            self.error("Unterminated string")
        
        self.advance()  # consume closing quote
        return value
    
    def read_number(self):
        """Read numeric literal"""
        value = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            value += self.advance()
        
        if '.' in value:
            return float(value)
        return int(value)
    
    def read_identifier(self):
        """Read identifier or keyword"""
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        return value
    
    def tokenize(self):
        """Convert code to tokens"""
        keywords = {
            'print', 'let', 'if', 'loop', 'function', 'return',
            'true', 'false', 'and', 'or', 'not'
        }
        
        while self.pos < len(self.code):
            self.skip_whitespace()
            
            if self.skip_comment():
                continue
            
            if self.pos >= len(self.code):
                break
            
            char = self.peek()
            
            # Strings
            if char in ('"', "'"):
                value = self.read_string(char)
                self.tokens.append(Token('STRING', value, self.line))
            
            # Numbers
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token('NUMBER', value, self.line))
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                value = self.read_identifier()
                if value in keywords:
                    self.tokens.append(Token(value.upper(), value, self.line))
                else:
                    self.tokens.append(Token('IDENTIFIER', value, self.line))
            
            # Operators and delimiters
            elif char == '+':
                self.advance()
                self.tokens.append(Token('+', '+', self.line))
            elif char == '-':
                self.advance()
                self.tokens.append(Token('-', '-', self.line))
            elif char == '*':
                self.advance()
                self.tokens.append(Token('*', '*', self.line))
            elif char == '/':
                self.advance()
                self.tokens.append(Token('/', '/', self.line))
            elif char == '%':
                self.advance()
                self.tokens.append(Token('%', '%', self.line))
            elif char == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token('==', '==', self.line))
                else:
                    self.tokens.append(Token('=', '=', self.line))
            elif char == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token('!=', '!=', self.line))
                else:
                    self.error("Unexpected '!'")  
            elif char == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token('<=', '<=', self.line))
                else:
                    self.tokens.append(Token('<', '<', self.line))
            elif char == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token('>=', '>=', self.line))
                else:
                    self.tokens.append(Token('>', '>', self.line))
            elif char == '(':
                self.advance()
                self.tokens.append(Token('(', '(', self.line))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(')', ')', self.line))
            elif char == '{':
                self.advance()
                self.tokens.append(Token('{', '{', self.line))
            elif char == '}':
                self.advance()
                self.tokens.append(Token('}', '}', self.line))
            elif char == ';':
                self.advance()
                self.tokens.append(Token(';', ';', self.line))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(',', ',', self.line))
            else:
                self.error(f"Unexpected character '{char}'")
        
        self.tokens.append(Token('EOF', 'EOF', self.line))
        return self.tokens

class Parser:
    """Parse tokens into Abstract Syntax Tree (AST)"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def error(self, msg: str):
        token = self.current()
        raise SyntaxError(f"{msg} at line {token.line}")
    
    def current(self):
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek(self, offset=1):
        """Look ahead"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def advance(self):
        """Consume and return current token"""
        token = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, expected):
        """Consume expected token or error"""
        token = self.current()
        if token.value != expected and token.type != expected:
            self.error(f"Expected '{expected}' but got '{token.value}'")
        return self.advance()
    
    def parse(self):
        """Parse program"""
        statements = []
        while self.current().type != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return {'type': 'program', 'statements': statements}
    
    def parse_statement(self):
        """Parse single statement"""
        token = self.current()
        
        if token.type == 'PRINT':
            return self.parse_print()
        elif token.type == 'LET':
            return self.parse_let()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'LOOP':
            return self.parse_loop()
        elif token.type == 'FUNCTION':
            return self.parse_function()
        elif token.type == 'RETURN':
            return self.parse_return()
        else:
            self.error(f"Unexpected token: {token.type}")
    
    def parse_print(self):
        """Parse print statement"""
        self.expect('PRINT')
        value = self.parse_expression()
        self.expect(';')
        return {'type': 'print', 'value': value}
    
    def parse_let(self):
        """Parse variable declaration"""
        self.expect('LET')
        name_token = self.expect('IDENTIFIER')
        self.expect('=')
        value = self.parse_expression()
        self.expect(';')
        return {'type': 'let', 'name': name_token.value, 'value': value}
    
    def parse_if(self):
        """Parse if statement"""
        self.expect('IF')
        condition = self.parse_expression()
        
        # Single statement or block
        if self.current().type == '{':
            self.advance()
            statements = []
            while self.current().type != '}':
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.expect('}')
            return {'type': 'if', 'condition': condition, 'statements': statements}
        else:
            statement = self.parse_statement()
            return {'type': 'if', 'condition': condition, 'statements': [statement]}
    
    def parse_loop(self):
        """Parse loop statement"""
        self.expect('LOOP')
        self.expect('(')
        count = self.parse_expression()
        self.expect(')')
        
        if self.current().type == '{':
            self.advance()
            statements = []
            while self.current().type != '}':
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.expect('}')
            return {'type': 'loop', 'count': count, 'statements': statements}
        else:
            self.error("Loop requires { } block")
    
    def parse_function(self):
        """Parse function definition"""
        self.expect('FUNCTION')
        name_token = self.expect('IDENTIFIER')
        self.expect('(')
        
        params = []
        while self.current().type != ')':
            param_token = self.expect('IDENTIFIER')
            params.append(param_token.value)
            if self.current().value == ',':
                self.advance()
        self.expect(')')
        
        self.expect('{')
        statements = []
        while self.current().type != '}':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.expect('}')
        
        return {
            'type': 'function',
            'name': name_token.value,
            'params': params,
            'statements': statements
        }
    
    def parse_return(self):
        """Parse return statement"""
        self.expect('RETURN')
        value = None
        if self.current().value != ';':
            value = self.parse_expression()
        self.expect(';')
        return {'type': 'return', 'value': value}
    
    def parse_expression(self):
        """Parse expression (handles operator precedence)"""
        return self.parse_comparison()
    
    def parse_comparison(self):
        """Parse comparison operators"""
        left = self.parse_additive()
        
        while self.current().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.advance().value
            right = self.parse_additive()
            left = {'type': 'binary_op', 'op': op, 'left': left, 'right': right}
        
        return left
    
    def parse_additive(self):
        """Parse + and - operators"""
        left = self.parse_multiplicative()
        
        while self.current().value in ('+', '-'):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = {'type': 'binary_op', 'op': op, 'left': left, 'right': right}
        
        return left
    
    def parse_multiplicative(self):
        """Parse *, /, % operators"""
        left = self.parse_unary()
        
        while self.current().value in ('*', '/', '%'):
            op = self.advance().value
            right = self.parse_unary()
            left = {'type': 'binary_op', 'op': op, 'left': left, 'right': right}
        
        return left
    
    def parse_unary(self):
        """Parse unary operators"""
        if self.current().value in ('-', 'NOT'):
            op = self.advance().value
            expr = self.parse_unary()
            return {'type': 'unary_op', 'op': op, 'expr': expr}
        
        return self.parse_primary()
    
    def parse_primary(self):
        """Parse primary expressions"""
        token = self.current()
        
        if token.type == 'NUMBER':
            self.advance()
            return {'type': 'number', 'value': token.value}
        
        elif token.type == 'STRING':
            self.advance()
            return {'type': 'string', 'value': token.value}
        
        elif token.type == 'IDENTIFIER':
            name = token.value
            self.advance()
            
            # Function call
            if self.current().value == '(':
                self.advance()
                args = []
                while self.current().value != ')':
                    args.append(self.parse_expression())
                    if self.current().value == ',':
                        self.advance()
                self.expect(')')
                return {'type': 'function_call', 'name': name, 'args': args}
            
            return {'type': 'identifier', 'name': name}
        
        elif token.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect(')')
            return expr
        
        elif token.type == 'TRUE':
            self.advance()
            return {'type': 'boolean', 'value': True}
        
        elif token.type == 'FALSE':
            self.advance()
            return {'type': 'boolean', 'value': False}
        
        else:
            self.error(f"Unexpected token: {token.type}")

class Executor:
    """Execute AST"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.return_value = None
        self.should_return = False
    
    def execute(self, ast):
        """Execute program"""
        if ast['type'] == 'program':
            result = None
            for stmt in ast['statements']:
                result = self.execute_statement(stmt)
                if self.should_return:
                    break
            return result
    
    def execute_statement(self, stmt):
        """Execute single statement"""
        if stmt['type'] == 'print':
            value = self.eval_expr(stmt['value'])
            print(value)
            return value
        
        elif stmt['type'] == 'let':
            value = self.eval_expr(stmt['value'])
            self.variables[stmt['name']] = value
            return value
        
        elif stmt['type'] == 'if':
            condition = self.eval_expr(stmt['condition'])
            if self.is_truthy(condition):
                result = None
                for s in stmt['statements']:
                    result = self.execute_statement(s)
                    if self.should_return:
                        break
                return result
        
        elif stmt['type'] == 'loop':
            count_val = self.eval_expr(stmt['count'])
            try:
                count = int(count_val)
            except (ValueError, TypeError):
                raise TypeError(f"Loop count must be number, got {count_val}")
            
            result = None
            for i in range(count):
                for s in stmt['statements']:
                    result = self.execute_statement(s)
                    if self.should_return:
                        break
                if self.should_return:
                    break
            return result
        
        elif stmt['type'] == 'function':
            self.functions[stmt['name']] = stmt
            return None
        
        elif stmt['type'] == 'return':
            self.return_value = self.eval_expr(stmt['value']) if stmt['value'] else None
            self.should_return = True
            return self.return_value
    
    def eval_expr(self, expr):
        """Evaluate expression"""
        if expr['type'] == 'number':
            return expr['value']
        
        elif expr['type'] == 'string':
            return expr['value']
        
        elif expr['type'] == 'boolean':
            return expr['value']
        
        elif expr['type'] == 'identifier':
            name = expr['name']
            if name not in self.variables:
                raise NameError(f"Variable '{name}' is not defined")
            return self.variables[name]
        
        elif expr['type'] == 'binary_op':
            left = self.eval_expr(expr['left'])
            right = self.eval_expr(expr['right'])
            op = expr['op']
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif op == '%':
                return left % right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
            else:
                raise ValueError(f"Unknown operator: {op}")
        
        elif expr['type'] == 'unary_op':
            operand = self.eval_expr(expr['expr'])
            if expr['op'] == '-':
                return -operand
            elif expr['op'] == 'NOT':
                return not self.is_truthy(operand)
            else:
                raise ValueError(f"Unknown unary operator: {expr['op']}")
        
        elif expr['type'] == 'function_call':
            return self.call_function(expr['name'], expr['args'])
        
        else:
            raise ValueError(f"Unknown expression type: {expr['type']}")
    
    def call_function(self, name, args):
        """Call a function"""
        if name not in self.functions:
            raise NameError(f"Function '{name}' is not defined")
        
        func = self.functions[name]
        params = func['params']
        
        if len(args) != len(params):
            raise ValueError(f"Function '{name}' expects {len(params)} args, got {len(args)}")
        
        # Save current variables (function scope)
        saved_vars = self.variables.copy()
        
        # Bind parameters
        for i, param in enumerate(params):
            self.variables[param] = self.eval_expr(args[i])
        
        # Execute function body
        self.should_return = False
        result = None
        for stmt in func['statements']:
            result = self.execute_statement(stmt)
            if self.should_return:
                break
        
        # Restore variables (function scope ends)
        self.variables = saved_vars
        self.should_return = False
        
        return result if result is not None else None
    
    def is_truthy(self, value):
        """Determine if value is truthy"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)

def run_hypercode(code: str):
    """Run HyperCode program"""
    # Tokenize
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    # Parse
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Execute
    executor = Executor()
    executor.execute(ast)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python hypercode_interpreter_v2.py <file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
        run_hypercode(code)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except (SyntaxError, NameError, TypeError, ValueError, ZeroDivisionError) as e:
        print(f"❌ {type(e).__name__}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
