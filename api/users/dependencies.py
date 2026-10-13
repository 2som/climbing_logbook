from api.dependencies import DbSession
from features.users import UsersRepository, UsersService


def get_users_service(
    session: DbSession,
):
    repository = UsersRepository(session)
    return UsersService(repository)
