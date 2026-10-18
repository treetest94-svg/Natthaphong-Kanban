import os
import re
import secrets
from typing import Literal
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from dotenv import load_dotenv
from repository import get_repository

load_dotenv(Path(__file__).with_name('.env'))
Status=Literal['todo','doing','done']
class CreateCard(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    title:str=Field(min_length=1,max_length=240)
    status:Status='todo'
    @field_validator('title',mode='before')
    @classmethod
    def trim_title(cls,value): return value.strip() if isinstance(value,str) else value
class UpdateCard(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    title:str|None=Field(default=None,min_length=1,max_length=240)
    status:Status|None=None
    @field_validator('title',mode='before')
    @classmethod
    def trim_title(cls,value): return value.strip() if isinstance(value,str) else value
    @model_validator(mode='after')
    def nonempty(self):
        if not self.model_fields_set or any(getattr(self,name) is None for name in self.model_fields_set):
            raise ValueError('Provide a title or a valid status.')
        return self
class Card(BaseModel):
    id:int
    title:str
    status:Status
    created_at:str

def create_app(repository=None):
    app=FastAPI(title='Natthaphong Kanban API',version='1.0.0',description='Create, list, move, edit and delete cards on a shared Kanban board.')
    origins=[x.strip() for x in os.getenv('ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
    app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST','PATCH','DELETE','OPTIONS'],allow_headers=['Content-Type'])
    def repo(request:Request):
        token=request.state.board_token
        if repository is not None:
            return repository.for_board(token) if hasattr(repository,'for_board') else repository
        return get_repository(token)
    @app.middleware('http')
    async def safe_headers(request:Request,call_next):
        if request.headers.get('content-length','').isdigit() and int(request.headers['content-length'])>8192:
            return JSONResponse({'detail':'Request body is too large.'},status_code=413)
        token=request.cookies.get('kanban_board','')
        new_board=not re.fullmatch(r'[a-f0-9]{64}',token)
        request.state.board_token=secrets.token_hex(32) if new_board else token
        if request.method in ['POST','PATCH','DELETE']:
            origin=request.headers.get('origin')
            if origin and origin not in origins and origin != str(request.base_url).rstrip('/'):
                return JSONResponse({'detail':'Request origin is not allowed.'},status_code=403)
        response=await call_next(request)
        if new_board:
            response.set_cookie('kanban_board',request.state.board_token,max_age=365*24*3600,httponly=True,secure=bool(os.getenv('VERCEL')),samesite='lax',path='/')
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
        if request.url.path.startswith('/api/') or request.url.path in ['/cards','/health']:
            response.headers['Cache-Control']='no-store'
        return response
    @app.exception_handler(Exception)
    async def database_error(_request:Request,_error:Exception):
        return JSONResponse({'detail':'The database request could not be completed. Please try again.'},status_code=503)
    @app.get('/api/health')
    @app.get('/health',include_in_schema=False)
    def health(db=Depends(repo)):
        db.list()
        return {'status':'ok','database':'connected'}
    @app.get('/api/cards',response_model=list[Card])
    @app.get('/cards',response_model=list[Card],include_in_schema=False)
    def list_cards(db=Depends(repo)): return db.list()
    @app.post('/api/cards',status_code=201,response_model=Card)
    @app.post('/cards',status_code=201,response_model=Card,include_in_schema=False)
    def add_card(card:CreateCard,db=Depends(repo)): return db.create(card.model_dump())
    @app.patch('/api/cards/{card_id}',response_model=Card)
    @app.patch('/cards/{card_id}',response_model=Card,include_in_schema=False)
    def update_card(card_id:int,card:UpdateCard,db=Depends(repo)):
        if card_id<1: raise HTTPException(status_code=422,detail='Card ID must be a positive integer.')
        result=db.update(card_id,card.model_dump(exclude_unset=True))
        if result is None: raise HTTPException(status_code=404,detail='Card not found. It may have been deleted by another visitor.')
        return result
    @app.delete('/api/cards/{card_id}',status_code=204)
    @app.delete('/cards/{card_id}',status_code=204,include_in_schema=False)
    def delete_card(card_id:int,db=Depends(repo)):
        if card_id<1: raise HTTPException(status_code=422,detail='Card ID must be a positive integer.')
        if not db.delete(card_id): raise HTTPException(status_code=404,detail='Card not found. It may have been deleted by another visitor.')
        return Response(status_code=204)
    static_dir=Path(__file__).resolve().parent.parent/'public'
    app.frontend('/',directory=str(static_dir),check_dir=False)
    return app
app=create_app()
