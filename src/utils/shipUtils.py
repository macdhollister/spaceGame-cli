from collections import Counter


def get_ships_with_factions(ships):
    grouped_ships = group_ships_by_faction(ships)

    for faction in grouped_ships.keys():
        grouped_ships[faction] = list(map(lambda ship: get_size(ship), grouped_ships[faction]))

    return grouped_ships


def group_ships_by_faction(ships):
    factions = {}
    for ship in ships:
        if ship.owner not in factions:
            factions[ship.owner] = [ship]
        else:
            factions[ship.owner].append(ship)

    return factions


def get_size(ship):
    return int(len(ship.modules) / 2)


def ships_to_str_owned(ship_list):
    ships = list(map(lambda ship: f"<id: {ship.id}, {ship.modules}>", ship_list))
    ships.insert(0, "Owned Ships:")

    return ships


def ships_to_str_observed(ship_list):
    ship_list = list(map(lambda ship: get_size(ship), ship_list))

    counts = Counter(ship_list)

    ship_types = list(counts.keys())
    ship_types.sort()

    display = ""
    for ship_type in ship_types:
        display += f"class {ship_type} x{counts[ship_type]}"

    return display
