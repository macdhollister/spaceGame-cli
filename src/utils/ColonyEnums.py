import enum


class ColonyType(enum.Enum):
    COLONY = 'Colony'
    OUTPOST = 'Outpost'
    STRONGHOLD = 'Stronghold'
    FORTRESS = 'Fortress'


colony_type_to_str = {
    ColonyType.COLONY: 'Colony',
    ColonyType.OUTPOST: 'Outpost',
    ColonyType.STRONGHOLD: 'Stronghold',
    ColonyType.FORTRESS: 'Fortress'
}


colony_str_to_type = {
    'Colony': ColonyType.COLONY,
    'Outpost': ColonyType.OUTPOST,
    'Stronghold': ColonyType.STRONGHOLD,
    'Fortress': ColonyType.FORTRESS,
}
