from fastapi import FastAPI

def create_app(repository=None):
    return FastAPI(title='Natthaphong Kanban')

app = create_app()
