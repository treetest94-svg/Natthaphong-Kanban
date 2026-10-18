import os
from functools import lru_cache
from supabase import create_client
from fastapi import HTTPException

class SupabaseCards:
    def __init__(self,client,board_token):
        self.client=client
        self.board_token=board_token
    def call(self,action,**kwargs):
        return self.client.rpc('kanban_cards',{'p_board_token':self.board_token,'p_action':action,**kwargs}).execute().data
    def list(self): return self.call('list')
    def create(self,values): return self.call('create',p_title=values['title'],p_status=values.get('status','todo'))
    def update(self,card_id,values): return self.call('update',p_card_id=card_id,p_title=values.get('title'),p_status=values.get('status'))
    def delete(self,card_id): return bool(self.call('delete',p_card_id=card_id))

@lru_cache
def get_client():
    url=os.getenv('SUPABASE_URL')
    key=os.getenv('SUPABASE_PUBLISHABLE_KEY')
    if not url or not key:
        raise HTTPException(status_code=503,detail='The database is not configured. Please contact the board owner.')
    return create_client(url,key)
def get_repository(board_token): return SupabaseCards(get_client(),board_token)
