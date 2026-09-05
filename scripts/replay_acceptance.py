"""20 declared simulated player turns per system; never a real-play transcript.

Uses the original Lockhouse scenario, deterministic test inputs, actual SQLite
writes, subprocess cold reads, and independent expected end-state assertions.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

import rules_math as rules
import session


ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert json.loads(path.read_text(encoding='utf-8')) == value


def resource(name, delta):
    return {'kind': 'resource', 'actor': 'pc1', 'resource': name, 'delta': delta}


def run(output, system):
    folder = output / system
    folder.mkdir(parents=True, exist_ok=False)
    state = json.loads((ROOT/'assets/templates/session-initial.json').read_text(encoding='utf-8'))
    if system == 'dnd':
        state['profile'] = {'system': 'D&D', 'edition': 'SRD5.2.1', 'options': {'multiclass': False}}
        state['actors']['pc1']['name'] = '艾琳'
        state['actors']['pc1']['resources'] = {'hp': {'value': 12, 'max': 12}, 'second_wind': {'value': 2, 'max': 2}, 'healer_kit': {'value': 10, 'max': 10}}
    else:
        state['actors']['pc1']['resources']['cash'] = {'value': 40, 'max': 40}
    state['private'] = {'next_actor': 'pc1', 'position': 'N1', 'test_fixture': True, 'secret': '管理员掩盖走私', 'san_day_start': 60, 'san_day_loss': 0}
    write(folder/'initial.json', state)
    db = folder/'campaign.sqlite'
    session.init(db, state)
    turns = [
        ('出示证件询问工人班次', '值班员递出值班记录，闸站位置已知。', 'N1'),
        ('仔细核对最后一行记录', '找到改写痕迹。', 'N1'),
        ('问清安全返回的路线', '沿岸高路可返回值班室。', 'N1'),
        ('沿主路前往仓房', '仓房门锁着，门下有新泥。', 'N2'),
        ('寻找夹层账本', '没有找到夹层，留下了翻动迹象。', 'N2'),
        ('绕屋寻找其他入口', '通风口传来敲击声，可沿步道接近。', 'N2'),
        ('尝试走湿栏杆捷径', '失足擦伤2点HP，退回安全步道。', 'N3'),
        ('先处理自己的擦伤', '处理伤口后继续行动。', 'N3'),
        ('隔着门询问被困者', '工人说门从外面上锁，管理员取走了钥匙。', 'N4'),
        ('尝试撬开门闩', '门闩松开，工人可以出来。', 'N4'),
        ('让工人指出账本的位置', '账本藏在仓房窗下夹层。', 'N4'),
        ('返回夹层取出账本', '按具体位置取出账本，无需重复猜测检定。', 'N2'),
        ('向管理员展示证据并要求解释', '管理员试图拿回账本，已逼近一步。', 'N3'),
        ('挡住管理员并要求放下棍子', '管理员挥棍，角色防御；进入明确战斗顺序。', 'N3'),
        ('继续保护账本并闪避', '本轮防御结算。', 'N3'),
        ('退到有退路的地方要求停手', '管理员停手；证据已无法夺回，选择求和。', 'N3'),
        ('带工人沿高路离开', '众人离开闸站危险区。', 'N1'),
        ('把证据交给值班员并照顾工人', '工人得到照顾，值班员保管证据。', 'N1'),
        ('在安全地点休息并整理记录', '休息完成，逐项处理允许恢复的资源。', 'N1'),
        ('结束调查并整理下一次线索', '事件结束；成长或后续里程碑另行结算。', 'N1'),
    ]
    transcript = []
    for n, (intent, narration, location) in enumerate(turns, 1):
        before = session.view(db, gm=True)['state']
        changes = []
        calculation = '无骰；原创情境裁定'
        source = '原创闸站夜班/'+location
        if n == 2:
            if system == 'coc':
                calculation = 'test fixture: 图书馆80，d100=40 -> '+rules.coc_result(80, 40)
                assert rules.coc_result(80, 40) == 'hard'
                source += ';核心PDF71–77'
            else:
                calculation = 'test fixture: 调查d20=15，INT−1，总14>=DC12'
                assert 15 + rules.dnd_modifier(8) >= 12
                source += ';SRD6–8'
        if n == 5:
            if system == 'coc':
                assert rules.coc_result(70, 85) == 'failure'
                calculation = 'test fixture: 侦查70，85失败，不授予账本'
            else:
                assert 5 + 3 < 12
                calculation = 'test fixture: 察觉5+3=8<12，不授予账本'
        if n == 7:
            changes.append(resource('hp', -2))
            calculation = 'test fixture: CoC DEX70骰80失败；D&D特技3+2=5<10；原创风险伤害2'
            if system == 'coc':
                assert rules.coc_injury(12, 12, 2) == (10, False, 'injured')
        if n == 8:
            changes.append(resource('hp', 1 if system == 'coc' else 2))
            if system == 'dnd':
                changes.append(resource('second_wind', -1))
                calculation = 'test fixture: Second Wind d10=4+1=5，实际治疗2，次数2→1'
                source = 'SRD48'
            else:
                calculation = 'test fixture: 急救60，d100=40普通成功，一小时内恢复1HP'
                source = 'CoC核心PDF103'
        if n == 10:
            calculation = 'test fixture: CoC机械维修10，d100=08成功；D&D力量10+3=13>=12'
        if n == 14:
            if system == 'coc':
                result = rules.coc_melee(40, 30, 60, 45, 'dodge')
                assert result == 'dodged'
                calculation = 'test fixture: 攻击40骰30与闪避60骰45均普通，闪避胜'
                source = 'Chaosium官方主持屏Combat'
            else:
                assert 11 + 2 < 17
                calculation = 'test fixture: 先攻PC14+2>NPC9+1；PC交涉，NPC攻击11+2<AC17未命中'
                source = 'SRD14–16'
        if n == 15:
            if system == 'coc':
                assert rules.coc_melee(40, 8, 60, 40, 'dodge') == 'attacker_hits'
                changes.append(resource('hp', -2))
                calculation = 'test fixture: 攻击40骰8极难胜过闪避60骰40普通；拳击极难最大3，纠正伤害为3'
                changes[-1] = resource('hp', -3)
                source = 'CoC核心PDF87–89'
            else:
                changes.append(resource('hp', -3))
                calculation = 'test fixture: PC Dodge；NPC劣势骰18/16取16+2=18命中AC17；1d4=3'
                source = 'SRD战斗与Dodge'
        if n == 18 and system == 'dnd':
            # Worker is injured but conscious; no kit charge needed just to offer care.
            calculation = '工人清醒，不消耗医疗包来虚构HP治疗'
        if n == 19 and system == 'dnd':
            changes += [resource('hp', 3), resource('second_wind', 1)]
            calculation = 'test fixture: 1小时短休花1d10生命骰=4+CON2，实际恢复3；Second Wind恢复1次'
            private = copy.deepcopy(before['private'])
            private['hit_dice_spent'] = 1
            changes.append({'kind': 'private', 'value': private})
            source = 'SRD187、48'
        if n == 20 and system == 'coc':
            assert rules.coc_development(80, 81, 4) == 84
            calculation = 'test fixture: 图书馆幕间成长81>80，加1d10=4，80→84'
            private = copy.deepcopy(before['private'])
            private['library_skill'] = 84
            changes.append({'kind': 'private', 'value': private})
            source = 'CoC核心PDF79'
        # Preserve other private fields when recording position/next actor.
        private = next((c['value'] for c in changes if c['kind'] == 'private'), copy.deepcopy(before['private']))
        private.update(position=location, next_actor='pc1', last_player_turn=n)
        changes = [c for c in changes if c['kind'] != 'private']
        changes.append({'kind': 'private', 'value': private})
        changes.append({'kind': 'fact', 'value': {'id': f'observed-{n}', 'text': narration, 'audience': ['pc1']}})
        changes.append({'kind': 'clock', 'minutes': 60 if n == 19 else 2})
        event = {'id': f'{system}-turn-{n:02}', 'revision': n-1, 'profile': state['profile'], 'input': intent,
                 'resolution': calculation+'；'+narration, 'sources': [source], 'changes': changes}
        write(folder/f'turn-{n:02}.json', event)
        result = session.apply(db, event)
        after = session.view(db, gm=True)
        assert after['revision'] == n
        if n == 10:
            cold = json.loads(subprocess.check_output([sys.executable, '-X', 'utf8', str(ROOT/'scripts/session.py'), str(db), 'view', '--gm'], encoding='utf-8'))
            assert cold == after
            assert session.apply(db, event)['duplicate']
            write(folder/'cold-recovery.json', {'verified': True, 'revision': 10, 'state_sha256': session.digest(cold['state'])})
        transcript.append({'player_turn': n, 'player': intent, 'gm': narration, 'calculation': calculation, 'sources': [source], 'before_hp': before['actors']['pc1']['resources']['hp']['value'], 'after_hp': after['state']['actors']['pc1']['resources']['hp']['value'], 'receipt': result})
    end = session.view(db, gm=True)
    assert end['state']['actors']['pc1']['resources']['hp']['value'] == (8 if system == 'coc' else 12)
    if system == 'coc':
        assert end['state']['private']['library_skill'] == 84
    else:
        assert end['state']['actors']['pc1']['resources']['second_wind']['value'] == 2
        assert end['state']['private']['hit_dice_spent'] == 1
    player = session.view(db, player='pc1')
    assert '掩盖走私' not in session.encode(player)
    write(folder/'transcript.json', transcript)
    write(folder/'player-view.json', player)
    write(folder/'final-gm.json', end)
    lines = ['# 连续主持回放：'+system, '', '20个预设玩家行动；test fixture，无真人参与、无随机骰。第10回合由新Python进程读回恢复。', '']
    for turn in transcript:
        lines += [f"## 回合{turn['player_turn']}", f"玩家：{turn['player']}", f"主持：{turn['gm']}", f"核验：{turn['calculation']}；HP {turn['before_hp']}→{turn['after_hp']}；{turn['sources'][0]}", '']
    (folder/'transcript.md').write_text('\n'.join(lines), encoding='utf-8')
    return {'system': system, 'player_turns': 20, 'cold_recovery_at': 10, 'final_hp': end['state']['actors']['pc1']['resources']['hp']['value'], 'status': 'passed scripted replay; not live player evaluation'}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = [run(args.output, s) for s in ['coc', 'dnd']]
    write(args.output/'results.json', result)
    print(session.encode(result))
