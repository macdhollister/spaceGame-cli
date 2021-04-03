from InquirerPy import inquirer as iq

from src.crud import planetCrud


def planet_prompt(database):
    return iq.fuzzy(
        message="Planet:",
        choices=planetCrud.get_planet_names(database),
        height=5
    ).execute()
