

import pathlib as pathlib
import imp as imp
import random as random

from flask import current_app

import eventlet

from app import db
from app.main import enemies, mixins
from app.main.models import WorldArea, EnemySpawn


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
        area = db.session.query(WorldArea).filter_by(area_name=self.area_name).first()
        rooms = area.rooms
        print(rooms)

    def spawn_enemies(self, app):
        with app.app_context():
        #     while True:
                area_file = db.session.query(WorldArea).filter_by(area_name=self.area_name).first()
                spawn_room_file = random.choice(area_file.rooms)
                new_enemy = EnemySpawn(enemy=enemies.Enemy(enemy_name=self._area_enemies[0],
                                                target=None,
                                                location_x=spawn_room_file.x,
                                                location_y=spawn_room_file.y,
                                                area=self.area_name),
                                        stop=False)
                spawn_room_file.enemies.append(new_enemy)
                db.session.add(new_enemy)
                db.session.flush()
                new_enemy.enemy.enemy_id = new_enemy.id
                eventlet.spawn(new_enemy.enemy.run, app, new_enemy.id)
                print(f"enemy {new_enemy.id} created.")
                db.session.commit()
                # eventlet.sleep(10)