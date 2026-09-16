"""Discoverable local tabletop command reference."""
import copy

COMMANDS = {'roll': {'summary': 'Actual dice with raw faces, kept dice and arithmetic.',
          'examples': ['.r3d6*5', '.r2d20k1', '.r2d20q1', '.r3#4d6k3', '.rf', '.rh1d100'],
          'limits': '100 dice per atom, 1000 per request, 2..1000 faces. Hidden results require a '
                    'private output file.'},
 'check': {'summary': 'CoC7 checks against recorded skills or explicit targets.',
           'examples': ['.rc 侦查', '.rc 60', '.rb 侦查', '.rp 2 侦查', '.rcl 60 3', '.rcv 60', '.hiy'],
           'limits': 'Core checks use .rc; .ra is an explicitly selected house profile. Outcomes '
                     'do not automatically apply consequences.'},
 'cards': {'summary': 'Persistent local cards and attribute-generation evidence.',
           'examples': ['.nn 阿达',
                        '.st STR60 INT70 HP12 侦查60',
                        '.st show灵感',
                        '.stc HP-1d3',
                        '.st export',
                        '.coc5',
                        '.coc show b1',
                        '.coc take b1 2 ada 阿达',
                        '.dnd 2'],
           'limits': 'Numeric storage is not a character legality audit. Creation age processing '
                     'and derived values remain separate.'},
 'team': {'summary': 'Keeper-controlled teams, NPCs and initiative.',
          'examples': ['.team set @p @q',
                       '.team',
                       '.team hp all 1d3',
                       '.npc st管家-HP10 侦查30',
                       '.ri +4 地精',
                       '.init'],
          'limits': 'Team updates are atomic; actor IDs identify local records.'},
 'table': {'summary': 'Keeper-controlled local table settings.',
           'examples': ['.kp',
                        '.table info',
                        '.table secret 1',
                        '.table deck 0',
                        '.table simple 1',
                        '.ob set keeper',
                        '.set 20'],
           'limits': 'Switches simple/secret/deck/ob accept only 0 or 1. Local operator controls '
                     'file access.'},
 'log': {'summary': 'Persistent session logs filtered by the recorded audience.',
         'examples': ['.log on 调查',
                      '.log off',
                      '.log list',
                      '.log get 调查',
                      '.log tables list 调查',
                      '.log tables get table1,table2 调查'],
         'limits': 'Export txt, clean-txt, html, json or docx using --export-log. Private entries '
                   'are filtered for the selected actor.'},
 'notes': {'summary': 'Local clues, scenes and opt-in exact text reminders.',
           'examples': ['.clue 门边有脚印',
                        '.des set 门厅|昏暗的灯光',
                        '.reply set 整理线索|核对证据来源',
                        '.reply enable 整理线索',
                        '.clock 60 收尾',
                        '.clock poll',
                        '.clock ack t1'],
           'limits': 'Timers persist locally; a running wait or later poll is required.'},
 'decks': {'summary': 'Source-attributed weighted and nested local random tables.',
           'examples': ['.deck install weather ["雨雾","晴朗"]', '.draw weather 2', '.deck list'],
           'limits': 'Draws are with replacement; local JSON data only. No executable table '
                     'scripts.'}}


def command_help(topic=''):
    if topic and topic not in COMMANDS:
        raise ValueError('Unknown help topic; choose: ' + ', '.join(COMMANDS))
    return {'reference':'references/dice-local.md',
            'topics':copy.deepcopy({topic:COMMANDS[topic]} if topic else COMMANDS)}
