
import pathlib as pathlib
import imp as imp

path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')

_world = {}
starting_position = (0, 0)
area_count = 10
room_count = 100


def load_tiles():
    """Parses a file that describes the world space into the _world object."""
    global area_count
    global room_count
    for path in map_list:
        _area = {}
        with open(path.resolve().as_posix(), 'r') as f:
            rows = f.readlines()
        x_max = len(rows[0].split('\t')) #assumes all rows contain the same number of tabs
        area = path.stem.split('.')[0]
        for y in range(len(rows)):
            cols = rows[y].split('\t')
            for x in range(x_max):
                tile_name = cols[x].replace('\n', '')
                if tile_name == 'field_glade':
                    global starting_position
                    starting_position = (x, y)
                _area[(x, y)] = None if tile_name == '' else getattr(module, area)(x, y, area, tile_name, room_number=int(str(area_count) + str(room_count)))
                _world[area] = _area
                room_count += 1
        area_count += 1


def tile_exists(x, y, area):
    area = area.replace(" ", "")
    return _world[area].get((x, y))


def area_rooms(area):
    area = area.replace(" ", "")
    return _world[area]


def area_enemies(area):
    area = area.replace(" ", "")
    all_enemies = []
    all_rooms = area_rooms(area)
    for room in all_rooms:
        if tile_exists(x=room[0], y=room[1], area=area):
            all_enemies.extend(all_rooms[room].enemies)
    return all_enemies


