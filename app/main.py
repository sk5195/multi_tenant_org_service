from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.db.mongo import close_mongo_connection, connect_to_mongo, ensure_master_indexes
from app.routes.admin import router as admin_router
from app.routes.org import router as org_router

app = FastAPI(title="Multi-Tenant Org Service")


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return """
    <html>
      <head><title>Multi-Tenant Org Service</title></head>
      <body>
        <h2>Multi-Tenant Org Service</h2>
        <p>API documentation: <a href=\"/docs\">/docs</a></p>
      </body>
    </html>
    """.strip()


@app.on_event("startup")
async def on_startup() -> None:
    connect_to_mongo()
    await ensure_master_indexes()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    close_mongo_connection()


app.include_router(admin_router)
app.include_router(org_router)
