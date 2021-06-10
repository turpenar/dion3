

"""

TODO: In Fill Room, replace npc search with simpler Sub-Class search
TODO: Eliminate need to pass character to the npcs.

"""

import time as time
import random as random
import textwrap as textwrap
import logging as logging
import eventlet

from app.main import config, items, enemies, actions, world, mixins, objects, shops, npcs


wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)

all_npcs = mixins.npcs

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def create_tile(area_name=None, room_name=None, room_number=None, x=None, y=None):
    return MapTile.tile(area_name=area_name, room_name=room_name, room_number=room_number, x=x, y=y)

    

class MapTile(mixins.DataFileMixin):
    def __init__(self, area_name: str, room_name: str, room_number: int, x, y):

        self._area_data = self.get_area_by_name(area_name)
        self._room_data = self._area_data[room_name]

        self.x = x
        self.y = y
        self.character = None
        self.room_name = self._room_data['name']
        self.area = self._room_data['area']
        self._room_number = room_number
        self.description = self._room_data['description']
        self._is_shop = self._room_data['shop']
        self._shop_items = self._room_data['shop_items']
        self.objects = []
        self.items = []
        self.npcs = []
        self.enemies = []
        self.spawn = self._room_data['spawn']
        self.hidden = []
        self.room_filled = False
        self.shop_filled = False

    areas = {}

    @classmethod
    def register_area(cls, area):
        """Catalogues tiles in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.areas[area] = subclass
            return subclass
        return decorator

    @classmethod
    def tile(cls, area_name, room_name, room_number, **kwargs):
        """Method used to initiate an action"""
        if area_name not in cls.areas:
            return
        return cls.areas[area_name](area_name=area_name, room_name=room_name, room_number=room_number, **kwargs)

    def modify_player(self):
        raise NotImplementedError()

    def adjacent_moves_enemy(self, area):
        moves = []
        if world.tile_exists(x=self.x, y=self.y - 1, area=self.area):
            moves.append(actions.MoveNorthEnemy())
        if world.tile_exists(x=self.x, y=self.y + 1, area=self.area):
            moves.append(actions.MoveSouthEnemy())
        if world.tile_exists(x=self.x + 1, y=self.y, area=self.area):
            moves.append(actions.MoveEastEnemy())
        if world.tile_exists(x=self.x - 1, y=self.y, area=self.area):
            moves.append(actions.MoveWestEnemy())
        return moves

    def obvious_exits(self):
        """Returns all of the available actions in this room."""
        moves = []
        if world.tile_exists(x=self.x, y=self.y - 1, area=self.area):
            moves.append("north")
        if world.tile_exists(x=self.x, y=self.y + 1, area=self.area):
            moves.append("south")
        if world.tile_exists(x=self.x + 1, y=self.y, area=self.area):
            moves.append("east")
        if world.tile_exists(x=self.x - 1, y=self.y, area=self.area):
            moves.append("west")
        obvious = []
        if len(moves) == 0:
            obvious = 'None'
            return "Obvious exits:  {}".format(obvious)
        for move in moves:
            obvious.append(move)
        obvious = ', '.join(obvious)
        return "Obvious exits:  {}".format(obvious)

    def all_objects(self):
        all_objects = []
        if len(self.items) + len(self.npcs) + len(self.objects) + len(self.enemies) == 0:
            return ""
        for char in self.npcs:
            all_objects.append(char.name)
        for char in self.enemies:
            all_objects.append(char.name)
        for item in self.items:
            all_objects.append(item.name)
        for object in self.objects:
            all_objects.append(object.name)
        if len(all_objects) > 1:
            all_objects_output = ', '.join(all_objects[:-1])
            all_objects_output = all_objects_output + ', and ' + all_objects[-1]
        else:
            all_objects_output = all_objects[0]
        return "You also see {}.".format(all_objects_output)
        
    def all_object_handles(self):
        all_object_handles = []
        if len(self.items) + len(self.npcs) + len(self.objects) + len(self.enemies) == 0:
            return ""
        for char in self.npcs:
            all_object_handles.append(char.name)
        for char in self.enemies:
            all_object_handles.append(char.name)
        for item in self.items:
            all_object_handles.append(item.name)
        for object in self.objects:
            all_object_handles.append(object.name)
        return all_object_handles

    def fill_room(self, character):
        if not self.room_filled:
            for category in self._room_data['objects']:
                for object in self._room_data['objects'][category]:
                    try:
                        self.objects.append(objects.create_object(object_category=category, object_name=object, room=self))
                    except:
                        print("WARNING:  Could not create object " + object.name + " in room " + self.room_name + " in " + self.area)
            for category in self._room_data['items']:
                for item in self._room_data['items'][category]:
                    try:
                        self.items.append(items.create_item(item_category=category, item_name=item))
                    except:
                        print("WARNING:  Could not create item " + item.name + " in room " + self.room_name + " in " + self.area)
            for npc in self._room_data['npcs']:
                try:
                    self.npcs.append(npcs.create_npc(npc_category=npc, npc_name=npc, character=character, room=self))
                except:
                    print("WARNING:  Could not create npc " + npc + " in room " + self.room_name + " in " + self.area)
            for door in self._room_data['hidden']['doors']:
                try:
                    self.hidden.append(objects.Door(object_name=door, room=self))
                except:
                    print("WARNING:  Could not create hidden door " + door.name + " in room " + self.room_name + " in " + self.area)
            for npc in self._room_data['hidden']['npcs']:
                try:
                    self.hidden.append(npcs.create_npc(npc_category=npc, npc_name=npc, character=character, room=self))
                except:
                    print("WARNING:  Could not create hidden npc " + npc.name + " in room " + self.room_name + " in " + self.area)
            for category in self._room_data['hidden']['items']:
                for item in self._room_data['hidden']['items'][category]:
                    try:
                        self.hidden.append(items.create_item(item_category=category, item_name=item))
                    except:
                        print("WARNING:  Could not create hidden item " + item.name + " in room " + self.room_name + " in " + self.area)
            self.room_filled = True
            
    def fill_shop(self):
        if not self.shop_filled:
            self.shop = shops.Shop(shop_name=self.area, shop_items=self.shop_items)
            self.shop.write_shop_menu() 
            self.shop_filled = True
    
    @property
    def room_number(self):
        return self._room_number
    @room_number.setter
    def room_number(self, room_number):
        self._room_number = room_number
            
    @property     
    def is_shop(self):
        return self._is_shop
        
    @property
    def shop(self):
        return self._shop
    @shop.setter
    def shop(self, shop):
        self._shop = shop
        
    @property
    def shop_items(self):
        return self._shop_items

    def add_object(self, object):
        self.objects.append(object)
        return

    def add_hidden_object(self, object):
        self.hidden.append(object)
        return

    def remove_object(self, object):
        self.objects.remove(object)
        return

    def remove_hidden_object(self, object):
        self.hidden.remove(object)
        return

    def add_item(self, item):
        self.items.append(item)
        return

    def remove_item(self, item):
        self.items.remove(item)
        return

    def add_hidden_item(self, item):
        self.hidden.append(item)
        return

    def remove_hidden_item(self, item):
        self.hidden.remove(item)
        return

    def add_npc(self, npc):
        self.npcs.append(npc)
        return

    def add_hidden_npc(self, npc):
        self.hidden.append(npc)
        return

    def remove_npc(self, npc):
        self.npcs.remove(npc)
        return

    def remove_hidden_npc(self, npc):
        self.hidden.remove(npc)
        return

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        return

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        return


    def intro_text(self):
        intro_text = """\
