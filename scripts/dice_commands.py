"""One command boundary parser shared by dispatch, policy and log export."""
from dataclasses import dataclass
import re

HEADS = set("kp help hiy set crule ral rcl rav rcv opposed coc card dnd name lookup magic5e magic3r 3ry 5ey rule dw pfy con getbook ti li bg gas tz dr nn st stc ra rc rb rp sc san en mark team npc monster ri init clue log des custom reply deck draw clock ob table strRoll rf rh r w ww ws".split())
COMPACT = {'r', 'rh', 'ra', 'rc', 'rb', 'rp', 'ral', 'rcl', 'nn', 'st', 'coc', 'dnd', 'w', 'ww', 'ws'}
SUBCOMMANDS = {
    'log': {'on','off','get','rm','list','tables'}, 'team': {'set','rm','clr','en','desc','hp','san'},
    'table': {'info','simple','secret','deck','ob'}, 'card': {'new','use','list'},
    'coc': {'show','take'}, 'crule': {'get','set'}, 'san': {'day','bout'},
    'init': {'set','rm','clr'}, 'ob': {'set','list','clr'},
    'deck': {'install','remove','list','help'}, 'draw': {'install','remove','list','help'},
    'clock': {'ack','cancel','list','poll'}, 'lookup': {'import'},
    'reply': {'enable','disable','publish','unpublish','set','input','rm','list'},
    'des': {'set','input','rm','list'}, 'custom': {'set','input','rm','list'},
    'st': {'show','get','export','list','rm','clr','lock','unlock','rename','cp'},
    'opposed': {'cancel'},
}

@dataclass(frozen=True)
class Command:
    text: str
    head: str = ''
    action: str = ''

    @property
    def is_roll(self):
        return self.head in {'r','rh','rf','ra','rc','rb','rp','ral','rcl','rav','rcv',
                             'ri','sc','en','w','ww','ws','coc','dnd'}

    @property
    def is_deck(self):
        return self.head in {'deck','draw','ti','li','bg','gas','tz','dr'}

    @property
    def private(self):
        return (self.head in {'npc','monster','des','custom','reply','clock','st','stc',
                              'card','nn','hiy','mark','init'} or
                self.head == 'team' and self.action == 'desc' or
                self.head == 'log' and self.action in {'get','tables'} or
                self.head == 'lookup' and self.action == 'import')


def split_word(text):
    parts = text.split(maxsplit=1)
    return (parts[0], parts[1] if len(parts) > 1 else '') if parts else ('', '')


def parse_command(text):
    text = text.strip()
    if text and text[0] in '。!！':
        text = '.' + text[1:]
    if not text.startswith('.'):
        return Command(text)
    body = text[1:]
    for head in sorted(HEADS, key=lambda x: (-len(x), x)):
        if not body.startswith(head):
            continue
        tail = body[len(head):]
        compact = bool(tail and not tail[0].isspace())
        if compact and head not in COMPACT:
            continue
        if compact and head in {'coc','dnd'} and not tail[0].isdigit():
            continue
        if compact and head in {'w','ww','ws'} and not re.fullmatch(r'[0-9akm+\-]+',tail):
            continue
        if compact:
            return Command('.'+head+tail,head)
        args = tail.strip()
        action = ''
        if head in SUBCOMMANDS and args:
            action, rest = split_word(args)
            if action not in SUBCOMMANDS[head]:
                return Command('.'+head+' '+args,head)
            if head == 'log' and action == 'tables' and rest:
                verb, value = split_word(rest)
                rest = verb + (' '+value if value else '')
            args = action + (' '+rest if rest else '')
        return Command('.'+head+(' '+args if args else ''),head,action)
    raise ValueError('Unsupported local command; use .help')


def audience_for(command, state, actor):
    if command.head == 'rh' or state['config'].get('secret') and command.is_roll:
        observers = state['observers'] if state['config'].get('ob',1) else []
        return list(dict.fromkeys([actor,*([state['gm']] if state['gm'] else []),*observers]))
    return [actor] if command.private else 'table'


def includes(audience, actor):
    return audience == 'table' or isinstance(audience,list) and actor in audience


def can_share(original, recipients):
    return original == 'table' or (isinstance(original,list) and isinstance(recipients,list)
                                   and set(recipients) <= set(original))
