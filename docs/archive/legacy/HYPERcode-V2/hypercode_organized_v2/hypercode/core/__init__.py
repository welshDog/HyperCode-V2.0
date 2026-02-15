# src/hypercode/core/__init__.py
"""
HyperCode Core Module

This module contains the core components of the HyperCode language implementation,
including the lexer, parser, and abstract syntax tree (AST) definitions.
"""

from .tokens import Token, TokenType
from .lexer import Lexer, LexerError, tokenize
from .parser import Parser, ParserError
from .ast import (
    Node, Expression, Literal, Var, Binary, Call,
    Statement, ExpressionStmt, VarDecl, Program
)

__all__ = [
    # Tokens
    'Token', 'TokenType',
    # Lexer
    'Lexer', 'LexerError', 'tokenize',
    # Parser
    'Parser', 'ParserError',
    # AST
    'Node', 'Expression', 'Literal', 'Var', 'Binary', 'Call',
    'Statement', 'ExpressionStmt', 'VarDecl', 'Program'
]
