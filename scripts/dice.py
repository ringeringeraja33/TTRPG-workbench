"""Bounded real dice and exact probabilities; no eval, no implicit game rules."""
import argparse, collections, datetime, itertools, json, re, secrets, sys, uuid

def distribution(expression):
    if expression=='4dF': faces=(-1,0,1); count=4
    else:
        m=re.fullmatch(r'(\d+)d(\d+)',expression)
        if not m: raise ValueError('Use NdS or 4dF')
        count,sides=map(int,m.groups())
        if not 1<=count<=100 or not 2<=sides<=1000: raise ValueError('Dice bounds exceeded')
        faces=range(1,sides+1)
    if len(faces)*count*count*max(len(faces),3)>10_000_000: raise ValueError('Exact calculation too large')
    dist={0:1}
    for _ in range(count):
        nxt=collections.Counter()
        for total,n in dist.items():
            for face in faces: nxt[total+face]+=n
        dist=dict(nxt)
    return dist

def probability(expression,threshold,mode='sum'):
    if mode=='sum':
        d=distribution(expression); good=sum(v for k,v in d.items() if k>=threshold); total=sum(d.values())
    elif mode in ('advantage','disadvantage'):
        if expression!='1d20': raise ValueError('Advantage modes require 1d20')
        good=sum((max(a,b) if mode=='advantage' else min(a,b))>=threshold for a in range(1,21) for b in range(1,21)); total=400
    elif mode in ('coc-bonus','coc-penalty'):
        if expression!='1d100' or not 1<=threshold<=100: raise ValueError('CoC requires 1d100 and threshold 1..100')
        # One extra tens die, shared units. 00+0 is 100.
        good=0; total=1000
        for u,a,b in itertools.product(range(10),repeat=3):
            vals=[(10*t+u) or 100 for t in (a,b)]
            result=min(vals) if mode=='coc-bonus' else max(vals)
            good+=result<=threshold
    else: raise ValueError('Unsupported mode')
    return {'expression':expression,'threshold':threshold,'mode':mode,'successes':good,'outcomes':total,'probability':good/total,'scope':'numeric threshold only; no critical/fumble or game-specific exceptions'}

def roll(expression):
    m=re.fullmatch(r'(\d+)d(\d+|F)([+-]\d+)?',expression)
    if not m: raise ValueError('Use NdS[+/-modifier] or NdF')
    n=int(m[1]); sides=3 if m[2]=='F' else int(m[2]); mod=int(m[3] or 0)
    if not 1<=n<=100 or not 2<=sides<=1000: raise ValueError('Dice bounds exceeded')
    faces=[secrets.randbelow(3)-1 if m[2]=='F' else secrets.randbelow(sides)+1 for _ in range(n)]
    return {'event_id':str(uuid.uuid4()),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expression':expression,'raw':faces,'modifier':mod,'total':sum(faces)+mod,'randomness':'OS secrets; actual roll'}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
    r=sub.add_parser('roll'); r.add_argument('expression')
    q=sub.add_parser('probability'); q.add_argument('expression'); q.add_argument('threshold',type=int); q.add_argument('--mode',default='sum',choices=['sum','advantage','disadvantage','coc-bonus','coc-penalty'])
    a=p.parse_args()
    try: result=roll(a.expression) if a.command=='roll' else probability(a.expression,a.threshold,a.mode)
    except ValueError as e: p.error(str(e))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
