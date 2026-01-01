from fastapi import FastAPI
from api.health import router as health_router
from api.warehouse import router as inventory_router
from api.agent import router as agent_router
from api.slack_listener import router as slack_router

app = FastAPI(
    title="Supply Chain Agent Backend",
    version="1.0"
)

app.include_router(health_router)
app.include_router(inventory_router)
app.include_router(agent_router)
app.include_router(slack_router)