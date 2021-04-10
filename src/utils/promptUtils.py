from InquirerPy import inquirer as iq

from src.crud import planetCrud


def planet_prompt(database, message="Planet:"):
    return iq.fuzzy(
        message=message,
        choices=planetCrud.get_planet_names(database),
        height=5
    ).execute()
