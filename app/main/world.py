
import pathlib as pathlib
import imp as imp

from app import db
from app.main import areas
from app.main.models import Area

world_map = None

path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')

class World:
    def __init__(self, **kwargs):
        self._world = {}
        self.starting_position = (0, 0)
        self._area_count = 10

    def load_areas(self):
        """Parses a file that describes the world space into the _world object."""
        for path in map_list:
            area_name = path.stem.split('.')[0]
            area_object = areas.Area(area_name=area_name, 
                                     area_path=path, 
                                     area_number=self._area_count)
            area = Area(area=areas.Area(area_name=area_name, 
                                        area_path=path, 
                                        area_number=self._area_count,
                        ),
                        area_name=area_name
            )
            db.session.add(area)
            self._world[area_name] = area_object
            self._area_count += 1
        db.session.commit()
        return

    def load_rooms(self):
        for area in self._world:
            self._world[area].create_rooms()

    def tile_exists(self, x, y, area):
        area_name = area.replace(" ", "")
        area = db.session.query(Area).filter_by(area_name=area_name).first()
        return area.area.tile_exists(area_name=area_name, x=x, y=y)

    def area_rooms(self, area):
        area = area.replace(" ", "")
        return self._world[area]

    def area_enemies(self, area):
        area = area.replace(" ", "")
        return self._world[area].area_enemies(area)

def create_world(app):
    global world_map
    world_map = World()
    world_map.load_areas()
    world_map.load_rooms()
    # for area in world_map._world:
    #     world_map._world[area].spawn_enemies(app)
    




