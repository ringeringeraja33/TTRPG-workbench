"""CoC7 profile-based creation audit; historical truth requires source review.

JSON examples define the schema. No eval, dice, network, or campaign mutation.
"""
import argparse
import json
from pathlib import Path


def number(value, maximum=999):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError('Expected nonnegative integer within bounds')
    return value


def budget(formula, attributes):
    if not isinstance(formula, dict) or not formula:
        raise ValueError('Explicit attribute multiplier map required')
    return sum(number(multiplier, 4)*number(attributes[name], 99) for name,multiplier in formula.items())


def audit(spec):
    if spec['profile']['system'] != 'CoC' or spec['profile']['edition'] != '7e':
        raise ValueError('This adapter supports CoC7 only')
    errors, cards = [], []
    number(spec['skill_cap'],99);number(spec['coverage_threshold'],99)
    if type(spec['house_rules_approved']) is not bool:
        raise ValueError('House-rule approval must be explicit boolean')
    sources = spec['sources']
    pending = list(spec.get('pending', []))
    for source in sources.values():
        if source.get('status') != 'read' or not source.get('locator'):
            pending.append('Unverified source: '+source.get('title','unnamed'))
    for ref in spec['rule_sources']:
        if ref not in sources:
            pending.append('Missing source: '+ref)
    if not spec['house_rules_approved']:
        pending.append('House rules not approved')
    for card in spec['characters']:
        cid=card['id']; attrs=card['attributes']; role=spec['occupations'][card['occupation']]
        if card['profile'] != spec['profile']:
            errors.append(cid+': profile conflict')
        if set(attrs) != {'STR','CON','SIZ','DEX','APP','INT','POW','EDU'}:
            raise ValueError('Eight characteristic values required')
        for value in attrs.values():
            number(value,99)
            if value==0: raise ValueError('Initial characteristics must be positive')
        if not 20 <= card['age'] <= 39:
            errors.append(cid+': this fixture adapter requires completed age treatment for ages20-39')
        if not card['generation'] or not card['age_check']:
            errors.append(cid+': missing generation or age evidence')
        bases={name:(attrs['EDU'] if value=='EDU' else attrs['DEX']//2 if value=='DEX/2' else number(value,99))
               for name,value in spec['skill_bases'].items()}
        values=bases.copy(); allocated=set(); occupation=interest=0
        for row in card['allocations']:
            if set(row) != {'skill','occupation','interest'}:
                raise ValueError('Allocation fields must not override a profile base')
            name=row['skill']; op=number(row['occupation']); ip=number(row['interest'])
            if name not in bases or name in allocated:
                errors.append(cid+': unknown/duplicate skill '+name);continue
            allocated.add(name)
            if op and name not in role['skills']:
                errors.append(cid+': occupation skill not eligible '+name)
            if ip and name in spec['no_interest']:
                errors.append(cid+': interest prohibited '+name)
            values[name]+=op+ip; occupation+=op; interest+=ip
            if values[name] > spec['skill_cap']:
                errors.append(cid+': skill cap '+name)
        expected=budget(role['formula'],attrs)
        if occupation!=expected or interest!=budget(spec['interest_formula'],attrs):
            errors.append(cid+': point budget mismatch')
        wealth=values[spec['wealth_skill']]
        if not role['wealth_range'][0]<=wealth<=role['wealth_range'][1]:
            errors.append(cid+': wealth range')
        for item in card['equipment']:
            if item not in spec['equipment_allowlist']:
                errors.append(cid+': unavailable equipment '+item)
        money=card['wealth']; policy=spec['wealth_policy']
        spent=number(money['equipment_cost'])
        if money['unit']!=policy['unit'] or number(money['cash'])!=policy['starting_cash']-spent or number(money['assets'],1000000)!=policy['asset_total']:
            errors.append(cid+': wealth accounting/currency mismatch')
        for field in ['name','languages','background','wealth','combat']:
            if not card.get(field): errors.append(cid+': missing '+field)
        hp=(attrs['CON']+attrs['SIZ'])//10; mp=attrs['POW']//5
        strength=attrs['STR']+attrs['SIZ']
        if strength > 164: raise ValueError('Higher Build requires full system adapter')
        build,db=(-2,'-2') if strength<=64 else (-1,'-1') if strength<=84 else (0,'0') if strength<=124 else (1,'1d4')
        mov=7 if attrs['STR']<attrs['SIZ'] and attrs['DEX']<attrs['SIZ'] else 9 if attrs['STR']>attrs['SIZ'] and attrs['DEX']>attrs['SIZ'] else 8
        cards.append({'id':cid,'name':card['name'],'occupation':card['occupation'],'age':card['age'],
                      'attributes':attrs,'luck':number(card['luck'],99),'generation':card['generation'],'age_check':card['age_check'],
                      'skills':{n:{'regular':v,'hard':v//2,'extreme':v//5} for n,v in values.items()},
                      'occupation_spent':occupation,'occupation_budget':expected,'interest_spent':interest,
                      'derived':{'hp':hp,'mp':mp,'san':attrs['POW'],'san_max':99-values['Cthulhu Mythos'],'build':build,'db':db,'mov':mov},
                      **{k:card[k] for k in ['equipment','languages','background','wealth','combat']}})
    ids=[c['id'] for c in cards]
    if len(set(ids))!=len(ids): errors.append('Duplicate character IDs')
    coverage={name:[c['id'] for c in cards if any(c['skills'].get(skill,{}).get('regular',0)>=spec['coverage_threshold'] for skill in options)]
              for name,options in spec['team_capabilities'].items()}
    gaps=[name for name,people in coverage.items() if not people]
    return {'status':'invalid' if errors else 'draft' if pending else 'passed configured arithmetic',
            'errors':errors,'pending':pending,'cards':cards,'team_coverage':coverage,'coverage_gaps':gaps,
            'scope':'Numerical and configured-availability audit, not independent historical certification'}


def player_view(result):
    # Build from known fields; never include spec, GM notes, sources or hidden routes.
    return {'status':result['status'],'cards':result['cards']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec',type=Path);parser.add_argument('--player',action='store_true')
    args=parser.parse_args()
    result=audit(json.loads(args.spec.read_text(encoding='utf-8-sig')))
    if args.player:result=player_view(result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result['status']!='passed configured arithmetic':raise SystemExit(1)


if __name__=='__main__':main()
