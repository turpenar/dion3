

import pathlib as pathlib
import imp as imp
import random as random

import eventlet

from app import db
from app.main import tiles, enemies, mixins
from app.main.models import Room, Area


path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')


class Area(mixins.DataFileMixin):
    def __init__(self, area_name, area_path, area_number, **kwargs):

        self._area_data = self.get_area_by_name(area_name)
        self.area_name = self._area_data['name']
        self._area_path = area_path
        self._area_number = area_number
        self._area_enemies = self._area_data['enemies']
        self._map_tiles = []
        self._room_count = 100

    def area_rooms(self):
        area = db.session.query(Area).filter_by(area_name=self.area_name.replace(" ", "")).first()
        rooms = area.rooms
        print(rooms)

    def spawn_enemies(self, room):
        room.enemies.append(enemies.Enemy(enemy_name=self._area_enemies[0],
                                        target=None,
                                        location_x=room.x,
                                        location_y=room.y,
                                        area=self.area_name))
                            
        thread = eventlet.spawn(room.enemies[-1].run)
        return


        # while character.area == self.area.replace(" ", ""):
        #     time.sleep(5)
        #     area_enemies = world.area_enemies(self.area)
        #     if len(area_enemies) < 1:
        #         area_rooms = {keys: value for keys, value in area_rooms.items() if value is not None}
        #         spawn_room_coords = random.choice(list(area_rooms))
        #         if random.randint(0,100) > 50:
        #             spawn_room = self.tile_exists(x=spawn_room_coords[0], y=spawn_room_coords[1], area=self.area)
        #             spawn_room.enemies.append(
        #                 enemies.Enemy(enemy_name=self._room_data['spawn'][0],
        #                                 target=character,
        #                                 room=spawn_room,
        #                                 location_x=spawn_room_coords[0],
        #                                 location_y=spawn_room_coords[1],
        #                                 area=self.area))