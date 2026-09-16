"""Synthetic action workflow walkthrough with actual OS dice and cold recovery."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import actions
import dice_local
import session
import session_review


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    campaign, dice = output/'campaign.sqlite', output/'dice.sqlite'
    state = {'profile':{'system':'original-demo','edition':'1','options':{}},
             'actors':{'pc1':{'name':'示例调查者','audience':['pc1'],
                'resources':{'hp':{'value':12,'max':12},'tools':{'value':3,'max':3}},'conditions':[]}},
             'facts':[], 'private':{}, 'pending':[], 'clock':0}
    session.init(campaign,state)
    revision = 0
    def send(step,data):
        nonlocal revision
        event = {'id':'demo-'+step,'revision':revision,'profile':state['profile'],
                 'input':'Synthetic workflow; player choices are scripted, dice use actual OS randomness',
                 'resolution':'Original demo: spend one tool use; 4+ opens door, otherwise lose 1 HP',
                 'sources':['Original demonstration procedure; not CoC or D&D rules'],
                 'changes':[{'kind':'action','action':'door','step':step,'data':data}]}
        file = output/(step+'.json')
        file.write_text(session.encode(event)+'\n',encoding='utf-8')
        result=session.apply(campaign,event)
        assert session.apply(campaign,event)['duplicate']
        revision=result['revision']
    send('declare',{'actor':'pc1','summary':'检查门闩','intent':'尝试打开门',
        'method':'使用工具','stakes':'花费一次工具使用；失败受到 1 点伤害',
        'audience':['pc1'],'costs':[{'kind':'resource','actor':'pc1','resource':'tools','delta':-1}],
        'roll':{'mode':'receipt','expression':'1d6','source':{'database':str(dice),
            'scope':'demo','actor':'player-local','operation':'door-roll'}}})
    receipt=dice_local.execute(dice,'demo','player-local','.rh 1d6','door-roll',0)
    assert dice_local.execute(dice,'demo','player-local','.rh 1d6','door-roll',0)==receipt
    send('roll',{})
    send('wait',{'actor':'pc1','prompt':'骰子已记录，确认结算？','options':{'resolve':'按已声明风险结算'}})
    private=output/'cold-private.json'
    cold=subprocess.run([sys.executable,'-X','utf8',str(Path(actions.__file__)),str(campaign),
        'view','--private-output',str(private)],capture_output=True,text=True,encoding='utf-8',check=True)
    assert set(json.loads(cold.stdout))=={'revision','private_result_saved'}
    recovered=json.loads(private.read_text(encoding='utf-8'))['actions']['door']
    assert recovered['status']=='waiting' and recovered['evidence']['roll']==receipt['result']
    send('choose',{'actor':'pc1','option':'resolve'})
    total=receipt['result']['results'][0]['total']
    effects=[] if total>=4 else [{'kind':'resource','actor':'pc1','resource':'hp','delta':-1}]
    send('settle',{'outcome':'success' if total>=4 else 'failure','effects':effects})
    saved=session.view(campaign,gm=True)['state']
    assert saved['actors']['pc1']['resources']['tools']['value']==2
    assert saved['actors']['pc1']['resources']['hp']['value']==(12 if total>=4 else 11)
    assert not session_review.recap(campaign,gm=True)['next_prep']['pending_actions']
    assert actions.view(campaign,player='outsider')['actions']=={}
    player=actions.view(campaign,player='pc1')
    assert set(player['actions']['door'])=={'summary','status'}
    (output/'player.json').write_text(session.encode(player)+'\n',encoding='utf-8')
    result={'passed':True,'transitions':revision,'cold_recovery':'waiting',
            'roll_origin':'actual OS randomness','player_choices':'scripted synthetic example',
            'duplicate_resource_spend':False,'private_evidence_in_player_view':False}
    (output/'result.json').write_text(session.encode(result)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    print(session.encode(run(parser.parse_args().output)))
