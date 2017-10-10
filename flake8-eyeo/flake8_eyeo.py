# This file is part of Adblock Plus <https://adblockplus.org/>,
# Copyright (C) 2006-present eyeo GmbH
#
# Adblock Plus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Adblock Plus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.

import ast
import re
import tokenize
import sys
import collections

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import pkg_resources

try:
    ascii
except NameError:
    ascii = repr

__version__ = pkg_resources.get_distribution('flake8-eyeo').version

DISCOURAGED_APIS = {
    're.match': 're.search',
    'codecs.open': 'io.open',
}

ESSENTIAL_BUILTINS = set(dir(builtins)) - {'apply', 'buffer', 'coerce',
                                           'intern', 'file'}

LEAVE_BLOCK = (ast.Return, ast.Raise, ast.Continue, ast.Break)
VOLATILE = object()


def evaluate(node):
    try:
        return eval(compile(ast.Expression(node), '', 'eval'), {})
    except Exception:
        return VOLATILE


def is_const(node):
    return evaluate(node) is not VOLATILE


def get_identifier(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return '{}.{}'.format(node.value.id, node.attr)


def get_statement(node):
    return type(node).__name__.lower()


class TreeVisitor(ast.NodeVisitor):
    Scope = collections.namedtuple('Scope', ['node', 'names', 'globals'])

    def __init__(self):
        self.errors = []
        self.scope_stack = []

    def _visit_block(self, nodes, block_required=False,
                     nodes_required=True, docstring=False,
                     can_have_unused_expr=False):
        pass_node = None
        has_non_pass = False
        leave_node = None
        dead_code = False

        for i, node in enumerate(nodes):
            if isinstance(node, ast.Pass):
                pass_node = node
            else:
                has_non_pass = True

            if leave_node and not dead_code:
                dead_code = True
                statement = get_statement(leave_node)
                self.errors.append((node, 'A202 dead code after '
                                          '{}'.format(statement)))

            if isinstance(node, LEAVE_BLOCK):
                leave_node = node

            if can_have_unused_expr or not isinstance(node, ast.Expr):
                continue
            if docstring and i == 0 and isinstance(node.value, ast.Str):
                continue
            if isinstance(node.value, (ast.Call, ast.Yield)):
                continue

            self.errors.append((node, 'A203 unused expression'))

        if pass_node:
            if not nodes_required or len(nodes) > 1:
                self.errors.append((pass_node, 'A204 redundant '
                                               'pass statement'))

            if not block_required and not has_non_pass:
                self.errors.append((pass_node, 'A205 empty block'))

    def _check_redundant_else(self, node, handlers, clause):
        if not node.orelse:
            return

        for handler in handlers:
            for child in handler.body:
                if isinstance(child, LEAVE_BLOCK):
                    leave_node = child
                    break
            else:
                return

        statement = get_statement(leave_node)
        self.errors.append((node.orelse[0],
                            'A206 Extraneous else statement after {} '
                            'in {}-clause'.format(statement, clause)))

    def visit_If(self, node):
        self._visit_block(node.body, block_required=bool(node.orelse))
        self._visit_block(node.orelse)
        self._check_redundant_else(node, [node], 'if')
        self.generic_visit(node)

    def visit_Try(self, node):
        self._visit_block(node.body, can_have_unused_expr=bool(node.handlers))
        self._visit_block(node.orelse)
        self._visit_block(node.finalbody)
        self._check_redundant_else(node, node.handlers, 'except')
        self.generic_visit(node)

    def visit_TryExcept(self, node):
        self._visit_block(node.body, can_have_unused_expr=True)
        self._visit_block(node.orelse)
        self._check_redundant_else(node, node.handlers, 'except')
        self.generic_visit(node)

    def visit_TryFinally(self, node):
        self._visit_block(node.body)
        self._visit_block(node.finalbody)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self._visit_block(node.body, block_required=True)
        self.generic_visit(node)

    def _visit_stored_name(self, node, name):
        scope = self.scope_stack[-1]
        scope.names.add(name)

        if name in ESSENTIAL_BUILTINS and isinstance(scope.node,
                                                     ast.FunctionDef):
            self.errors.append((node, 'A302 redefined built-in ' + name))

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Param)):
            self._visit_stored_name(node, node.id)

    def visit_arg(self, node):
        self._visit_stored_name(node, node.arg)

    def _visit_with_scope(self, node):
        scope = self.Scope(node, names=set(), globals=[])
        self.scope_stack.append(scope)
        self.generic_visit(node)
        del self.scope_stack[-1]
        return scope

    def visit_Module(self, node):
        self._visit_block(node.body, block_required=True,
                          nodes_required=False, docstring=True)
        self._visit_with_scope(node)

    def visit_FunctionDef(self, node):
        self._visit_stored_name(node, node.name)
        self._visit_block(node.body, block_required=True, docstring=True)

        scope = self._visit_with_scope(node)
        global_names = set()

        for declaration in scope.globals:
            for name in declaration.names:
                if name not in scope.names or name in global_names:
                    statement = get_statement(declaration)
                    self.errors.append((declaration,
                                        'A201 redundant {} declaration for '
                                        '{}'.format(statement, name)))
                else:
                    global_names.add(name)

    visit_ClassDef = visit_FunctionDef

    def visit_Global(self, node):
        scope = self.scope_stack[-1]
        scope.globals.append(node)

        if isinstance(scope.node, ast.Module):
            statement = get_statement(node)
            self.errors.append((node, 'A201 {} declaration on '
                                      'top-level'.format(statement)))

    visit_Nonlocal = visit_Global

    def _visit_iter(self, node):
        if isinstance(node, (ast.Tuple, ast.Set)):
            self.errors.append((node, 'A101 use lists for data '
                                      'that have order'))

    def visit_comprehension(self, node):
        self._visit_iter(node.iter)
        self.generic_visit(node)

    def visit_For(self, node):
        self._visit_iter(node.iter)
        self._visit_block(node.body, block_required=True)
        self._visit_block(node.orelse)
        self.generic_visit(node)

    def visit_While(self, node):
        self._visit_block(node.body, block_required=True)
        self._visit_block(node.orelse)
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Str):
            self.errors.append((node, 'A107 use format() instead of '
                                      '% operator for string formatting'))

        multi_addition = (isinstance(node.op, ast.Add) and
                          isinstance(node.left, ast.BinOp) and
                          isinstance(node.left.op, ast.Add))
        if multi_addition and (isinstance(node.left.left, ast.Str) or
                               isinstance(node.left.right, ast.Str) or
                               isinstance(node.right, ast.Str)):
            self.errors.append((node, 'A108 use format() instead of '
                                      '+ operator when concatenating '
                                      'more than two strings'))

        self.generic_visit(node)

    def visit_Compare(self, node):
        left = node.left
        single = len(node.ops) == 1

        for op, right in zip(node.ops, node.comparators):
            membership = isinstance(op, (ast.In, ast.NotIn))
            symmetric = isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot))

            if membership and isinstance(right, (ast.Tuple, ast.List)):
                self.errors.append((right, 'A102 use sets for distinct '
                                           'unordered data'))

            consts_first = single and not membership or symmetric
            if consts_first and is_const(left) and not is_const(right):
                self.errors.append((left, 'A103 yoda condition'))

            left = right

        self.generic_visit(node)

    def _check_deprecated(self, node, name):
        substitute = DISCOURAGED_APIS.get(name)
        if substitute:
            self.errors.append((node, 'A301 use {}() instead of '
                                      '{}()'.format(substitute, name)))

    def visit_Call(self, node):
        func = get_identifier(node.func)
        arg = next(iter(node.args), None)
        redundant_literal = False

        if isinstance(arg, ast.Lambda):
            if len(node.args) == 2 and func in {'map', 'filter',
                                                'imap', 'ifilter',
                                                'itertools.imap',
                                                'itertools.ifilter'}:
                self.errors.append((node, 'A104 use a comprehension '
                                          'instead of calling {}() with '
                                          'lambda function'.format(func)))
        elif isinstance(arg, (ast.List, ast.Tuple)):
            if func == 'dict':
                redundant_literal = all(isinstance(elt, (ast.Tuple, ast.List))
                                        for elt in arg.elts)
            else:
                redundant_literal = func in {'list', 'set', 'tuple'}
        elif isinstance(arg, (ast.ListComp, ast.GeneratorExp)):
            if func == 'dict':
                redundant_literal = isinstance(arg.elt, (ast.Tuple, ast.List))
            else:
                redundant_literal = func in {'list', 'set'}

        if redundant_literal:
            self.errors.append((node, 'A105 use a {0} literal or '
                                      'comprehension instead of calling '
                                      '{0}()'.format(func)))

        self._check_deprecated(node, func)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self._visit_stored_name(node, alias.asname or alias.name)

            if hasattr(node, 'module'):
                self._check_deprecated(node, '{}.{}'.format(node.module,
                                                            alias.name))

    visit_ImportFrom = visit_Import

    def visit_Assign(self, node):
        if isinstance(node.value, ast.BinOp) and len(node.targets) == 1:
            target = node.targets[0]
            left_is_target = (isinstance(target, ast.Name) and
                              isinstance(node.value.left, ast.Name) and
                              target.id == node.value.left.id)
            if left_is_target:
                self.errors.append((node, 'A106 use augment assignment, '
                                          'e.g. x += y instead x = x + y'))
        self.generic_visit(node)

    def _visit_hash_keys(self, nodes, what):
        keys = []
        for node in nodes:
            key = evaluate(node)
            if key is VOLATILE:
                continue

            if key in keys:
                self.errors.append((node, 'A207 duplicate ' + what))
                continue

            keys.append(key)

    def visit_Dict(self, node):
        self._visit_hash_keys(node.keys, 'key in dict')

    def visit_Set(self, node):
        self._visit_hash_keys(node.elts, 'item in set')


