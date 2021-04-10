from InquirerPy import inquirer as iq

from src.crud import planetCrud, factionCrud


def planet_prompt(database, message="Planet:"):
    return iq.fuzzy(
        message=message,
        choices=planetCrud.get_planet_names(database),
        height=5
    ).execute()


def faction_prompt(database, message="Faction:"):
    return iq.select(
        message=message,
        choices=factionCrud.get_faction_names(database)
    ).execute()
