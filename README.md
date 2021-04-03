# Space Game Python CLI

## Requirements

- A python environment is set up (developed with `python 3.9.2` -- compatibility with python 2 is not guaranteed)
- Requirements are installed (`pip install -r requirements.txt`)
- A file named `.env` is created at the base directory of this repo with the following entry (replace `database_name` with whatever you want the database file to be called)  
`DATABASE_URL=sqlite:///database_name.db`

##Scripts

Each script can be run using the following pattern:
```
python <script_name> <command>
```
For example
```
python planets.py generate_planets
```

By running this without any `<command>` argument, scripts will print out a help message with all available commands.

## <u>planet.py</u>
This script manages planets and facilities on planets.  

Commands:
* `generate_planets`  
  Prompts for a "planets file" (in JSON format) and builds the map, including all connections.
  An example planets file can be found below. Reads from `game_resources/planets.json` by default.

* `print_planets`  
  Prints out a report of all planets in the map including names, sizes, resource values, colony sizes / owner (if there is one), connections, and facilities.
  Can be printed for a specific faction, which shows _ships_ that are not hidden from the faction (note that this is used for debugging only and planets
  that are not visible to the faction are still shown).

* `print_single_planet`  
  Prints out a report of a designated planet.

* `claim`  
  Assigns a planet to a faction.
  
* `colonize`  
  Colonize a planet for a faction. The planet must be unclaimed and the faction must have a colony ship in orbit which is automatically destroyed.
  
* `upgrade`  
  Upgrades a colony to the next size (colony &#8594; outpost &#8594; stronghold &#8594; fortress)
  
* `damage`  
  Inflicts garrison point damage to a planet.
  
* `restore`  
  Restores a planet's garrison points.
  

## <u>faction.py</u>
This script manages all factions, including research and resources.

Commands:
* `generate_factions`  
  Prompts for a "factions file" as with the `generate_planets` method of `planet.py`. An example is shown below.
  Reads from `game_resources/faction.json` by default.

* `update_research`  
  Updates a faction's research in a certain ship module to a designated tech level.

* `update_resource`  
  Updates a faction's resource count (mp, rp, or lp) to a given new total.
  
* `spend_resource`  
  Spends an amount of `mp` or `rp`.

* `update_all_resources`  
  Calculates incomes for each resource type and updates all factions' resource pools. Can optionally be used for only a single faction.

* `print_factions`  
  Prints out all factions including faction names, resources (mp, rp, lp), and research achieved for each module.
  
  
## <u>ship.py</u>
Manages all ships in the game.

Commands:
* `create`  
  Creates a ship on a designated planet belonging to a designated player with a designated set of modules.
  
* `destroy`  
  Destroys a designated ship.
  
* `damage`  
  Damages a designated ship.
  
* `restore`  
  Restores a ship to full hit points.
  
* `restore_all`  
  Restores all ships in the game to full hit points.
  
* `move`  
  Moves a designated ship to a designated planet. Auto-resolves connected planets for possible destinations.
  
* `get_all`  
  Prints out all ships. Can be filtered by planet name and/or by faction.
  

## <u>facility.py</u>
Manages facilities


* `get_facilities`  
  Prints out all facilities on a planet.

* `create`  
  Creates a basic facility on the given planet with the given type. Type can be the full name (underscored) or abbreviated.
  For example, `--type "planetary_shields"` or `--type "p"` are both valid. Type is case-insensitive.

* `upgrade`  
  Upgrades a facility from basic to intermediate or intermediate to advanced. Throws an error if an advanced facility is upgraded.
  
* `downgrade`  
  Downgrades a facility from advanced to intermediate or intermediate to basic. Destroys the facility if it is already basic.
  
* `damage`  
  Does a single HP point of damage to a facility.
  
* `restore_single`  
  Restores the HP of a single facility.
  
* `restore_all`  
  Restores HP of all facilities on a planet.
  

## <u>report.py</u>

Unlike other scripts, `report.py` takes no commands. It prompts for a faction name and prints out a full ready-to-send report for that faction.

## Example JSON files
Example files have been provided in the `game_resources` directory of this repo, which has been added to the `.gitignore` for your convenience.
It is recommended to place files called `planets.json` and `factions.json` in that directory for your own use.

### <u>Planets File</u>
The top level "planets" key is required, and must have a value of an array of json objects.
All fields other than `special` are required: `name`, `size`, `resources`, `connections` (an array of strings which must be names of other planets).
If `special` is not provided, the planet will default to be a standard world.
```
{
  "planets": [
    {
      "name": "planet_a",
      "size": "s",
      "resources": 4,
      "connections": ["planet_b", "planet_c"]
    },
    {
      "name": "planet_b",
      "special": "Logistics Hub",
      "size": "m",
      "resources": 3,
      "connections": ["planet_a", "planet_c"]
    },
    {
      "name": "planet_c",
      "size": "l",
      "resources": 2,
      "connections": ["planet_a", "planet_b", "planet_d"]
    }
  ]
}
```

### <u>Factions File</u>
The top level "factions" key is required, and must have a value of an array of json objects, each with exactly one
key/value pair giving the name of the faction.
```
{
  "factions": [
    {
      "faction_name": "faction_1"
    },
    {
      "faction_name": "faction_2"
    }
  ]
}
```