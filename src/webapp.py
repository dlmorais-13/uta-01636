from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.requests import Request
from src.routers import admin, parcels, soils, studies

STATIC_ROUTES = [
    "/",
    "/parcels",
    "/studies",
    "/admin",
    "/admin/data-import",
    "/admin/simulations",
    "/admin/configurations",
]

app = FastAPI(debug=True)


@app.middleware("http")
async def serve_spa(request: Request, call_next):
    # print(f'url_path: {request.url.path}')
    if request.url.path in STATIC_ROUTES:
        return FileResponse("src/static/index.html")

    path = Path(
        os.path.abspath(
            os.path.join(__file__, os.pardir, "static", request.url.path[1:])
        )
    )
    print(f"path: {path} {path.exists()}")
    if path.exists() and path.is_file():
        return FileResponse(path.absolute())

    response = await call_next(request)
    return response


@app.get("/api")
def read_root():
    return {"v": "0.0.1"}


app.include_router(admin.router)
app.include_router(parcels.router)
app.include_router(soils.router)
app.include_router(studies.router)
