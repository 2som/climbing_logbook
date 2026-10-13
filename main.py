from fastapi import FastAPI
from api.auth.auth_api import router as auth_router
from api.training_plans.training_plans_api import router as training_plans_router
from libraries.db.session import initialize_database

def _register_openapi_security_scheme(app: FastAPI) -> None:
    default_openapi = app.openapi

    def openapi_with_bearer_scheme() -> dict[str, object]:
        schema = default_openapi()
        components = schema.setdefault("components", {})
        components.setdefault("securitySchemes", {})["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Access token issued by api",
        }
        return schema

    app.openapi = openapi_with_bearer_scheme  

initialize_database("sqlite+aiosqlite:////home/ms/projects/climbing_lookbook/lookbook.db")

app = FastAPI()

app.include_router(auth_router)
app.include_router(training_plans_router)
_register_openapi_security_scheme(app)