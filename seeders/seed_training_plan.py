"""Seed the simplified PCC winter 2026/27 plan (PLAN_ZIMA_2026_PCC_UPROSZCZONY.md).

Usage:
    poetry run python -m seeders.seed_training_plan --email user@example.com [--start-date 2026-10-26]

Creates the exercise template library (skipped per template if a template with
the same name already exists), the plan with its phases, sessions and
exercises, and optionally activates it. Idempotent: an existing plan with the
same name for the user is left untouched.
"""

import argparse
import asyncio
import datetime
from dataclasses import dataclass, field

from sqlalchemy import select

from features.training_plans.models.enum import ExerciseUnitEnum as U
from features.training_plans.models.enum import SessionTypeEnum as T
from features.training_plans.models.training_plan import (
    ActiveTrainingPlan,
    Exercise,
    Phase,
    Session,
    TrainingPlan,
)
from features.training_plans.models.training_plan_templates import ExerciseTemplate
from features.users.model import UserModel
from libraries.db.session import initialize_database, open_session

PLAN_NAME = "Plan zima 2026/27: 7b"
DEFAULT_DB_URL = "sqlite+aiosqlite:////home/ms/projects/climbing_lookbook/lookbook.db"


@dataclass
class Tpl:
    name: str
    description: str
    feedback_enabled: bool = False
    sets: int | None = None
    repetitions: int | None = None
    duration_seconds: int | None = None
    unit: U | None = None
    unit_label: str | None = None


@dataclass
class Ex:
    """Exercise position in a session: template name + overrides."""

    template: str
    description: str | None = None
    sets: int | None = None
    repetitions: int | None = None
    duration_seconds: int | None = None


@dataclass
class Sess:
    name: str
    type: T
    duration_minutes: int
    description: str | None
    exercises: list[Ex] = field(default_factory=list)


@dataclass
class Ph:
    name: str
    description: str
    duration_weeks: int
    sessions: list[Sess] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Exercise template library (legend from the plan)
# --------------------------------------------------------------------------- #

