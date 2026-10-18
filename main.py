import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'backend'))
from backend.main import app

# Register the Vite build explicitly at the deployment entry point.
app.frontend('/',directory='frontend/dist',check_dir=False)
