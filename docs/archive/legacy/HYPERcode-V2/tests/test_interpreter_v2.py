#!/usr/bin/env python3
"""
Tests for HyperCode Interpreter v2
Covers: variables, conditionals, loops, functions
"""

import pytest
from hypercode_interpreter_v2 import Tokenizer, Parser, Executor

class TestTokenizer:
    """Test tokenization"""
    
    def test_keywords(self):
        tokenizer = Tokenizer("let print if loop function")
        tokens = tokenizer.tokenize()
        types = [t.type for t in tokens[:-1]]  # exclude EOF
        assert 'LET' in types
        assert 'PRINT' in types
    
    def test_strings(self):
        tokenizer = Tokenizer('"hello world"')
        tokens = tokenizer.tokenize()
        assert tokens[0].type == 'STRING'
        assert tokens[0].value == 'hello world'
    
    def test_numbers(self):
        tokenizer = Tokenizer('42 3.14 -5')
        tokens = tokenizer.tokenize()
        assert tokens[0].value == 42
        assert tokens[1].value == 3.14

class TestParser:
    """Test parsing"""
    
    def test_print_statement(self):
        code = 'print "hello";'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast['statements'][0]['type'] == 'print'
    
    def test_let_statement(self):
        code = 'let x = 5;'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast['statements'][0]['type'] == 'let'
        assert ast['statements'][0]['name'] == 'x'
    
    def test_if_statement(self):
        code = 'if x > 5 print "big";'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast['statements'][0]['type'] == 'if'
    
    def test_loop_statement(self):
        code = 'loop(3) { print "hi"; }'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast['statements'][0]['type'] == 'loop'
    
    def test_function_definition(self):
        code = 'function add(a, b) { return a + b; }'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast['statements'][0]['type'] == 'function'
        assert ast['statements'][0]['name'] == 'add'

class TestExecutor:
    """Test execution"""
    
    def setup_method(self):
        """Reset executor before each test"""
        self.executor = Executor()
    
    def run_code(self, code):
        """Helper to run code"""
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.executor.execute(ast)
    
    def test_print_string(self, capsys):
        self.run_code('print "hello";')
        captured = capsys.readouterr()
        assert "hello" in captured.out
    
    def test_print_number(self, capsys):
        self.run_code('print 42;')
        captured = capsys.readouterr()
        assert "42" in captured.out
    
    def test_variable_assignment(self):
        self.run_code('let x = 10;')
        assert self.executor.variables['x'] == 10
    
    def test_variable_usage(self, capsys):
        self.run_code('let x = 5; print x;')
        captured = capsys.readouterr()
        assert "5" in captured.out
    
    def test_arithmetic(self):
        self.run_code('let result = 10 + 5;')
        assert self.executor.variables['result'] == 15
    
    def test_string_concatenation(self, capsys):
        self.run_code('print "hello" + " " + "world";')
        captured = capsys.readouterr()
        assert "hello world" in captured.out
    
    def test_comparison_equal(self):
        self.run_code('let x = 5 == 5;')
        assert self.executor.variables['x'] == True
    
    def test_comparison_not_equal(self):
        self.run_code('let x = 5 != 3;')
        assert self.executor.variables['x'] == True
    
    def test_if_true_condition(self, capsys):
        self.run_code('if 5 > 3 print "yes";')
        captured = capsys.readouterr()
        assert "yes" in captured.out
    
    def test_if_false_condition(self, capsys):
        self.run_code('if 3 > 5 print "no";')
        captured = capsys.readouterr()
        assert "no" not in captured.out
    
    def test_if_block(self, capsys):
        code = '''if 10 > 5 {
            print "block1";
            print "block2";
        }'''
        self.run_code(code)
        captured = capsys.readouterr()
        assert "block1" in captured.out
        assert "block2" in captured.out
    
    def test_loop_basic(self, capsys):
        code = 'loop(3) { print "hi"; }'
        self.run_code(code)
        captured = capsys.readouterr()
        assert captured.out.count("hi") == 3
    
    def test_loop_with_variable(self, capsys):
        code = '''let i = 0;
loop(3) {
  print i;
  let i = i + 1;
}'''
        self.run_code(code)
        captured = capsys.readouterr()
        assert "0" in captured.out
        assert "1" in captured.out
        assert "2" in captured.out
    
    def test_function_definition(self):
        self.run_code('function greet(name) { print name; }')
        assert 'greet' in self.executor.functions
    
    def test_function_call(self, capsys):
        code = '''function greet(name) {
            print "hello ";
            print name;
        }
        greet("world");'''
        self.run_code(code)
        captured = capsys.readouterr()
        assert "hello" in captured.out
        assert "world" in captured.out
    
    def test_function_with_arithmetic(self, capsys):
        code = '''function double(x) {
            let result = x * 2;
            print result;
        }
        double(5);'''
        self.run_code(code)
        captured = capsys.readouterr()
        assert "10" in captured.out
    
    def test_function_return(self):
        code = '''function add(a, b) {
            let sum = a + b;
            return sum;
        }'''
        self.run_code(code)
        # Function should be defined
        assert 'add' in self.executor.functions
    
    def test_division_by_zero(self):
        with pytest.raises(ValueError):
            self.run_code('let x = 10 / 0;')
    
    def test_undefined_variable(self):
        with pytest.raises(NameError):
            self.run_code('print undefined_var;')
    
    def test_undefined_function(self):
        with pytest.raises(NameError):
            self.run_code('undefined_func(5);')

class TestComplexPrograms:
    """Test real programs"""
    
    def setup_method(self):
        self.executor = Executor()
    
    def run_code(self, code):
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.executor.execute(ast)
    
    def test_hello_world(self, capsys):
        self.run_code('print "Hello, World!";')
        captured = capsys.readouterr()
        assert "Hello, World!" in captured.out
    
    def test_fizzbuzz(self, capsys):
        """Test FizzBuzz algorithm"""
        code = '''let i = 1;
loop(3) {
  if i % 3 == 0 print "Fizz";
  if i % 2 == 0 print "Buzz";
  let i = i + 1;
}'''
        self.run_code(code)
        captured = capsys.readouterr()
        # Should have some output
        assert len(captured.out) > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