TEMPLATES: list[Tpl] = [
    # warm up / cool down
    Tpl("Climbing Movement Prep", "Jumping Jacks x10, Seal Jacks x10, Leg Kicks x5/str., Circle Kicks x3/str., Inchworms x3, Spidermans x3/str., Can Opener x5/str., Hip Bridge x5/str., krążenia nadgarstków i finger flicks x20.", duration_seconds=300),
    Tpl("On the Wall Mobility", "Bardzo łatwy teren: drop knee, high step, heel hook, zakresy barków i bioder. Bez pompy.", duration_seconds=600),
    Tpl("Contrast Warm Up", "Ten sam bald 2x: raz bardzo powoli bez rozmachu, raz z rozmachem z nóg.", sets=2),
    Tpl("One Touch", "Każda ręka i stopa kładziona raz. Źle postawiłeś, zostaje.", sets=2),
    Tpl("Rhythm Cool Down", "Łatwe baldy, rytm, spokojny oddech.", sets=2),
    Tpl("Route Warm Up", "Łatwe drogi, rosnąca trudność, płynnie, wpinki z dobrych stanowisk.", sets=2),
    Tpl("Route Warm Up (Pacing)", "Łatwa droga odrobinę szybciej niż zwykle, precyzja zostaje.", sets=1),
    Tpl("Route Cool Down", "Bardzo łatwa droga, oddech, luźno.", sets=1),
    Tpl("Hangboard Warm Up", "Krążenia ramion, podciągnięcia na klamie, scapular pull ups, finger flicks, zwisy BW na coraz mniejszych chwytach, potem zwisy z rosnącym dociążeniem.", duration_seconds=600),
    # bouldering
    Tpl("Perfect Repeat", "Bald ok. flash, 3-5 razy, każde przejście czystsze: bez poprawek, bez szarpania, dobre tempo. Ten sam bald przez kilka sesji.", sets=1, repetitions=4),
    Tpl("Boulder Mini Project", "Bald do zrobienia w kilka sesji. Max 15-20 min na jeden. Padł w 1 sesji: następny o stopień trudniej.", duration_seconds=1800),
    Tpl("Single Session Sends", "Baldy na 3-7 prób, do zrobienia w 1 sesji. Różne style, kąty, chwyty.", duration_seconds=2400),
    Tpl("Three Strike", "Newcomers: nowy bald tuż nad flashem, 3 próby łącznie. Repeat Circuit: najtrudniejsze zrobione baldy, 3 próby każdy, 3+ min przerwy. Trzecie odpadnięcie, idziesz dalej.", sets=2, repetitions=3),
    Tpl("Limit Bouldering", "1-5 ruchów blisko maksa na zwykłej ścianie, bez boardu. Różne kąty i chwyty. Długie przerwy. Koniec, gdy siada koordynacja.", duration_seconds=1200),
    Tpl("Spraywall Endurance Circuit", "Circuit 20-30 ruchów 50-60% maksa pod rząd, potem 4 min rest stance na ścianie. Progresja: więcej rund, gorszy rest stance, gorsze stopy, dłuższy circuit. Odpadasz w dwóch rundach pod rząd: krok wstecz.", feedback_enabled=True, sets=2, unit=U.COUNT, unit_label="rundy"),
    Tpl("Boulder Intervals", "2 baldy V3-V4 pod rząd + 2 min rest stance + 1 min na ziemi = runda. Odpadanie dopiero pod koniec, wcześniej = za trudno.", feedback_enabled=True, sets=3, unit=U.COUNT, unit_label="rundy"),
    Tpl("Projekt na skałach", "Od wejścia projekt. Jeden projekt 60-90 min, 8-10 min przerwy. Metryka: do którego ruchu.", feedback_enabled=True, sets=1, unit=U.COUNT, unit_label="ruch (high point)"),
    # routes
    Tpl("Route Mini Project", "Mini projekt 6b+ - 6c+, 2-3 sesje. Kolejność: bolt-to-bolt, links, overlaps, RP. 15-20 min przerwy. Padł w 1 sesji: widełki w górę.", feedback_enabled=True, sets=2, unit=U.COUNT, unit_label="bolt (high point)"),
    Tpl("Route Project", "Projekt 6c+ - 7a, 4-8 sesji. Kolejność: bolt-to-bolt, links, overlaps, high point / low point, RP. 15-20 min przerwy.", feedback_enabled=True, sets=2, unit=U.COUNT, unit_label="bolt (high point)"),
    Tpl("UDU Project", "Lead bez wpinania stanu, zejście odpinając, od razu w górę. Zatrzymuj się na odpoczynkach, wytrzepuj. Notuj bolt w drugim wejściu.", feedback_enabled=True, sets=2, unit=U.COUNT, unit_label="bolt w drugim wejściu"),
    Tpl("Steep Laps", "Stroma droga 5c-6a, wszystkie przejścia lead, 2 min przerwy. Odpadłeś: zjazd, przerwa, następne.", feedback_enabled=True, sets=3, unit=U.COUNT, unit_label="przejścia"),
    Tpl("Vert Laps", "Pion ~1 stopień pod OS, pierwsze lead, reszta wędka, bez przerwy, do odpadnięcia.", feedback_enabled=True, sets=1, unit=U.COUNT, unit_label="przejścia"),
    Tpl("Drogi w pacingu (objętość)", "Drogi 6a - 6a+ na lead w pacingu, 5 min przerwy między drogami. Pewność, wpinki, pacing, głowa.", feedback_enabled=True, sets=5, unit=U.COUNT, unit_label="drogi czysto"),
    # hangboard
    Tpl("Max Hangs 7/53", "Half crimp, 4 palce, 20mm, 7s zwis / 53s przerwa, 1 zwis = 1 seria. Ostatnie zwisy trudne, z zapasem ~2s. Dociążenie sięga 50% masy ciała: mniejsza krawędź.", feedback_enabled=True, sets=5, duration_seconds=7, unit=U.KG, unit_label="dociążenie"),
    Tpl("Minimum Edge Hangs 7/53", "Jak Max Hangs, na krawędzi z testu. Czysto: mniejsza krawędź, na najmniejszej: małe dociążenie.", feedback_enabled=True, sets=5, duration_seconds=7, unit=U.MM, unit_label="krawędź"),
    Tpl("Find the Max Hang Weight", "Kg na 20mm half crimp na 10-12s, 2-3 min przerwy.", feedback_enabled=True, sets=1, duration_seconds=10, unit=U.KG, unit_label="dociążenie"),
    Tpl("Find the Minimum Edge", "Najmniejsza krawędź na 10-12s half crimp, forma trzyma.", feedback_enabled=True, sets=1, duration_seconds=10, unit=U.MM, unit_label="krawędź"),
    # gym
    Tpl("Podciągnięcia z obciążeniem", "Nachwyt, pełny zakres, bez kipu, powoli w dół. Ostatnia seria trudna, ale czysta.", feedback_enabled=True, sets=4, repetitions=5, unit=U.KG, unit_label="obciążenie"),
    Tpl("Eksplozywne podciągnięcia", "Bez obciążenia, mostek do drążka, minimalny kip, powoli w dół.", sets=3, repetitions=3),
    Tpl("Wyciskanie na ławce", "Łopatki ściągnięte, stopy na ziemi, sztanga do dolnej części klatki. RPE 7 = 3 powtórzenia w zapasie, 8 = 2, 9 = 1.", feedback_enabled=True, sets=3, repetitions=10, unit=U.KG, unit_label="ciężar"),
    Tpl("Przysiady", "Sztanga na plecach lub front squat, do równoległości. Ból pleców: goblet squat lub Bulgarian split squat.", feedback_enabled=True, sets=3, repetitions=10, unit=U.KG, unit_label="ciężar"),
    Tpl("Mięśnie antagonistyczne + core", "2 z: face pull 3x15, rotacja zewnętrzna barku 3x15, reverse wrist curl 3x15, dipy lub pompki 3x8. 1 z: hanging knee raises 3x10, hollow body hold 3x30s, side plank 3x30s.", duration_seconds=600),
    # tests
    Tpl("Max flash bald", "Najtrudniejszy bald na flash + 3 najtrudniejsze zrobione (lista do Three Strike).", feedback_enabled=True, sets=1, unit=U.COUNT, unit_label="V"),
    Tpl("Podciągnięcie z obciążeniem 5RM", "Ciężar na 5 czystych powtórzeń.", feedback_enabled=True, sets=1, repetitions=5, unit=U.KG, unit_label="obciążenie"),
]


