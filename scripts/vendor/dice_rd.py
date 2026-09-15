"""Dice! RD-inspired local Python adaptation, AGPL-3.0-or-later.

Copyright (C) 2018-2021 w4123; 2019-2025 String.Empty.
Local adaptation (2026): strict recursive parser, OS randomness, all-face evidence,
bounded expansion, keep-low, parentheses and rational arithmetic. This is NOT the
upstream DLL or a byte-for-byte behavioral emulation. See dice_source/upstream.json
and dice_source/LICENSE for source pin and full license. No warranty.
"""
import re
import secrets
import uuid
from datetime import datetime, timezone
from fractions import Fraction


TOKEN = re.compile(r'(?:\d*d(?:\d+|f)?(?:[kq]\d*)?|[bp]\d*|\d+|[()+*/-])', re.I)


class Expression:
    def __init__(self, text, default=100):
        text = text.lower().replace(' ', '').replace('x', '*') or 'd'
        if len(text) > 500 or not 2 <= default <= 1000:
            raise ValueError('Expression/default die outside bounds')
        self.tokens = TOKEN.findall(text)
        if ''.join(self.tokens) != text: raise ValueError('Unsupported expression token')
        self.i, self.default, self.draws = 0, default, 0
        self.tree = self.parse()
        if self.i != len(self.tokens): raise ValueError('Trailing expression tokens')
        if self.draws > 1000: raise ValueError('At most 1000 dice per expression')

    def parse(self, minimum=0, depth=0):
        if depth > 40 or self.i >= len(self.tokens): raise ValueError('Incomplete/deep expression')
        token = self.tokens[self.i]; self.i += 1
        if token in ('+', '-'):
            node = ('unary', token, self.parse(3, depth + 1))
        elif token == '(':
            node = self.parse(0, depth + 1)
            if self.i >= len(self.tokens) or self.tokens[self.i] != ')': raise ValueError('Missing )')
            self.i += 1
        elif token.isdecimal():
            if len(token) > 9: raise ValueError('Integer too large')
            node = ('constant', int(token))
        elif token[0] in 'bp':
            count = int(token[1:] or 1)
            if not 1 <= count <= 2: raise ValueError('CoC extra dice limited to 1..2')
            self.draws += count + 2
            node = ('percentile', token[0], count)
        else:
            m = re.fullmatch(r'(\d*)d(\d*|f)(?:([kq])(\d*))?', token)
            if not m: raise ValueError('Expected a number or die')
            n = int(m[1] or (4 if m[2] == 'f' else 1))
            sides = 3 if m[2] == 'f' else int(m[2] or self.default)
            keep = int(m[4] or 1) if m[3] else n
            if not 1 <= n <= 100 or not 2 <= sides <= 1000 or not 1 <= keep <= n:
                raise ValueError('Dice count, faces or keep count outside bounds')
            self.draws += n
            node = ('dice', n, sides, m[2] == 'f', m[3], keep)
        while self.i < len(self.tokens):
            op = self.tokens[self.i]; precedence = {'+': 1, '-': 1, '*': 2, '/': 2}.get(op, -1)
            if precedence < minimum: break
            self.i += 1
            node = ('binary', op, node, self.parse(precedence + 1, depth + 1))
        return node

    def evaluate(self, maximum=False):
        evidence = []
        def visit(node):
            kind = node[0]
            if kind == 'constant': return Fraction(node[1])
            if kind == 'unary': return visit(node[2]) * (-1 if node[1] == '-' else 1)
            if kind == 'binary':
                a, b = visit(node[2]), visit(node[3])
                if node[1] == '+': value = a + b
                elif node[1] == '-': value = a - b
                elif node[1] == '*': value = a * b
                else:
                    if b == 0: raise ValueError('Division by zero')
                    value = a / b
                if abs(value) > 10**12: raise ValueError('Arithmetic result too large')
                return value
            if kind == 'percentile':
                if maximum: raise ValueError('Maximum percentile not supported here')
                units = secrets.randbelow(10)
                tens = [secrets.randbelow(10) for _ in range(node[2] + 1)]
                candidates = [(x * 10 + units) or 100 for x in tens]
                value = (min if node[1] == 'b' else max)(candidates)
                evidence.append({'kind': node[1], 'units': units, 'tens': tens, 'candidates': candidates, 'total': value})
                return Fraction(value)
            _, n, sides, fudge, mode, keep = node
            raw = [(sides if maximum else secrets.randbelow(sides) + 1) - (2 if fudge else 0) for _ in range(n)]
            selected = sorted(range(n), key=lambda i: raw[i], reverse=mode != 'q')[:keep]
            value = sum(raw[i] for i in selected)
            evidence.append({'kind': 'fudge' if fudge else 'dice', 'faces': sides, 'raw': raw, 'kept_indices': selected, 'total': value})
            return Fraction(value)
        value = visit(self.tree)
        return {'total': value.numerator if value.denominator == 1 else float(value),
                'exact': str(value), 'dice': evidence}


def roll(text, default=100):
    parts = text.split('#')
    if len(parts) > 2: raise ValueError('Use count#expression')
    if len(parts) == 2:
        if not parts[0].strip().isdecimal(): raise ValueError('Invalid repeat count')
        count, expression = int(parts[0]), parts[1]
    else: count, expression = 1, text
    if not 1 <= count <= 100: raise ValueError('Repeat count must be 1..100')
    parsed = Expression(expression, default)
    if parsed.draws * count > 1000: raise ValueError('At most 1000 dice per request')
    return {'event_id': str(uuid.uuid4()), 'utc': datetime.now(timezone.utc).isoformat(),
            'expression': text, 'results': [parsed.evaluate() for _ in range(count)],
            'randomness': 'OS secrets; actual roll', 'engine': 'dice-rd-python-adaptation-v1'}


def pool(count=10, explode=10, success=8, sides=10, modifier=0):
    if not 1 <= count <= 500 or not 2 <= sides <= 1000 or not 2 <= explode <= sides or not 1 <= success <= sides:
        raise ValueError('Pool bounds: count1..500, faces2..1000, explosion2..faces, success1..faces')
    waves, remaining, hits, total = [], count, 0, 0
    while remaining:
        if total + remaining > 5000: raise ValueError('Explosion limit exceeded; no result committed')
        faces = [secrets.randbelow(sides) + 1 for _ in range(remaining)]
        waves.append(faces); total += remaining
        hits += sum(x >= success for x in faces)
        remaining = sum(x >= explode for x in faces)
    return {'waves': waves, 'successes': hits, 'modifier': modifier, 'total': hits + modifier,
            'randomness': 'OS secrets; actual roll'}
