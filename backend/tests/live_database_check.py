"""Opt-in integration check against configured Supabase, not collected by pytest."""
from secrets import token_hex
from fastapi.testclient import TestClient
from main import create_app

def run():
    app=create_app()
    marker='QA-'+token_hex(4)
    with TestClient(app) as a,TestClient(app) as b:
        assert a.get('/api/health').status_code==200
        first=a.post('/api/cards',json={'title':marker,'status':'todo'})
        assert first.status_code==201,first.text
        card=first.json();cid=card['id']
        assert a.get('/api/cards').json()==[card]
        assert b.get('/api/cards').json()==[]
        assert b.patch(f'/api/cards/{cid}',json={'status':'doing'}).status_code==404
        assert b.delete(f'/api/cards/{cid}').status_code==404
        for status in ['doing','done','todo']:
            assert a.patch(f'/api/cards/{cid}',json={'status':status}).json()['status']==status
        assert a.post('/api/cards',json={'title':'  '}).status_code==422
        assert a.delete(f'/api/cards/{cid}').status_code==204
        assert a.get('/api/cards').json()==[]
    print('PASS: real Supabase create/list/move/delete, private board isolation and invalid-input rejection.')
if __name__=='__main__':run()