# --------------------------------------------------------------------------- #
# Sessions
# --------------------------------------------------------------------------- #

WARMUP_BOULDER = [
    Ex("Climbing Movement Prep"),
    Ex("On the Wall Mobility"),
    Ex("Contrast Warm Up", "2 łatwe baldy"),
    Ex("One Touch", "2 średnie baldy"),
]
WARMUP_ROUTE = [
    Ex("Climbing Movement Prep"),
    Ex("On the Wall Mobility"),
    Ex("Route Warm Up", "2 łatwe drogi"),
    Ex("Route Warm Up (Pacing)", "1 średnia droga"),
]
WARMUP_GYM = [Ex("Climbing Movement Prep"), Ex("Hangboard Warm Up")]
COOL_BOULDER = [Ex("Rhythm Cool Down", "2 łatwe baldy")]
COOL_ROUTE = [Ex("Route Cool Down", "1 łatwa droga")]


def gym(hang: Ex, pullups: Ex, bench_squat_sets: int, bench_squat_reps: int, rpe: str, extra: list[Ex] | None = None) -> Sess:
    return Sess("Wt: siłownia (SST)", T.GYM, 60, "Hangboard na początku, na świeżych palcach. Ciężary w górę, gdy wszystkie serie czyste.", [
        *WARMUP_GYM,
        hang,
        pullups,
        *(extra or []),
        Ex("Wyciskanie na ławce", f"RPE {rpe}", sets=bench_squat_sets, repetitions=bench_squat_reps),
        Ex("Przysiady", f"RPE {rpe}", sets=bench_squat_sets, repetitions=bench_squat_reps),
        Ex("Mięśnie antagonistyczne + core"),
    ])


BOULDER_POWER = Sess("Pn: baldy, moc", T.STRENGTH_POWER, 120, "Na świeżo. Bez hangboardu.", [
    *WARMUP_BOULDER,
    Ex("Three Strike", "F2 tydzień 1: Newcomers (1 nowy bald). Potem Repeat Circuit: 2 najtrudniejsze zrobione baldy."),
    Ex("Boulder Mini Project", "30-45 min", duration_seconds=2400),
    Ex("Limit Bouldering", "F2: 15-20 min, F3: do 30 min. Bez boardu."),
    *COOL_BOULDER,
])

