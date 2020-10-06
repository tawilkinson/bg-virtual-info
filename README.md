# bg-virtual-info

Gets board game information and compiles a json file of services they can be played on. This can then be displayed elsewhere.

## Requirements

- Python 3.7+
- requests
- bs4

## Usage

Run: `python get_info.py`

Optional arguments:
- `-v`, `--verbose`: prints more information to the command line
- `-s`, `--start`: start scraping from a specific number, default = 1
- `-e`, `--end`: stop scraping at a sepcific number, default = 190000
- `-h`, `--help`: displays help text

## Limitations

- Does not handle JavaScript webpages
- Does not fully load the Steam page for official Tabletop Simulator DLC
- Does not search for Tabletop Simulator Workshop items
- Does not do any fuzzy matching

## TODO

- Occasionally checkpoint to file so that if script crashes or is killed you don't lose all scraped data
- Load JavaScript sites so that Tabletopia can be cached
- Cache all Tabletop Simulator DLC
- [Optional] Cache Tabletop Simulator Workshop items
- Google Search to try to find app version. This seems like something that may be already on BGG somewhere, just need to poke around.
