import enum
from collections import Counter


class FacilityLevel(enum.Enum):
    BASIC = 'Basic'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'


class FacilityType(enum.Enum):
    FACTORY = 'factory'
    LABORATORY = 'laboratory'
    SHIPYARD = 'shipyard'
    RADAR = 'radar'
    DEFENSE_GRID = 'defense_grid'
    FLEET_HQ = 'fleet_hq'
    PLANETARY_SHIELDS = 'planetary_shields'


type_to_abbreviated_str = {
    FacilityType.FACTORY: 'F',
    FacilityType.LABORATORY: 'L',
    FacilityType.SHIPYARD: 'Y',
    FacilityType.RADAR: 'R',
    FacilityType.DEFENSE_GRID: 'D',
    FacilityType.FLEET_HQ: 'Q',
    FacilityType.PLANETARY_SHIELDS: 'P'
}

type_to_str = {
    FacilityType.FACTORY: 'Factory',
    FacilityType.LABORATORY: 'Laboratory',
    FacilityType.SHIPYARD: 'Shipyard',
    FacilityType.RADAR: 'Radar',
    FacilityType.DEFENSE_GRID: 'Defense Grid',
    FacilityType.FLEET_HQ: 'Fleet HQ',
    FacilityType.PLANETARY_SHIELDS: 'Planetary Shield'
}

type_to_enum = {
    'factory': FacilityType.FACTORY,
    'f': FacilityType.FACTORY,
    'laboratory': FacilityType.LABORATORY,
    'l': FacilityType.LABORATORY,
    'shipyard': FacilityType.SHIPYARD,
    'y': FacilityType.SHIPYARD,
    'radar': FacilityType.RADAR,
    'r': FacilityType.RADAR,
    'defense_grid': FacilityType.DEFENSE_GRID,
    'd': FacilityType.DEFENSE_GRID,
    'fleet_hq': FacilityType.FLEET_HQ,
    'q': FacilityType.FLEET_HQ,
    'planetary_shields': FacilityType.PLANETARY_SHIELDS,
    'p': FacilityType.PLANETARY_SHIELDS
}

level_to_abbreviated_str = {
    FacilityLevel.BASIC: 'B',
    FacilityLevel.INTERMEDIATE: 'I',
    FacilityLevel.ADVANCED: 'A'
}

level_to_str = {
    FacilityLevel.BASIC: 'Basic',
    FacilityLevel.INTERMEDIATE: 'Intermediate',
    FacilityLevel.ADVANCED: 'Advanced'
}

level_to_enum = {
    'basic': FacilityLevel.BASIC,
    'b': FacilityLevel.BASIC,
    'intermediate': FacilityLevel.INTERMEDIATE,
    'i': FacilityLevel.INTERMEDIATE,
    'advanced': FacilityLevel.ADVANCED,
    'a': FacilityLevel.ADVANCED
}


def display_facilities(facilities):
    counts = Counter(facilities)
    types_array = []

    for fac_type in counts.keys():
        types_array.append(f"{fac_type}{' x'+str(counts.get(fac_type)) if counts.get(fac_type) > 1 else ''}")

    if len(types_array) > 0:
        return f"[{', '.join(types_array)}]"
    else:
        return "No facilities"
