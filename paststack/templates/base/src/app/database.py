"""Accès données : démarrage / arrêt du moteur ou pool, état « DB prête »."""


async def lifespan_startup() -> None:
    return


async def lifespan_shutdown() -> None:
    return


def is_database_configured() -> bool:
    return False
