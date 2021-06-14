
import pathlib as pathlib
import imp as imp

from app.main import areas


path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')

class World:
    def __init__(self, **kwargs):
        self._world = {}
        self.starting_position = (0, 0)
        self._area_count = 10

    def load_tiles(self):
        """Parses a file that describes the world space into the _world object."""
        for path in map_list:
            area_name = path.stem.split('.')[0]
            area = areas.Area(area_name=area_name, area_path=path, area_number=self._area_count)
            self._world[area_name] = area

            self._area_count += 1
        return

    def tile_exists(self, x, y, area):
        area = area.replace(" ", "")
        return self._world[area].tile_exists(x=x, y=y)

    def area_rooms(self, area):
        area = area.replace(" ", "")
        return self._world[area]

    def area_enemies(self, area):
        area = area.replace(" ", "")
        return self._world[area].area_enemies(area)

world_map = World()
world_map.load_tiles()
for area in world_map._world:
    world_map._world[area].spawn_enemies()




