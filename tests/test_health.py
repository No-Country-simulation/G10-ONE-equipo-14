from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
class FakeDB:
    def execute(self, _): return 1
def override_db(): yield FakeDB()
app.dependency_overrides[get_db] = override_db
client = TestClient(app)
def test_health():
    r=client.get('/api/v1/health')
    assert r.status_code == 200
    assert r.json()['database'] == 'ok'
    assert r.json()['version'] == 'v1'
