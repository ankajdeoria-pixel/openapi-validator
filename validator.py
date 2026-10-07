import sys
from pathlib import Path
import yaml
class DuplicateKeyError(Exception): pass
class StrictLoader(yaml.SafeLoader): pass
def construct_mapping(loader,node,deep=False):
    m={}
    for kn,vn in node.value:
        k=loader.construct_object(kn,deep=deep)
        if k in m: raise DuplicateKeyError(f"Duplicate YAML key detected: '{k}' at line {kn.start_mark.line+1}")
        m[k]=loader.construct_object(vn,deep=deep)
    return m
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,construct_mapping)
class ValidationError:
    def __init__(self,r,m): self.rule_id,self.message=r,m
    def __str__(self): return f"[FAIL] {self.rule_id}: {self.message}"
def load_yaml(p):
    with Path(p).open(encoding='utf-8') as f: return yaml.load(f,Loader=StrictLoader)
def schemes(s):
    c=s.get('components',{})
    return c.get('securitySchemes',{}) if isinstance(c,dict) and isinstance(c.get('securitySchemes',{}),dict) else {}
def operations(s):
    paths=s.get('paths',{})
    if not isinstance(paths,dict): return
    methods={'get','post','put','delete','patch','options','head','trace'}
    for p,item in paths.items():
        if isinstance(item,dict):
            for method,op in item.items():
                if method.lower() in methods and isinstance(op,dict): yield p,method.upper(),op
def a1(s): return [] if 'openapi' in s else [ValidationError('AUTH-001',"Missing 'openapi' field.")]
def a2(s): return [] if 'components' in s else [ValidationError('AUTH-002',"Missing 'components' section.")]
def a3(s): return [] if schemes(s) else [ValidationError('AUTH-003','No security schemes defined.')]
def a4(s): return [] if 'BearerAuth' in schemes(s) else [ValidationError('AUTH-004','BearerAuth security scheme is missing.')]
def a5(s):
    b=schemes(s).get('BearerAuth'); return [] if b is None or (isinstance(b,dict) and b.get('type')=='http') else [ValidationError('AUTH-005',"BearerAuth.type must be 'http'.")]
def a6(s):
    b=schemes(s).get('BearerAuth'); return [] if not isinstance(b,dict) or (isinstance(b.get('scheme'),str) and b['scheme'].lower()=='bearer') else [ValidationError('AUTH-006',"BearerAuth.scheme must be 'bearer'.")]
def a7(s): return [] if isinstance(s.get('paths'),dict) and s['paths'] else [ValidationError('AUTH-007','No API paths defined.')]
def a8(s): return []
def a9(s): return [ValidationError('AUTH-009',f'{m} {p} missing security requirement.') for p,m,o in operations(s) if 'security' not in o]
def a10(s): return [ValidationError('AUTH-010',f'{m} {p} missing responses.') for p,m,o in operations(s) if not o.get('responses')]
def a11(s): return [] if 'info' in s else [ValidationError('AUTH-011','Missing info section.')]
def a12(s): return [] if 'servers' in s else [ValidationError('AUTH-012','Missing servers section.')]
RULE_HANDLERS={'AUTH-001':a1,'AUTH-002':a2,'AUTH-003':a3,'AUTH-004':a4,'AUTH-005':a5,'AUTH-006':a6,'AUTH-007':a7,'AUTH-008':a8,'AUTH-009':a9,'AUTH-010':a10,'AUTH-011':a11,'AUTH-012':a12}
def load_rules(p):
    try: d=load_yaml(p)
    except DuplicateKeyError as e: raise ValueError(f'rules.yaml contains duplicate keys: {e}')
    except yaml.YAMLError as e: raise ValueError(f'Invalid rules.yaml: {e}')
    if not isinstance(d,dict) or not isinstance(d.get('rules'),dict): raise ValueError("rules.yaml must contain a 'rules' mapping.")
    r=d['rules']; req={f'AUTH-{i:03d}' for i in range(1,13)}; miss=sorted(req-set(r)); unk=sorted(set(r)-set(RULE_HANDLERS))
    if miss: raise ValueError('rules.yaml is missing required rules: '+', '.join(miss))
    if unk: raise ValueError('rules.yaml contains unknown rules: '+', '.join(unk))
    return r
def enabled(r,i): return isinstance(r.get(i),dict) and r[i].get('enabled',True) is True
def validate(s,r):
    out=[]
    for i in sorted(RULE_HANDLERS):
        if enabled(r,i):
            try: out.extend(RULE_HANDLERS[i](s))
            except Exception as e: out.append(ValidationError(i,f'Rule handler failed: {e}'))
    return out
def main():
    if len(sys.argv) not in (2,3): print('Usage: python validator.py <openapi.yaml> [rules.yaml]',file=sys.stderr); return 2
    op=Path(sys.argv[1]); rp=Path(sys.argv[2]) if len(sys.argv)==3 else Path(__file__).with_name('rules.yaml')
    if not op.is_file(): print(f'[ERROR] OpenAPI file not found: {op}',file=sys.stderr); return 2
    if not rp.is_file(): print(f'[ERROR] Rules file not found: {rp}',file=sys.stderr); return 2
    try: r=load_rules(rp)
    except ValueError as e: print(f'[ERROR] {e}',file=sys.stderr); return 2
    try: s=load_yaml(op)
    except DuplicateKeyError as e:
        print(f'[FAIL] AUTH-008: {e}' if enabled(r,'AUTH-008') else f'[ERROR] {e}',file=sys.stdout if enabled(r,'AUTH-008') else sys.stderr); return 1
    except yaml.YAMLError as e: print(f'[ERROR] Invalid OpenAPI YAML: {e}',file=sys.stderr); return 1
    if not isinstance(s,dict): print('[ERROR] OpenAPI document must be a YAML mapping.',file=sys.stderr); return 1
    errs=validate(s,r)
    if errs:
        print('\n'.join(map(str,errs))); print(f'\nValidation failed: {len(errs)} error(s)'); return 1
    print('[PASS] OpenAPI validation successful.'); print('[PASS] Enabled AUTH rules passed.'); return 0
if __name__=='__main__': sys.exit(main())
