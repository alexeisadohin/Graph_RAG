from config import *

ACCENT_MAPPING = {
    '́': '',
    '̀': '',
    'а́': 'а',
    'а̀': 'а',
    'е́': 'е',
    'ѐ': 'е',
    'и́': 'и',
    'ѝ': 'и',
    'о́': 'о',
    'о̀': 'о',
    'у́': 'у',
    'у̀': 'у',
    'ы́': 'ы',
    'ы̀': 'ы',
    'э́': 'э',
    'э̀': 'э',
    'ю́': 'ю',
    '̀ю': 'ю',
    'я́́': 'я',
    'я̀': 'я',
}
ACCENT_MAPPING = {unicodedata.normalize('NFKC', i): j for i, j in ACCENT_MAPPING.items()}


def unaccentify(s):
    source = unicodedata.normalize('NFKC', s)
    for old, new in ACCENT_MAPPING.items():
        source = source.replace(old, new)
    return source

def normalize(text):
    return (unaccentify(text)
            .replace('«','')
            .replace('»','')
            .replace('"','')
            .replace('<','')
            .replace('>',''))


def add_entity(entities,name,kind,desc):
    if name in entities.keys():
        entities[name]['kind'].append(kind)
        entities[name]['desc'].append(desc)
    else:
        entities[name] = { 'kind' : [kind], 'desc' : [desc] }

def extract_ER(lines):
    entities = {}
    relations = []
    for x in lines:
        x = normalize(x)
        if z:=re.match(r'\((.*)\)',x):
            z = z.string.strip()[1:-1].split('|')
            z = [t.strip().lower() for t in z]
            if z[0] == 'entity':
                if len(z)<4:
                    z.append('')
                else:
                    add_entity(entities, z[1], z[2], z[3])
            elif z[0] == 'relationship':
                while len(z)<5:
                    z.append('')
                relations.append({ 
                    "source": z[1], 
                    "target" : z[2], 
                    "relation": z[3],
                    "desc" : z[4]})
            else:
                print(f'Неверная команда: {z}')
    relations = [x for x in relations if x['source'] in entities.keys() and x['target'] in entities.keys()]
    
    return entities, relations


