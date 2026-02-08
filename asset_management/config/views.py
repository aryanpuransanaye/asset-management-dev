from django.shortcuts import render
from django.conf import settings
from pathlib import Path

def serve_frontend(request):

    frontend_path = Path(settings.BASE_DIR) / 'frontend_dist' / 'index.html'
    
    if not frontend_path.exists():
        raise FileNotFoundError(frontend_path)

    return render(request, str(frontend_path))