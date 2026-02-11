#!/usr/bin/env python3
"""
Test suite for HyperCode Tokenizer
Tests basic tokenization of HyperCode syntax
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypercode_interpreter import tokenize

def test_print_statement():
    """Test print statement tokenization"""
    code = 'print "Hello";'
    tokens = tokenize(code)
    assert 'PRINT' in tokens
    assert 'STRING' in tokens
    assert ';' in tokens
    print("✅ test_print_statement passed")

def test_let_statement():
    """Test variable declaration"""
    code = 'let x = 5;'
    tokens = tokenize(code)
    assert 'LET' in tokens
    assert 'IDENTIFIER' in tokens
    assert 'NUMBER' in tokens
    assert '=' in tokens
    print("✅ test_let_statement passed")

def test_number_tokenization():
    """Test number parsing"""
    code = 'let num = 42;'
    tokens = tokenize(code)
    assert any('42' in str(t) for t in tokens)
    print("✅ test_number_tokenization passed")

def test_string_tokenization():
    """Test string parsing"""
    code = 'print "HyperCode";'
    tokens = tokenize(code)
    assert 'STRING' in tokens
    print("✅ test_string_tokenization passed")

def test_if_statement():
    """Test conditional tokenization"""
    code = 'if x > 5 print "yes";'
    tokens = tokenize(code)
    assert 'IF' in tokens
    assert '>' in tokens
    print("✅ test_if_statement passed")

def test_comment_handling():
    """Test comment tokenization"""
    code = '# This is a comment\nprint "test";'
    tokens = tokenize(code)
    # Comments should be skipped
    assert 'PRINT' in tokens
    print("✅ test_comment_handling passed")

def test_whitespace_handling():
    """Test whitespace normalization"""
    code = '  let   x   =   10   ;  '
    tokens = tokenize(code)
    assert 'LET' in tokens
    assert 'IDENTIFIER' in tokens
    print("✅ test_whitespace_handling passed")

if __name__ == '__main__':
    print("\n🤪 Running Tokenizer Tests...\n")
    test_print_statement()
    test_let_statement()
    test_number_tokenization()
    test_string_tokenization()
    test_if_statement()
    test_comment_handling()
    test_whitespace_handling()
    print("\n✨ All tokenizer tests passed!\n")
