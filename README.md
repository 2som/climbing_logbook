# Climbing Lookbook API

FastAPI backend. JWT auth (HS256), Argon2 password hashing. User lookup currently mocked in-memory.

## Wymagania

- Python >= 3.12
- [Poetry](https://python-poetry.org/) >= 2.0

## Instalacja

```bash
poetry install
```

## Konfiguracja

Skopiuj `.env.example` do `.env` i uzupełnij:

```bash
cp .env.example .env
```

| Zmienna | Opis |
|---|---|
| `AUTH_SECRET_KEY` | Sekret do podpisu JWT. Ustaw własny, długi, losowy. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Czas życia access tokena w minutach (int). |

## Uruchomienie

Dev (hot reload):

```bash
poetry run fastapi dev main.py
```

Prod:

```bash
poetry run fastapi run main.py
```

Domyślnie: http://127.0.0.1:8000

Docs: http://127.0.0.1:8000/docs

## Endpointy

| Metoda | Ścieżka | Opis |
|---|---|---|
| POST | `/auth/login` | Login `{email, password}` → `{access_token, token_type}`. |
| GET | `/auth/user` | Bieżący user. Wymaga `Authorization: Bearer <token>`. |

## Auth

1. POST `/auth/login` z emailem i hasłem.
2. Weź `access_token` z odpowiedzi.
3. Dodaj header `Authorization: Bearer <access_token>` do chronionych requestów.

Użytkownicy są na razie zaszyte w `features/users/users_repository.py` (`fake_users_db`) — brak realnej bazy. Hasło trzymane jako hash Argon2; nowy hash wygenerujesz przez `get_password_hash()` z `libraries/auth`.

## Struktura

```
main.py                 # entrypoint, montuje router auth
api/                    # warstwa HTTP (routery, dependencies, settings)
features/               # logika domenowa (auth, users, training_plans)
libraries/              # współdzielone (JWT encode/decode, hashowanie, errors)
```
