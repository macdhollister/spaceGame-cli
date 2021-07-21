import enum
import json


class SpecialPlanet(enum.Enum):
    STANDARD = 'Standard World'
    ARTIFACT = 'Artifact World'
    LOGISTICS = 'Logistics Hub'
    FORGE = 'Forge World'
    CONDUIT = 'Conduit World'
    THRONE = 'Throne World'


special_str_to_enum = {
    'Standard World': SpecialPlanet.STANDARD,
    'Artifact World': SpecialPlanet.ARTIFACT,
    'Logistics Hub': SpecialPlanet.LOGISTICS,
    'Forge World': SpecialPlanet.FORGE,
    'Conduit World': SpecialPlanet.CONDUIT,
    'Throne World': SpecialPlanet.THRONE
}


def validate_planets_file(file_name):
    with open(file_name) as f:
        planets = json.load(f)['planets']

    errors = []

    planet_names = list(map(lambda p: p['name'], planets))
    name_counts = {name: planet_names.count(name) for name in planet_names}

    planet_connections = {planet['name']: planet['connections'] for planet in planets}

    for planet in planets:
        if planet['size'] not in ['s', 'm', 'l']:
            errors.append(f"Invalid size for {planet['name']}. Size must be 's', 'm', or 'l'.")

        if 'special' in planet.keys() and planet['special'] not in special_str_to_enum.keys():
            errors.append(f"Invalid special designation for {planet['name']}. Special must be one of: {list(special_str_to_enum.keys())}")

        if not planet['resources'].isdigit():
            errors.append(f"Invalid resource value for {planet['name']}. Resource values must be integers.")

        if name_counts.get(planet['name']) > 1:
            errors.append(f"Planet name '{planet['name']}' occurs multiple times. Names must be unique.")

        if len(planet['connections']) < 1:
            errors.append(f"{planet['name']} has no connections. All planets must have at least one connection.")

        for other in planet_connections.get(planet['name']):
            if planet['name'] not in planet_connections.get(other):
                errors.append(f"{planet['name']} lists {other} as a connection, but {other} does not list {planet['name']}. Connections must be bi-directional.")

    return errors