ROUTE_VOLUME = Sess("Cz: liny, objętość lekka", T.ENDURANCE, 75, "Tylko F1 i F2, gdy jest partner. Zamiast Cz baldy. Sb bez zmian.", [
    Ex("Climbing Movement Prep"),
    Ex("On the Wall Mobility"),
    Ex("Route Warm Up", "1 łatwa droga", sets=1),
    Ex("Drogi w pacingu (objętość)", "4-5 dróg 6a - 6a+ na lead, pacing, 5 min przerwy"),
    *COOL_ROUTE,
])

PHASES: list[Ph] = [
    Ph("Testy", "5 testów, punkt odniesienia. Reszta tygodnia luźno, bez projektowania.", 1, [
        Sess("Wt: testy siłownia", T.GYM, 60, "Find the Max Hang Weight + punkt odniesienia na siłowni.", [
            *WARMUP_GYM,
            Ex("Find the Max Hang Weight"),
            Ex("Podciągnięcie z obciążeniem 5RM"),
            Ex("Wyciskanie na ławce", "ciężar na 3x10 przy RPE 7"),
            Ex("Przysiady", "ciężar na 3x10 przy RPE 7"),
        ]),
        Sess("Cz: testy baldy", T.OPEN, 90, "Max flash bald + lista 3 najtrudniejszych zrobionych.", [
            *WARMUP_BOULDER,
            Ex("Max flash bald"),
            *COOL_BOULDER,
        ]),
        Sess("Sb: testy liny", T.OPEN, 120, "UDU i Vert Laps baseline na 6a.", [
            *WARMUP_ROUTE,
            Ex("UDU Project", "punkt odniesienia: do którego bolta w drugim wejściu", sets=1),
            Ex("Vert Laps", "punkt odniesienia: ile przejść do odpadnięcia"),
            *COOL_ROUTE,
        ]),
    ]),
    Ph("Faza 1: siła + wytrzymałość ogólna", "Max Hangs, Perfect Repeat, mini projekty, spraywall, UDU. Tydzień 4 = deload: połowa serii i rund.", 4, [
        Sess("Pn: baldy, siła", T.STRENGTH_POWER, 120, "Na świeżo. Bez hangboardu.", [
            *WARMUP_BOULDER,
            Ex("Perfect Repeat", "1 średni bald, 3-5 powtórzeń"),
            Ex("Boulder Mini Project", "15-30 min"),
            Ex("Single Session Sends", "30-45 min"),
            *COOL_BOULDER,
        ]),
        gym(Ex("Max Hangs 7/53", "start 5 zwisów, ~90% z testu. Wszystkie czyste: +1 zwis", sets=5),
            Ex("Podciągnięcia z obciążeniem", "4x5, 2-3 min przerwy", sets=4, repetitions=5),
            3, 10, "7"),
        Sess("Cz: baldy, wytrzymałość ogólna", T.ENDURANCE, 90, "Można zacząć lekko zmęczony.", [
            *WARMUP_BOULDER,
            Ex("Boulder Mini Project", "15 min", duration_seconds=900),
            Ex("Spraywall Endurance Circuit", "start 2 rundy, 4 min rest stance", sets=2),
            *COOL_BOULDER,
        ]),
        ROUTE_VOLUME,
        Sess("Sb: liny, wytrzymałość", T.ENDURANCE, 150, "Zawsze liny.", [
            *WARMUP_ROUTE,
            Ex("Route Mini Project", "1-2 próby"),
            Ex("UDU Project", "6a, ta sama droga cały cykl, 2-3 próby, 8-10 min przerwy"),
            Ex("Vert Laps", "tylko tydzień 3: do odpadnięcia"),
            *COOL_ROUTE,
        ]),
    ]),
    Ph("Faza 2: moc + wytrzymałość", "Max Hangs, Three Strike, Limit, nowy spraywall circuit, pierwszy projekt, Steep Laps. Tydzień 4 = deload (święta): połowa serii i rund, Find the Minimum Edge zamiast Max Hangs.", 4, [
        BOULDER_POWER,
        gym(Ex("Max Hangs 7/53", "start 7 zwisów. Wszystkie czyste: +1 zwis, max 9, potem +kg. Deload: Find the Minimum Edge", sets=7),
            Ex("Podciągnięcia z obciążeniem", "5x3, ciężej niż F1, 3 min przerwy", sets=5, repetitions=3),
            4, 6, "8"),
        Sess("Cz: baldy, wytrzymałość", T.ENDURANCE, 100, "Nowy circuit V2-V3 zbudowany w deloadzie F1.", [
            *WARMUP_BOULDER,
            Ex("Boulder Mini Project", "15 min", duration_seconds=900),
            Ex("Limit Bouldering", "15 min", duration_seconds=900),
            Ex("Spraywall Endurance Circuit", "start 3 rundy", sets=3),
            *COOL_BOULDER,
        ]),
        ROUTE_VOLUME,
        Sess("Sb: liny, projekt + Steep Laps", T.PROJECT, 150, "Projekt pierwszy, laps po 15 min przerwy.", [
            *WARMUP_ROUTE,
            Ex("Route Mini Project", "1 próba", sets=1),
            Ex("Route Project", "1-2 próby, 15 min przerwy"),
            Ex("Steep Laps", "start 3 przejścia, lead, 2 min przerwy"),
            *COOL_ROUTE,
        ]),
    ]),
    Ph("Faza 3: wytrzymałość siłowa", "Min Edge Hangs, Three Strike, Limit, Boulder Intervals, projekt. Cz zawsze baldy. Ostatni tydzień bez rekordów na ławce i przysiadzie.", 3, [
        BOULDER_POWER,
        gym(Ex("Minimum Edge Hangs 7/53", "start 5 zwisów, krawędź z deloadu F2. Wszystkie czyste: +1 zwis, max 7, potem mniejsza krawędź", sets=5),
            Ex("Podciągnięcia z obciążeniem", "5x3", sets=5, repetitions=3),
            5, 3, "8-9",
            extra=[Ex("Eksplozywne podciągnięcia", "3x3 po seriach z obciążeniem")]),
        Sess("Cz: baldy, wytrzymałość siłowa", T.ENDURANCE, 100, "W F3 zawsze baldy, bez alternatywy linowej.", [
            *WARMUP_BOULDER,
            Ex("Three Strike", "Repeat Circuit: 1 trudny bald", sets=1),
            Ex("Boulder Mini Project", "do 30 min"),
            Ex("Boulder Intervals", "3 rundy. Co tydzień 1 bald w rundzie trudniej"),
            *COOL_BOULDER,
        ]),
        Sess("Sb: liny, projekt", T.PROJECT, 120, "Tylko projekt, jakość prób. Projekt padł: OS 6b / 6b+, 1 próba.", [
            *WARMUP_ROUTE,
            Ex("Route Project", "2-3 próby, 15-20 min przerwy", sets=3),
            *COOL_ROUTE,
        ]),
    ]),
    Ph("Retest", "Objętość deloadu + 5 testów z tygodnia 0. Nd + Pn pełny odpoczynek.", 1, [
        Sess("Wt: retest siłownia", T.GYM, 60, "Bez normalnego SST.", [
            *WARMUP_GYM,
            Ex("Find the Max Hang Weight"),
            Ex("Podciągnięcie z obciążeniem 5RM"),
            Ex("Wyciskanie na ławce", "3x10 RPE 7"),
            Ex("Przysiady", "3x10 RPE 7"),
        ]),
        Sess("Cz: retest baldy", T.OPEN, 90, "Max flash + Three Strike na baldach z tygodnia 0.", [
            *WARMUP_BOULDER,
            Ex("Max flash bald"),
            Ex("Three Strike", "Repeat Circuit na baldach z tygodnia 0"),
            *COOL_BOULDER,
        ]),
        Sess("Sb: retest liny", T.OPEN, 120, "UDU i Vert Laps jak w tygodniu 0, porównaj. Potem 1 próba na projekcie na luzie.", [
            *WARMUP_ROUTE,
            Ex("UDU Project", "ta sama droga co w tygodniu 0", sets=1),
            Ex("Vert Laps", "punkt odniesienia, porównaj z tygodniem 0"),
            Ex("Route Project", "1 próba na luzie", sets=1),
            *COOL_ROUTE,
        ]),
    ]),
]


