
import pathlib as pathlib
import imp as imp
import random as random

from app import db
from app.main import areas, tiles
from app.main.models import Area, Room

path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')
starting_position = (0,0)
starting_area = 'Field'

class World:
    def __init__(self, **kwargs):
        self._world = {}
        self.starting_position = (0, 0)
        self._area_count = 10

    def load_areas(self):
        """Parses a file that describes the world space into the database."""
        for path in map_list:
            area_name = path.stem.split('.')[0]
            area_exists = db.session.query(Area).filter_by(area_name=area_name).first()
            if not area_exists:
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
        return

    def load_rooms(self):
        for area in self._world:
            self._world[area].create_rooms()

    def area_rooms(self, area):
        area = area.replace(" ", "")
        return self._world[area]

    def area_enemies(self, area):
        area = area.replace(" ", "")
        return self._world[area].area_enemies(area)

    # for area in world_map._world:
    #     world_map._world[area].spawn_enemies(app)

def load_world():
    area_count = 10
    room_count = 100
    """Parses a file that describes the world space into the database."""
    for path in map_list:
        area_name = path.stem.split('.')[0]
        area_exists = db.session.query(Area).filter_by(area_name=area_name).first()
        if not area_exists:
            area = Area(area=areas.Area(area_name=area_name, 
                                        area_path=path, 
                                        area_number=area_count,
                        ),
                        area_name=area_name
            )
            db.session.add(area)
            print("Created {} area with area number {}".format(area_name, area_count))
        else:
            area = area_exists
            print("Area {} already exists".format(area_name))
        area_count += 1

        with open(path.resolve().as_posix(), 'r') as f:
            rows = f.readlines()
        x_max = len(rows[0].split('\t')) #assumes all rows contain the same number of tabs

        for y in range(len(rows)):
            cols = rows[y].split('\t')
            for x in range(x_max):
                tile_name = cols[x].replace('\n', '')
                if tile_name == '':
                    pass
                else:
                    room_number = int(str(area_count) + str(room_count))
                    room_exists = db.session.query(Room).filter_by(room_number=room_number).first()
                    if not room_exists:
                        room = Room(room=tiles.create_tile(area_name=area_name.replace(" ", ""), 
                                                        room_name=tile_name, 
                                                        room_number=room_number, 
                                                        x=x, 
                                                        y=y
                                                        ), 
                                    room_number=room_number,
                                    x=x,
                                    y=y,
                                    area_name=area_name
                                    )
                        room.room.fill_room()
                        if room.room.is_shop:
                            room.room.fill_shop()
                        print("Created {} room with room number {} in area {}".format(tile_name, room_number, area_name))
                        db.session.add(room)
                        area.rooms.append(room)
                room_count += 1
    db.session.commit()
    return

def initiate_enemies():
    rooms = []
    areas = db.session.query(Area).all()
    for area in areas:
        if len(area.area._area_enemies) > 0:
            for room in area.rooms:
                rooms.append(room.room)
            spawn_room = random.choice(rooms)
            area.area.spawn_enemies(room=spawn_room)


def tile_exists(x, y, area):
    room = db.session.query(Room).filter_by(x=x, y=y, area_name=area.replace(" ", "")).first()
    if room:
        return room.room
    else:
        return None
    




