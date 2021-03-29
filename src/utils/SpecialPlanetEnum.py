import enum


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