def check_ast(tree):
    visitor = TreeVisitor()
    visitor.visit(tree)

    for node, error in visitor.errors:
        yield (node.lineno, node.col_offset, error, None)


def check_non_default_encoding(physical_line, line_number):
    if line_number <= 2 and re.search(r'^\s*#.*coding[:=]', physical_line):
        return (0, 'A303 non-default file encoding')


def check_quotes(logical_line, tokens, previous_logical, checker_state):
    first_token = True

    token_strings = [t[1] for t in tokens]
    future_import = token_strings[:3] == ['from', '__future__', 'import']

    if future_import and 'unicode_literals' in token_strings:
        checker_state['has_unicode_literals'] = True

    for kind, token, start, end, _ in tokens:
        if kind == tokenize.INDENT or kind == tokenize.DEDENT:
            continue

        if kind == tokenize.STRING:
            match = re.search(r'^([rub]*)([\'"]{1,3})(.*)\2$',
                              token, re.IGNORECASE | re.DOTALL)
            prefixes, quote, text = match.groups()
            prefixes = prefixes.lower()

            if 'u' in prefixes:
                yield (start, 'A112 use "from __future__ import '
                              'unicode_literals" instead of '
                              'prefixing literals with "u"')

            if first_token and re.search(r'^(?:(?:def|class)\s|$)',
                                         previous_logical):
                pass  # Ignore docstrings
            elif start[0] != end[0]:
                pass  # Ignore multiline strings
            elif 'r' in prefixes:
                if quote != "'" and not (quote == '"' and "'" in text):
                    yield (start, 'A110 use single quotes for raw string')
            else:
                prefix = ''
                if sys.version_info[0] >= 3:
                    if 'b' in prefixes:
                        prefix = 'b'
                else:
                    u_literals = checker_state.get('has_unicode_literals')
                    if 'u' in prefixes or u_literals and 'b' not in prefixes:
                        prefix = 'u'

                literal = '{0}{1}{2}{1}'.format(prefix, quote, text)
                if ascii(eval(literal)) != literal:
                    yield (start, "A110 string literal doesn't match "
                                  '{}()'.format(ascii.__name__))

        first_token = False


