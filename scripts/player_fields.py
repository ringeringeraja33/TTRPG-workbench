"""Explicit, recursive field projection for generated player character cards."""

def project(value, schema, path='card'):
    if isinstance(schema,type):
        if type(value) is not schema:
            raise ValueError(path+' has an invalid public field type')
        return value
    if isinstance(schema,list):
        if not isinstance(value,list): raise ValueError(path+' must be a list')
        return [project(item,schema[0],path+'[]') for item in value]
    if not isinstance(value,dict): raise ValueError(path+' must be an object')
    if '*' in schema:
        if any(not isinstance(key,str) or not key for key in value):
            raise ValueError(path+' requires nonempty field names')
        return {key:project(item,schema['*'],path+'.'+key) for key,item in value.items()}
    return {key:project(value[key],expected,path+'.'+key) for key,expected in schema.items() if key in value}

CARD = {
    **dict.fromkeys(('id','name','occupation','generation','age_check'),str),
    **dict.fromkeys(('age','luck','occupation_spent','occupation_budget','interest_spent'),int),
    'attributes':dict.fromkeys(('STR','CON','SIZ','DEX','APP','INT','POW','EDU'),int),
    'skills':{'*':dict.fromkeys(('regular','hard','extreme'),int)},
    'derived':{**dict.fromkeys(('hp','mp','san','san_max','build','mov'),int),'db':str},
    'equipment':[str], 'languages':dict.fromkeys(('native','additional'),str),
    'background':dict.fromkeys(('appearance','belief','important_person','place','treasured_item',
                               'trait','connection','motivation','conditions'),str),
    'wealth':{**dict.fromkeys(('cash','assets','equipment_cost'),int),
              **dict.fromkeys(('unit','authority','equipment_ownership'),str)},
    'combat':{**dict.fromkeys(('brawl','dodge','weapon'),str),'armor':int},
}
