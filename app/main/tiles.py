

"""

TODO: In Fill Room, replace npc search with simpler Sub-Class search

"""

import textwrap as textwrap
import logging as logging
import eventlet

from app.main import config, items, world, mixins, objects, shops, npcs


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
        self._room_data = self._area_data['rooms'][room_name]

        self.x = x
        self.y = y
        self.room_name = self._room_data['name']
        self.area = self._room_data['area']
        self._room_number = room_number
        self.description = self._room_data['description']
        self._is_shop = self._room_data['shop']
        self._shop_items = self._room_data['shop_items']
        self.characters = []
        self.objects = []
        self.items = []
        self.npcs = []
        self.enemies = []
        self.spawn = self._room_data['spawn']
        self.hidden = []
        self.room_filled = False
        self.shop_filled = False

        self.room_result = {
            "action_success": True,
            "action_error": None,
            "room_change": {
                "room_change_flag":  False,
                "leave_room_text": None,
                "old_room":  None,
                "new_room":  None,
                "enter_room_text":  None
            },
            "display_room":  {
                "display_room_flag":  False,
                "display_room_text":  None,
            },
            "character_output":  {
                "character_output_flag":  False,
                "character_output_text":  None
            },
            "room_output":  {
                "room_output_flag":  False,
                "room_output_text":  None
            },
            "area_output":  {
                "area_output_flag":  False,
                "area_output_text":  None
            },
            "spawn_generator":  {
                "spawn_generator_flag":  False,
                "spawn_generator_thread":  None
            },
            "status_output": {
                "status_output_flag": False,
                "status_output_text": None
            }
        }
        self.room_result_default = self.room_result.copy()

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
        if area_name.replace(" ", "") not in cls.areas:
            return
        return cls.areas[area_name.replace(" ", "")](area_name=area_name, room_name=room_name, room_number=room_number, **kwargs)

    def update_room(self, character, old_room_number):
        self.room_result['room_change']['room_change_flag'] = True
        self.room_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.room_result['room_change']['old_room'] = old_room_number
        self.room_result['room_change']['new_room'] = character.room.room_number
        self.room_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.room_result['display_room_flag'] = True
        return

    def update_character_output(self, character_output_text):
        self.room_result['character_output']['character_output_flag'] = True
        self.room_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.room_result['display_room']['display_room_flag'] = True
        self.room_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.room_result['room_output']['room_output_flag'] = True
        self.room_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.room_result['area_output']['area_output_flag'] = True
        self.room_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.room_result['status_output']['status_output_flag'] = True
        self.room_result['status_output']['status_output_text'] = status_text
        return

    def reset_result(self):
        self.room_result = self.room_result_default.copy()
    
    def modify_player(self):
        raise NotImplementedError()

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
        else:
            for move in moves:
                obvious.append(move)
            obvious = ', '.join(obvious)
        return f"Obvious exits:  {obvious}"

    def all_objects(self, room_file, character_file):
        all_objects = []
        if len(self.items) + len(self.npcs) + len(self.objects) + len(room_file.enemies) == 0:
            all_objects_output = None
        else:
            for char in self.npcs:
                all_objects.append(char.name)
            for item in self.items:
                all_objects.append(item.name)
            for object in self.objects:
                all_objects.append(object.name)
            for enemy_file in room_file.enemies:
                if enemy_file.enemy.position != 'standing':
                    all_objects.append(f"<b>{enemy_file.enemy.name}</b> who is {enemy_file.enemy.position}")
                else:
                    all_objects.append(enemy_file.enemy.name)
            if len(all_objects) > 1:
                all_objects_output = ', '.join(all_objects[:-1])
                all_objects_output = f"You see {all_objects_output}, and {all_objects[-1]}."
            else:
                all_objects_output = f"You see {all_objects[0]}."

        character_names = []
        for character_file_list in room_file.characters:
            if character_file_list.first_name == character_file.first_name:
                pass
            elif character_file_list.char.health < 0:
                character_names.append(f"the body of {character_file_list.first_name} who is lying down")
            elif character_file_list.char.position != "standing":
                character_names.append(f"{character_file_list.first_name} who is {character_file_list.char.position}")
            else:
                character_names.append(character_file_list.first_name)
        if len(character_names) > 1:
            all_characters_output = ', '.join(character_names[:-1])
            all_characters_output = f"You also see {all_characters_output}, and {character_names[-1]}."
        elif len(character_names) == 1:
            all_characters_output = f"You also see {character_names[0]}."
        else:
            all_characters_output = None

        if all_objects_output and all_characters_output:
            all_object_and_character_output = f"""\
{all_objects_output}
{all_characters_output}\
                """
        elif all_characters_output:
            all_object_and_character_output = f"""\
{all_characters_output}\
                """
        elif all_objects_output:
            all_object_and_character_output = f"""\
{all_objects_output}\
                """
        else:
            all_object_and_character_output = ""
        return all_object_and_character_output
        
    def all_object_handles(self):
        all_object_handles = []
        if len(self.items) + len(self.npcs) + len(self.objects) + len(self.enemies) == 0:
            return ""
        for char in self.npcs:
            all_object_handles.append(char.name)
        for item in self.items:
            all_object_handles.append(item.name)
        for object in self.objects:
            all_object_handles.append(object.name)
        return all_object_handles

    def fill_room(self):
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
                npcs.create_npc(npc_category=npc, npc_name=npc, room=self)
                try:
                    self.npcs.append(npcs.create_npc(npc_category=npc, npc_name=npc, room=self))
                except:
                    print("WARNING:  Could not create npc " + npc + " in room " + self.room_name + " in " + self.area)
            for door in self._room_data['hidden']['doors']:
                try:
                    self.hidden.append(objects.Door(object_name=door, room=self))
                except:
                    print("WARNING:  Could not create hidden door " + door + " in room " + self.room_name + " in " + self.area)
            for npc in self._room_data['hidden']['npcs']:
                try:
                    self.hidden.append(npcs.create_npc(npc_category=npc, npc_name=npc, room=self))
                except:
                    print("WARNING:  Could not create hidden npc " + npc + " in room " + self.room_name + " in " + self.area)
            for category in self._room_data['hidden']['items']:
                for item in self._room_data['hidden']['items'][category]:
                    try:
                        self.hidden.append(items.create_item(item_category=category, item_name=item))
                    except:
                        print("WARNING:  Could not create hidden item " + item.name + " in room " + self.room_name + " in " + self.area)
            self.room_filled = True
        return
            
    def fill_shop(self):
        if not self.shop_filled:
            self.shop = shops.Shop(shop_name=self.area, shop_items=self.shop_items)
            self.shop.write_shop_menu() 
            self.shop_filled = True
        return
    
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

    def add_character(self, character):
        self.characters.append(character)
        return

    def remove_character(self, character):
        self.characters.remove(next((x for x in self.characters if (x.first_name == character.first_name) and (x.last_name == character.last_name)), None))
        return

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

    def get_characters(self, character_file, room_file):
        character_names = []
        for character_file_list in room_file.characters:
            if character_file_list.first_name == character_file.first_name:
                pass
            elif character_file_list.char.health < 0:
                character_names.append(f"the body of {character_file_list.first_name} who is lying down")
            elif character_file_list.char.position != "standing":
                character_names.append(f"{character_file_list.first_name} who is {character_file_list.char.position}")
            else:
                character_names.append(character_file_list.first_name)
        if len(character_names) > 1:
            all_characters_output = ', '.join(character_names[:-1])
            all_characters_output = all_characters_output + ', and ' + character_names[-1]
            return all_characters_output
        if len(character_names) == 1:
            all_characters_output = character_names[0]
            return all_characters_output
        else:
            all_characters_output = "None"
            return all_characters_output

    def intro_text(self, character_file, room_file):
        self.reset_result()
        intro_text = f"""\
<b>{self.area}, {self.room_name}</b>
{self.description}
{self.obvious_exits()}
{self.all_objects(room_file=room_file, character_file=character_file)}\
""",
        self.update_display_room(display_room_text=intro_text)
        return self.room_result

    def spawn_generator(self, character):
        return NotImplementedError()

    def search_room(self):
        pass


@MapTile.register_area('Town')
class Town(MapTile):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x, y)


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


@MapTile.register_area('Field')
class Field(Town):
    def __init__(self, area_name, room_name, room_number, x, y):
        MapTile.__init__(self, area_name, room_name, room_number, x=x, y=y)


