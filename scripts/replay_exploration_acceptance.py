"""Original exploration walkthrough: explicit costs, deadlines and cold recovery."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import exploration
import session


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    state=json.loads((Path(__file__).resolve().parents[1]/'assets/templates/session-initial.json').read_text(encoding='utf-8'))
    state['actors']['pc1']['resources']['supplies']={'value':3,'max':3}
    database=output/'campaign.sqlite';session.init(database,state)
    def saved():return session.view(database,gm=True)
    def event(change):
        rev=saved()['revision']
        return {'id':f'explore-{rev}','revision':rev,'profile':state['profile'],
                'input':'Original scripted exploration example','resolution':'Explicit original timing and costs',
                'sources':['GM original acceptance procedure; no published-system default'], 'changes':[change]}
    def ex(step,data):return session.apply(database,event({'kind':'exploration','step':step,'data':data}))
    def cost():return {'kind':'resource','actor':'pc1','resource':'supplies','delta':-1}
    def activity(minutes,costs):return {'minutes':minutes,'participants':['pc1'],'summary':'Explore the passage','costs':costs,'audience':['all']}
    ex('setup',{'audience':['all']})
    ex('schedule',{'id':'watch','label':'SECRET patrol deadline','due':5,'every':5,'blocking':True,'audience':[]})
    planned=event({'kind':'exploration','step':'advance','data':activity(5,[cost()])})
    before=saved();preview=exploration.preview(database,planned);assert saved()==before
    (output/'gm-preview.json').write_text(session.encode(preview),encoding='utf-8')
    session.apply(database,planned);assert session.apply(database,planned)['duplicate']
    snapshot=output/'gm-cold.json'
    cold=subprocess.run([sys.executable,'-X','utf8',str(Path(exploration.__file__)),str(database),'view','--private-output',str(snapshot)],capture_output=True,text=True,encoding='utf-8')
    assert cold.returncode==0,cold.stderr
    assert 'SECRET' not in cold.stdout
    restored=json.loads(snapshot.read_text(encoding='utf-8'))
    assert restored['exploration']['reminders']['watch']['status']=='due'
    before=saved()
    try:ex('advance',activity(1,[cost()]))
    except ValueError:pass
    else:raise AssertionError('Deadline crossing accepted')
    assert saved()==before
    ex('ack',{'id':'watch','resolution':'Patrol passes; continue'})
    ex('reschedule',{'id':'watch','due':12,'every':5,'reason':'Explicit changed patrol schedule'})
    declaration={'actor':'pc1','summary':'Search side room','intent':'Find the exit','method':'Careful search',
        'stakes':'Spend supplies and time','audience':['all'],'roll':None,'costs':[cost()]}
    session.apply(database,event({'kind':'action','action':'search','step':'declare','data':declaration}))
    session.apply(database,event({'kind':'action','action':'search','step':'settle','data':{'outcome':'no-check',
        'effects':[{'kind':'exploration_effect','step':'advance','data':activity(6,[])}]}}))
    ex('advance',activity(1,[cost()]))
    final=saved();assert final['state']['clock']==12
    assert final['state']['actors']['pc1']['resources']['supplies']['value']==0
    assert final['state']['private']['exploration']['reminders']['watch']['status']=='due'
    player=session.view(database,player='pc1');assert 'SECRET' not in session.encode(player)
    for filename,value in [('gm-final.json',final),('player-view.json',player)]:
        (output/filename).write_text(session.encode(value),encoding='utf-8')
    result={'passed':True,'transitions':final['revision'],'minutes':12,'supplies_remaining':0,
            'preview_mutated_source':False,'cold_recovery':'due reminder','duplicate_spend':False,
            'rules':'original scripted procedure; not live-player evaluation'}
    (output/'results.json').write_text(session.encode(result),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    print(session.encode(run(parser.parse_args().output)))
