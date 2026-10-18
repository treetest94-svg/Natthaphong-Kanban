from copy import deepcopy
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from main import create_app

class TestRepository:
    __test__ = False
    def __init__(self):
        self.rows = {}
        self.next_id = 1
    def list(self):
        return deepcopy(list(self.rows.values()))
    def create(self, values):
        row = {'id': self.next_id, 'created_at': datetime.now(timezone.utc).isoformat(), **values}
        self.rows[self.next_id] = row
        self.next_id += 1
        return deepcopy(row)
    def update(self, card_id, values):
        if card_id not in self.rows:
            return None
        self.rows[card_id].update(values)
        return deepcopy(self.rows[card_id])
    def delete(self, card_id):
        return self.rows.pop(card_id, None) is not None

@pytest.fixture
def client():
    with TestClient(create_app(TestRepository())) as test_client:
        yield test_client

def test_list_starts_empty(client):
    response = client.get('/api/cards')
    assert response.status_code == 200
    assert response.json() == []

def test_create_returns_saved_card_and_survives_another_request(client):
    response = client.post('/api/cards', json={'title':'  Plan the project  ', 'status':'todo'})
    assert response.status_code == 201
    card = response.json()
    assert card['title'] == 'Plan the project'
    assert card['status'] == 'todo'
    assert isinstance(card['id'], int)
    assert client.get('/api/cards').json() == [card]

def test_move_through_all_columns(client):
    card = client.post('/api/cards', json={'title':'Ship it'}).json()
    for status in ['doing','done','todo']:
        response = client.patch(f"/api/cards/{card['id']}",json={'status':status})
        assert response.status_code == 200
        assert response.json()['status'] == status
        assert client.get('/api/cards').json()[0]['status'] == status

def test_delete_removes_card_and_missing_card_is_404(client):
    card = client.post('/api/cards',json={'title':'Temporary card'}).json()
    response = client.delete(f"/api/cards/{card['id']}")
    assert response.status_code == 204
    assert client.get('/api/cards').json() == []
    assert client.delete(f"/api/cards/{card['id']}").status_code == 404

@pytest.mark.parametrize('title',['','  ','x'*241,None,123])
def test_reject_invalid_titles(client,title):
    assert client.post('/api/cards',json={'title':title}).status_code == 422
    assert client.get('/api/cards').json() == []

@pytest.mark.parametrize('status',['in progress','complete','TODO','',None])
def test_reject_invalid_statuses(client,status):
    assert client.post('/api/cards',json={'title':'Valid title','status':status}).status_code == 422

def test_invalid_move_does_not_change_existing_card(client):
    card = client.post('/api/cards',json={'title':'Keep this intact'}).json()
    assert client.patch(f"/api/cards/{card['id']}",json={'status':'unknown'}).status_code == 422
    assert client.get('/api/cards').json()[0]['status'] == 'todo'

def test_update_missing_card_returns_404(client):
    assert client.patch('/api/cards/999',json={'status':'done'}).status_code == 404

def test_update_title(client):
    card = client.post('/api/cards',json={'title':'Old title'}).json()
    response = client.patch(f"/api/cards/{card['id']}",json={'title':'  Updated title  '})
    assert response.status_code == 200
    assert response.json()['title'] == 'Updated title'

def test_health_and_security_headers(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.headers['x-content-type-options'] == 'nosniff'

def test_empty_update_rejected(client):
    card = client.post('/api/cards',json={'title':'No blank patch'}).json()
    assert client.patch(f"/api/cards/{card['id']}",json={}).status_code == 422

class PrivateTestRepository:
    def __init__(self): self.boards={}
    def for_board(self,token): return self.boards.setdefault(token,TestRepository())

def test_private_browser_boards_are_isolated():
    app=create_app(PrivateTestRepository())
    with TestClient(app) as alice, TestClient(app) as bob:
        added=alice.post('/api/cards',json={'title':'Private card'}).json()
        assert bob.get('/api/cards').json()==[]
        assert bob.patch(f"/api/cards/{added['id']}",json={'status':'done'}).status_code==404
        assert bob.delete(f"/api/cards/{added['id']}").status_code==404
        assert alice.get('/api/cards').json()[0]['title']=='Private card'
        assert alice.get('/api/cards').json()[0]['status']=='todo'

def test_board_cookie_is_httponly_and_stable(client):
    first=client.get('/api/cards')
    cookie=client.cookies.get('kanban_board')
    assert len(cookie)==64
    assert 'HttpOnly' in first.headers['set-cookie']
    assert 'SameSite=lax' in first.headers['set-cookie']
    client.get('/api/cards')
    assert client.cookies.get('kanban_board')==cookie

def test_cross_origin_writes_rejected(client):
    response=client.post('/api/cards',json={'title':'No cross-site changes'},headers={'Origin':'https://untrusted.example'})
    assert response.status_code==403
