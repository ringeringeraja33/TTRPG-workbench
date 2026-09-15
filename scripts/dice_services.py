"""Bounded local JSON decks and timer queries (AGPL-3.0-or-later).

No scripts or network services."""
import secrets


def deck_entries(value):
    if isinstance(value, list):
        return value, None  # Existing flat decks remain readable.
    if not isinstance(value, dict) or set(value) != {'source', 'entries'}:
        raise ValueError('Deck must be an array or {source, entries}')
    if not isinstance(value['source'], str) or not value['source'].strip() or len(value['source']) > 1000:
        raise ValueError('Deck source must be a nonempty bibliography, at most1000 characters')
    return value['entries'], value['source']


def validate_decks(decks):
    if len(decks) > 1000:
        raise ValueError('At most1000 local decks')
    edges = {}
    total = 0
    for name, value in decks.items():
        if not isinstance(name, str) or not name or len(name) > 100 or any(c.isspace() for c in name):
            raise ValueError('Deck name must be a nonempty token, at most100 characters')
        entries, _ = deck_entries(value)
        if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
            raise ValueError('Deck requires1..1000 entries')
        total += len(entries)
        if total > 10000:
            raise ValueError('At most10000 entries across local decks')
        edges[name] = []
        for entry in entries:
            if isinstance(entry, str):
                if len(entry) > 5000:
                    raise ValueError('Deck text exceeds5000 characters')
                continue
            if not isinstance(entry, dict) or not ({'text'} <= set(entry) <= {'text', 'weight'} or
                                                   {'ref'} <= set(entry) <= {'ref', 'weight'}):
                raise ValueError('Entry must be text or {text|ref, weight?}')
            weight = entry.get('weight', 1)
            if type(weight) is not int or not 1 <= weight <= 1000:
                raise ValueError('Weight must be an integer1..1000')
            if 'text' in entry:
                if not isinstance(entry['text'], str) or len(entry['text']) > 5000:
                    raise ValueError('Invalid entry text')
            else:
                if not isinstance(entry['ref'], str) or entry['ref'] not in decks:
                    raise ValueError('Referenced deck missing; install children first')
                edges[name].append(entry['ref'])
    depths = {}

    def visit(name, active):
        if name in active:
            raise ValueError('Cyclic deck reference')
        if len(active) >= 25:
            raise ValueError('Deck nesting exceeds25')
        if name in depths:
            return depths[name]
        depth = 1 + max((visit(child, active | {name}) for child in edges[name]), default=0)
        if depth > 25:
            raise ValueError('Deck nesting exceeds25')
        depths[name] = depth
        return depth

    for name in decks:
        visit(name, set())


def draw_deck(decks, name, count):
    validate_decks(decks)  # Reject bad graphs before consuming randomness.
    if name not in decks or type(count) is not int or not 1 <= count <= 100:
        raise ValueError('Existing deck and count1..100 required')
    draws, paths = [], []
    for _ in range(count):
        current, path = name, []
        while True:
            entries, source = deck_entries(decks[current])
            weights = [e.get('weight', 1) if isinstance(e, dict) else 1 for e in entries]
            ticket = secrets.randbelow(sum(weights))
            remaining = ticket
            for index, weight in enumerate(weights):
                if remaining < weight:
                    break
                remaining -= weight
            path.append({'deck': current, 'index': index, 'ticket': ticket,
                         'weight_total': sum(weights), 'source': source})
            entry = entries[index]
            if isinstance(entry, dict) and 'ref' in entry:
                current = entry['ref']
            else:
                draws.append(entry['text'] if isinstance(entry, dict) else entry)
                paths.append(path)
                break
    return {'indices': [p[0]['index'] for p in paths], 'draws': draws, 'paths': paths,
            'replacement': True, 'randomness': 'OS secrets; actual weighted draw'}


def actor_timers(state, actor, now, due_only=False):
    return {key: dict(value, status=value.get('status', 'pending'))
            for key, value in sorted(state['clocks'].items(), key=lambda x: (x[1]['due'], x[0]))
            if value['owner'] == actor and
            (not due_only or (value.get('status', 'pending') == 'pending' and value['due'] <= now))}
