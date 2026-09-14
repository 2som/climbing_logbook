from fastapi import FastAPI
from api.auth.auth_api import router as auth_router

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

app = FastAPI()

app.include_router(auth_router)
_register_openapi_security_scheme(app)








# in_memory_acents = []

# class AscentStyleEnum(str, Enum):
#     REDPOINT = 'redpoint'
#     FLASH = 'flash'
#     ONSIGHT = 'onsight'
#     TOP_ROPE = 'top_rope'

# class AscentTypeEnum(str, Enum):
#     ROUTE = 'route'
#     BOULDER = 'boulder'

# class AddAscentRequest(BaseModel):
#     name: str
#     style: AscentStyleEnum
#     type: AscentTypeEnum
#     difficulty: str
#     outdoor: bool = True
#     sector: str | None = None
#     crag: str | None = None
#     rating: int | None = None
#     comment: str | None = None


# @app.get("/auth/test")
# def me(token: Annotated[str, Depends(get_current_user)]):
#     return {
#         "token": token
#     }

# def some_function(message: str):
#     return { "elo": message}

# @app.get("/sectors")
# def get_sectors():
#     pass

# @app.get(path="/crags")
# def get_crags():
#     pass

# @app.get("/boulders")
# def get_boulders():
#     pass

# @app.get("/routes")
# def get_routes():
#     pass


# @app.get("/ascents/counts")
# def get_accents_counts(function: Annotated[dict, Depends(some_function)]):
#     return function
#     return {
#         "routes": len([ascent for ascent in in_memory_acents if ascent["type"] == AscentTypeEnum.ROUTE]),
#         "boulders": len([ascent for ascent in in_memory_acents if ascent["type"] == AscentTypeEnum.BOULDER])
#     }

# @app.get("/ascents")
# def index_ascents(page: int = 1, per_page: int = 10, query: Annotated[str | None, Query(max_length=50)] = None):
#     # TODO CURSOR PAGINATION
#     start = per_page * (page -1)
#     end = start + per_page + 1

#     return {
#         "page": page,
#         "per_page": per_page,
#         "total": len(in_memory_acents),
#         "items": in_memory_acents[start:end]
#     }

# @app.post("/ascents")
# def add_ascent(request: AddAscentRequest):
#     new_ascent = request.model_dump()
#     new_ascent["uuid"] = uuid7()
#     in_memory_acents.append(new_ascent)