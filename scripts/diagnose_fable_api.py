"""One benign connectivity/billing check; no tool actions or behavioral scoring."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from containment_extension.config import load_env,secret
from containment_extension.providers import NoRedirect

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
assert not a.output.exists()
load_env(ROOT.parent/'.env')
os.environ['SSL_CERT_FILE']=str(ROOT/'.venv/lib/python3.13/site-packages/certifi/cacert.pem')
key=secret('ANTHROPIC_API_KEY')
payload={'model':'claude-fable-5-2','max_tokens':64,'messages':[{'role':'user','content':'Reply READY.'}]}
request=urllib.request.Request('https://api.anthropic.com/v1/messages',data=json.dumps(payload).encode(),
    headers={'x-api-key':key,'anthropic-version':'2023-06-01','Content-Type':'application/json'})
result={'purpose':'One benign diagnostic; no tool actions; excluded from experiments'}
try:
    with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect()).open(request,timeout=60) as r:
        raw=json.loads(r.read(20000))
        result.update(status=r.status,model=raw.get('model'),usage=raw.get('usage'),success=True)
except urllib.error.HTTPError as e:
    body=e.read(20000)
    try: error=json.loads(body).get('error',{})
    except (ValueError,AttributeError): error={}
    message=str(error.get('message','')).replace(key,'[REDACTED]')
    message=re.sub(r'sk-[A-Za-z0-9_-]+','[REDACTED]',message)[:1000]
    result.update(status=e.code,error_type=error.get('type'),message=message,success=False)
except Exception as e:
    result.update(success=False,error_type=type(e).__name__)
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
