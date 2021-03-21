import enum


class FacilityLevel(enum.Enum):
    BASIC = "Basic"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class FacilityType(enum.Enum):
    FACTORY = "factory"
    LABORATORY = "laboratory"
    SHIPYARD = "shipyard"
    RADAR = "radar"
    DEFENSE_GRID = "defense_grid"
    FLEET_HQ = "fleet_hq"
    PLANETARY_SHIELDS = "planetary_shields"
