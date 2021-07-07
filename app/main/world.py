
import pathlib as pathlib
import imp as imp
import random as random
import eventlet

from app import db
from app.main import areas, tiles
from app.main.models import WorldArea, Room, EnemySpawn

path_maps = pathlib.Path.cwd() / "app" / "resources" / "maps"
map_list = path_maps.glob('*.txt')
module = imp.load_source('tiles', 'app/main/tiles.py')
starting_position = (0,0)
starting_area = 'Field'


def load_world():
    area_count = 10
    room_count = 100
    """Parses a file that describes the world space into the database."""
    for path in map_list:
        area_name = path.stem.split('.')[0]
        area_exists = db.session.query(WorldArea).filter_by(area_name=area_name).first()
        if not area_exists:
            area = WorldArea(area=areas.Area(area_name=area_name, 
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
                        room = Room(room=tiles.create_tile(area_name=area_name, 
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

def initiate_enemies(app):
    areas = db.session.query(WorldArea).all()
    for area_file in areas:
        if len(area_file.area._area_enemies) > 0:
            eventlet.spawn(area_file.area.spawn_enemies, app)
    return

def clear_enemies(app):
    all_enemies = db.session.query(EnemySpawn).all()
    print(all_enemies)
    for enemy_file in all_enemies:
        print(enemy_file)
        print(enemy_file.id)
        enemy_file.stop = True
        db.session.merge(enemy_file)
        print(f"after stop flag changed for enemy {enemy_file.id}")
        print(f"enemy {enemy_file.id} stop flag = {enemy_file.stop}")
    db.session.commit()
    return
    

def tile_exists(x, y, area):
    room = db.session.query(Room).filter_by(x=x, y=y, area_name=area).first()
    if room:
        return room
    else:
        return None
    




