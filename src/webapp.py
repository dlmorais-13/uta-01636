from pathlib import Path
import os
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.requests import Request
from src.routers import admin

STATIC_ROUTES = ['/', '/map', '/admin', '/admin/data-import', '/admin/simulations', '/admin/configurations']

app = FastAPI(debug=True)

@app.middleware("http")
async def serve_spa(request: Request, call_next):
    # print(f'url_path: {request.url.path}')
    if request.url.path in STATIC_ROUTES:
        return FileResponse('src/static/index.html')

    path = Path(os.path.abspath(os.path.join(__file__, os.pardir, 'static', request.url.path[1:])))
    print(f'path: {path} {path.exists()}')
    if path.exists() and path.is_file():
        return FileResponse(path.absolute())

    response = await call_next(request)
    return response

@app.get("/api")
def read_root():
    return {"Hello": "World"}

app.include_router(admin.router)
