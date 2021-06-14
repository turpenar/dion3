

import pathlib as pathlib
import imp as imp
import random as random

from app import db
from app.main import tiles, enemies, mixins
from app.main.models import Room


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
        self._map_tiles = {}
        self._room_count = 100

        with open(area_path.resolve().as_posix(), 'r') as f:
            rows = f.readlines()
        x_max = len(rows[0].split('\t')) #assumes all rows contain the same number of tabs

        for y in range(len(rows)):
            cols = rows[y].split('\t')
            for x in range(x_max):
                tile_name = cols[x].replace('\n', '')
                if tile_name == 'field_glade':
                    self.starting_position = (x, y)
                if tile_name == '':
                    self._map_tiles[(x, y)] = None
                else:
                    room_number = int(str(self._area_number) + str(self._room_count))
                    self._map_tiles[(x, y)] = tiles.create_tile(area_name=self.area_name.replace(" ", ""), room_name=tile_name, room_number=room_number, x=x, y=y)
                    room = Room(room_number=room_number)
                    db.session.add(room)
                    db.session.commit()
                self._room_count += 1

    def tile_exists(self, x, y):
        return self._map_tiles.get((x, y))

    def area_rooms(self):
        return self._map_tiles
    
    def area_enemies(self):
        all_enemies = []
        all_rooms = self.area_rooms()
        for room in all_rooms:
            if self.tile_exists(x=room[0], y=room[1]):
                all_enemies.extend(all_rooms[room].enemies)
        return all_enemies

    def spawn_enemies(self):
        if len(self._area_enemies) >= 1:
            all_area_rooms = self.area_rooms()
            area_rooms = {keys: value for keys, value in all_area_rooms.items() if value is not None}
            spawn_room_coords = random.choice(list(area_rooms))
            spawn_room = self.tile_exists(x=spawn_room_coords[0], y=spawn_room_coords[1])
            spawn_room.enemies.append(enemies.Enemy(enemy_name=self._area_enemies[0],
                                        target=None,
                                        room=spawn_room,
                                        location_x=spawn_room_coords[0],
                                        location_y=spawn_room_coords[1],
                                        area=self.area_name))
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