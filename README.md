# Space Game Python CLI

## Requirements

- A python environment is set up (developed with `python 3.9.2` -- compatibility with python 2 is not guaranteed)
- Requirements are installed (`pip install -r requirements.txt`)
- A file named `.env` is created at the base directory of this repo with the following entry (replace `database_name` with whatever you want the database file to be called)  
`DATABASE_URL=sqlite:///database_name.db`

##Scripts

Each script can be run using the following pattern:
```
python <script_name> <command> <arguments>
```
For example
```
python planets.py generate_planets --planets-file game_resources/planets.json
```

By running this without the `<command>` or `<arguments>`, scripts will print out a help message with all available commands and arguments.
Note that any arguments shown in the help message that are surrounded in `[square brackets]` are optional and default values are described
in the help message.

## <u>planet.py</u>
This script manages planets and facilities on planets.  

Commands:
* `generate_planets`  
  Takes in a "planets file" (in JSON format) and builds the map, including all connections.
  An example planets file can be found below.
* `print_planets`  
  Prints out a report of all planets in the map including names, sizes, resource values, colony sizes / owner (if there is one), connections, and facilities.
* `print_single_planet`  
  Prints out a report of a designated planet.
* `claim`  
  Assigns a planet to a player. This method can be used regardless of if the planet is already owned by another player.
* `build_facility`  
  Builds a facility on the planet. Facility names should follow the convention of `<level><type>` for example `BY` or `AF`.
* `destroy_facility`  
  Destroys a facility with a particular type on a designated planet.
  

## <u>faction.py</u>
This script manages all factions, including research and resources.

Commands:
* `generate_factions`  
  Takes in a "factions file" as with the `generate_planets` method of `planet.py`. An example is shown below.

* `print_factions`  
  Prints out all factions including faction names, resources (mp, rp, lp), and research achieved for each module.

* `update_research`  
  Updates a faction's research in a certain ship module to a designated tech level.
  
  
## <u>ship.py</u>
Manages all ships in the game.

Commands:
* `create`  
  Creates a ship on a designated planet belonging to a designated player with a designated set of modules.
  
* `destroy`  
  Destroys a designated ship.
  
* `damage`  
  Damages a designated ship, optional parameter of the amount of damage which defaults to 1.
  
* `restore`  
  Restores a ship to full hit points.
  
* `restore_all`  
  Restores all ships in the game to full hit points.
  
* `move`  
  Moves a designated ship to a designated planet.

## Example JSON files
Example files have been provided in the `game_resources` directory of this repo, which has been added to the `.gitignore` for your convenience.
It is recommended to place files called `planets.json` and `factions.json` in that directory for your own use.

### <u>planets-file</u>
The top level "planets" key is required, and must have a value of an array of json objects.
All fields are required: `name`, `size`, `resources`, `connections` (an array of strings which must be names of other planets)
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

### <u>factions-file</u>
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