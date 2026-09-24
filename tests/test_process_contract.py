from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
payload={'organization_id':'one','community_id':'g10','reference_period':'2026-W38','requested_assets':['LINKEDIN','FAQ'],'interactions':[{'author':'Mariana','channel':'logros','type':'testimonio','text':'Conseguí mi primer empleo.'}]}
def test_idempotency_required(): assert client.post('/api/v1/process',json=payload).status_code == 422
def test_contract_returns_202():
    r=client.post('/api/v1/process',json=payload,headers={'Idempotency-Key':'demo-001'})
    assert r.status_code == 202
    assert r.json()['schema_version']=='v1'
def test_same_key_same_run_id():
    h={'Idempotency-Key':'stable-key'}
    a=client.post('/api/v1/process',json=payload,headers=h).json()
    b=client.post('/api/v1/process',json=payload,headers=h).json()
    assert a['run_id']==b['run_id']