[{}, {}] <br>
{} <br>
{} <br>
{}\
        """.format(self.area,
                   self.room_name,
                   wrapper.fill(text=self.description),
                   self.obvious_exits(),
                   self.all_objects())
        return intro_text

    def spawn_generator(self, character):
        return NotImplementedError()

    def search_room(self):
        pass

    def run(self, character):
        return NotImplementedError()


@MapTile.register_area('Town')
class Town(MapTile):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x, y)

    def spawn_generator(self, character):
        pass

    def run(self, character):
        pass


@MapTile.register_area('Dochas')
class Dochas(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


@MapTile.register_area('DochasGrounds')
class DochasGrounds(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


@MapTile.register_area('DochasLeatherworks')
class DochasLeatherworks(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


@MapTile.register_area('DochasSmallHouse')
class DochasSmallHouse(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)
        

@MapTile.register_area('DochasWeaponsmith')
class DochasWeaponsmith(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


@MapTile.register_area('EdgewoodForest')
class EdgewoodForest(MapTile):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)

    def spawn_generator(self, character):
        area_rooms = world.area_rooms(self.area)
        while character.area == self.area.replace(" ", ""):
            time.sleep(5)
            area_enemies = world.area_enemies(self.area)
            if len(area_enemies) < 1:
                area_rooms = {keys: value for keys, value in area_rooms.items() if value is not None}
                spawn_room_coords = random.choice(list(area_rooms))
                if random.randint(0,100) > 50:
                    spawn_room = world.tile_exists(x=spawn_room_coords[0], y=spawn_room_coords[1], area=self.area)
                    spawn_room.enemies.append(
                        enemies.Enemy(enemy_name=self._room_data['spawn'][0],
                                      target=character,
                                      room=spawn_room,
                                      location_x=spawn_room_coords[0],
                                      location_y=spawn_room_coords[1],
                                      area=self.area))
                    spawn_room.enemies[-1].start()


    def run(self, character):
        spawn_thread = eventlet.spawn(self.spawn_generator, args=(character,))


@MapTile.register_area('Field')
class Field(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