# --------------------------------------------------------------------------- #
# Seeding
# --------------------------------------------------------------------------- #

async def seed_templates(session) -> dict[str, ExerciseTemplate]:
    existing = {t.name: t for t in (await session.execute(select(ExerciseTemplate))).scalars()}
    out: dict[str, ExerciseTemplate] = {}
    for tpl in TEMPLATES:
        if tpl.name in existing:
            out[tpl.name] = existing[tpl.name]
            continue
        row = ExerciseTemplate(**tpl.__dict__)
        session.add(row)
        out[tpl.name] = row
    await session.flush()
    return out


def build_exercise(ex: Ex, tpl: ExerciseTemplate, order: int, session_row: Session) -> Exercise:
    return Exercise(
        session_uuid=session_row.uuid,
        exercise_template_uuid=tpl.uuid,
        name=tpl.name,
        description=ex.description or tpl.description,
        order=order,
        feedback_enabled=tpl.feedback_enabled,
        sets=ex.sets if ex.sets is not None else tpl.sets,
        repetitions=ex.repetitions if ex.repetitions is not None else tpl.repetitions,
        duration_seconds=ex.duration_seconds if ex.duration_seconds is not None else tpl.duration_seconds,
        unit=tpl.unit,
        unit_label=tpl.unit_label,
    )


