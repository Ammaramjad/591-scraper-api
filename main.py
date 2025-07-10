from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.route_land import router as land_router
from routes.route_store import router as store_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(land_router)
app.include_router(store_router)