def check_redundant_parenthesis(logical_line, tokens):
    start_line = tokens[0][2][0]
    level = 0
    statement = None

    for i, (kind, token, _, end, _) in enumerate(tokens):
        if kind == tokenize.INDENT or kind == tokenize.DEDENT:
            continue

        if statement is None:
            # logical line doesn't start with an if, elif or while statement
            if kind != tokenize.NAME or token not in {'if', 'elif', 'while'}:
                break

            # expression doesn't start with parenthesis
            next_token = tokens[i + 1]
            if next_token[:2] != (tokenize.OP, '('):
                break

            # expression is empty tuple
            if tokens[i + 2][:2] == (tokenize.OP, ')'):
                break

            statement = token
            pos = next_token[2]
            continue

        # expression ends on a different line, parenthesis are necessary
        if end[0] > start_line:
            break

        if kind == tokenize.OP:
            if token == ',':
                # expression is non-empty tuple
                if level == 1:
                    break
            elif token == '(':
                level += 1
            elif token == ')':
                level -= 1
                if level == 0:
                    # outer parenthesis closed before end of expression
                    if tokens[i + 1][:2] != (tokenize.OP, ':'):
                        break

                    return [(pos, 'A111 redundant parenthesis for {} '
                                  'statement'.format(statement))]

    return []


for checker in [check_ast, check_non_default_encoding,
                check_quotes, check_redundant_parenthesis]:
    checker.name = 'eyeo'
    checker.version = __version__
