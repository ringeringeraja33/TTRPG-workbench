"""Original synthetic encounter: reservations, pending choice, expiry and recovery."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import actions
import combat
import session


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    database=output/'campaign.sqlite'
    profile={'system':'original-boundary-demo','edition':'1','options':{}}
    state={'profile':profile,'actors':{actor:{'name':actor,'audience':[actor],
        'resources':{'focus':{'value':1,'max':1}},'conditions':[]} for actor in ('pc1','pc2')},
        'facts':[],'private':{},'pending':[],'clock':0}
    session.init(database,state);revision=0
    def send(change):
        nonlocal revision
        event={'id':'demo-'+str(revision),'revision':revision,'profile':profile,
               'input':'Scripted synthetic choices; actual OS roll',
               'resolution':'Original timing demonstration, not a published system rule',
               'sources':['GM original demonstration: one focus; effect until next own turn start'],
               'changes':[change]}
        (output/(event['id']+'.json')).write_text(session.encode(event)+'\n',encoding='utf-8')
        result=session.apply(database,event)
        assert session.apply(database,event)['duplicate']
        revision=result['revision']
    def turn(step,data=None):send({'kind':'combat','step':step,'data':data or {}})
    def act(step,data):send({'kind':'action','action':'protect','step':step,'data':data})
    turn('start',{'id':'encounter-1','audience':['all'],'order':['pc1','pc2'],
                  'refresh':[{'actor':'pc1','resource':'focus','at':'start','value':1}]})
    act('declare',{'actor':'pc1','summary':'施加防护','intent':'protect self','method':'original test action',
        'stakes':'spend one focus on settlement','audience':['pc1'],'roll':{'mode':'tool','expression':'1d6'},
        'costs':[{'kind':'resource','actor':'pc1','resource':'focus','delta':-1}],
        'timing':{'encounter':'encounter-1','turn':1}})
    own=actions.view(database,player='pc1')['resource_availability'][0]
    assert own['reserved']==1 and own['available']==0
    act('roll',{})
    act('wait',{'actor':'pc1','prompt':'确认按已声明费用结算？','options':{'confirm':'确认'}})
    private=output/'cold-private.json'
    cold=subprocess.run([sys.executable,'-X','utf8',str(Path(actions.__file__)),str(database),'view',
        '--private-output',str(private)],capture_output=True,text=True,encoding='utf-8',check=True)
    assert json.loads(cold.stdout)['private_result_saved']
    assert json.loads(private.read_text(encoding='utf-8'))['actions']['protect']['status']=='waiting'
    act('choose',{'actor':'pc1','option':'confirm'})
    act('settle',{'outcome':'success','effects':[{'kind':'combat_effect','step':'add_effect','data':
        {'id':'ward','label':'防护','targets':['pc1'],'audience':['pc1'],
         'expires':{'actor':'pc1','at':'start','occurrence':2}}}]})
    turn('end_turn');turn('next_turn')
    middle=session.view(database,gm=True)['state']
    assert middle['private']['combat']['effects']['ward']['status']=='active'
    assert middle['actors']['pc1']['resources']['focus']['value']==0
    assert session.view(database,player='pc2')['combat']['effects']=={}
    turn('end_turn');turn('next_turn')
    final=session.view(database,gm=True)['state']
    assert final['private']['combat']['round']==2
    assert final['private']['combat']['effects']['ward']['status']=='expired'
    assert final['actors']['pc1']['resources']['focus']['value']==1
    assert actions.reservations(final)=={}
    result={'passed':True,'transitions':revision,'cold_recovery':'pending choice',
            'reserved_then_spent_once':True,'expiry':'pc1 second turn start',
            'refresh':'configured original procedure','dice':'actual OS randomness','choices':'synthetic'}
    (output/'result.json').write_text(session.encode(result)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    print(session.encode(run(parser.parse_args().output)))
