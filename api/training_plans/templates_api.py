from fastapi import APIRouter


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/phases")
def get_phases_templates():
    pass


@router.get("/sessions")
def get_sessions_templates():
    pass


@router.get("/exercises")
def get_exercises_templates():
    pass