async def seed_plan(session, user: UserModel, templates: dict[str, ExerciseTemplate]) -> TrainingPlan:
    plan = TrainingPlan(user_uuid=user.uuid, name=PLAN_NAME)
    session.add(plan)
    await session.flush()
    for order, ph in enumerate(PHASES, start=1):
        phase = Phase(plan_uuid=plan.uuid, name=ph.name, description=ph.description, duration_weeks=ph.duration_weeks, order=order)
        session.add(phase)
        await session.flush()
        for s in ph.sessions:
            row = Session(plan_uuid=plan.uuid, phase_uuid=phase.uuid, name=s.name, description=s.description, duration_minutes=s.duration_minutes, type=s.type)
            session.add(row)
            await session.flush()
            for i, ex in enumerate(s.exercises, start=1):
                session.add(build_exercise(ex, templates[ex.template], i, row))
    await session.flush()
    return plan


async def activate(session, user: UserModel, plan: TrainingPlan, start: datetime.date) -> None:
    weeks = sum(ph.duration_weeks for ph in PHASES)
    session.add(ActiveTrainingPlan(user_uuid=user.uuid, plan_uuid=plan.uuid, start_date=start, end_date=start + datetime.timedelta(weeks=weeks) - datetime.timedelta(days=1)))


async def run(email: str, start: datetime.date | None, db_url: str) -> None:
    initialize_database(db_url)
    async with open_session() as session:
        user = (await session.execute(select(UserModel).where(UserModel.email == email))).scalar_one_or_none()
        if user is None:
            raise SystemExit(f"user not found: {email}")
        exists = (await session.execute(select(TrainingPlan).where(TrainingPlan.user_uuid == user.uuid, TrainingPlan.name == PLAN_NAME))).scalar_one_or_none()
        if exists is not None:
            raise SystemExit(f"plan already exists: {PLAN_NAME} ({exists.uuid})")
        templates = await seed_templates(session)
        plan = await seed_plan(session, user, templates)
        if start is not None:
            await activate(session, user, plan, start)
        await session.commit()
        n_sessions = sum(len(ph.sessions) for ph in PHASES)
        n_ex = sum(len(s.exercises) for ph in PHASES for s in ph.sessions)
        print(f"seeded plan {plan.uuid}: {len(PHASES)} phases, {n_sessions} sessions, {n_ex} exercises, {len(templates)} templates")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--email", required=True)
    parser.add_argument("--start-date", type=datetime.date.fromisoformat, default=None, help="activate the plan from this date (YYYY-MM-DD)")
    parser.add_argument("--db-url", default=DEFAULT_DB_URL)
    args = parser.parse_args()
    asyncio.run(run(args.email, args.start_date, args.db_url))


if __name__ == "__main__":
    main()
