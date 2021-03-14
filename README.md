# Space Game Python CLI

## Example JSON files

### planets-file
```
{
  "planets": [
    {
      "name": "planet_a",
      "size": "s",
      "resources": 4,
      "owner": null,
      "facilities": [],
      "connections": ["planet_b", "planet_c"]
    },
    {
      "name": "planet_b",
      "size": "m",
      "resources": 3,
      "owner": null,
      "facilities": [],
      "connections": ["planet_a", "planet_c"]
    },
    {
      "name": "planet_c",
      "size": "l",
      "resources": 2,
      "owner": null,
      "facilities": [],
      "connections": ["planet_a", "planet_b", "planet_d"]
    }
  ]
}
```