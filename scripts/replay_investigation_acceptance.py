"""Original live-investigation extension and knowledge recovery walkthrough."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import investigation_runtime as runtime
import session


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1]
    state=json.loads((root/'assets/templates/session-initial.json').read_text(encoding='utf-8'))
    database=output/'campaign.sqlite';session.init(database,state)
    def saved():return session.view(database,gm=True)
    def event(step,data):
        rev=saved()['revision']
        return {'id':f'investigate-{rev}','revision':rev,'profile':state['profile'],
                'input':'Original scripted investigation example','resolution':'Explicit GM procedure',
                'sources':['GM original acceptance procedure'],
                'changes':[{'kind':'investigation','step':step,'data':data}]}
    def apply(step,data):return session.apply(database,event(step,data))
    apply('setup',{'plan':{'schema':1,'evidence':[{'id':'note','text':'Original note','audience':['all'],'available':True}],
        'conclusions':[{'id':'destination','text':'GM_SECRET destination','audience':[],'essential':True,'routes':[['note']]}]}})
    apply('discover',{'evidence':'note','recipients':['pc1'],'method':'Read the note'})
    apply('hypothesize',{'id':'theory','actor':'pc1','text':'The note is genuine','evidence':['note']})
    before_extension=saved()
    expanded=event('extend',{'evidence':[{'id':'witness','text':'A contrary witness account','audience':['all'],'available':True}],
        'conclusions':[],'routes':[{'conclusion':'destination','route':['witness']}],'reason':'New interview opportunity'})
    session.apply(database,expanded);assert session.apply(database,expanded)['duplicate']
    assert session.view(database,player='pc1')['investigation']['evidence']==[{'id':'note','text':'Original note'}]
    before=saved()
    try:apply('edit_unseen',{'evidence':'note','text':'Silently replaced note','reason':'Correction'})
    except ValueError:pass
    else:raise AssertionError('Delivered note was rewritten')
    assert saved()==before
    apply('edit_unseen',{'evidence':'witness','text':'The witness disputes the note date','reason':'Clarified interview preparation'})
    apply('discover',{'evidence':'witness','recipients':['pc1'],'method':'Interview witness'})
    assert saved()['state']['private']['investigation']['hypotheses']['theory']['status']=='open'
    cold=output/'gm-cold.json'
    process=subprocess.run([sys.executable,'-X','utf8',str(Path(runtime.__file__)),str(database),'view','--private-output',str(cold)],capture_output=True,text=True,encoding='utf-8')
    assert process.returncode==0,process.stderr
    assert 'GM_SECRET' not in process.stdout
    assert json.loads(cold.read_text(encoding='utf-8'))['investigation']==saved()['state']['private']['investigation']
    player=session.view(database,player='pc1');assert 'GM_SECRET' not in session.encode(player)
    (output/'player-expanded.json').write_text(session.encode(player),encoding='utf-8')
    restore=event('unused',{});restore['changes']=[{'kind':'restore','revision':before_extension['revision']}]
    session.apply(database,restore)
    assert saved()['state']==before_extension['state']
    result={'passed':True,'transitions':saved()['revision'],'old_observation_preserved':True,
        'new_clue_auto_delivered':False,'hypothesis_auto_changed':False,'cold_recovery':True,'restore':True,
        'scope':'original scripted example; not live-player evaluation'}
    (output/'results.json').write_text(session.encode(result),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    print(session.encode(run(parser.parse_args().output)))
