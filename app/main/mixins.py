
import abc as abc
import json as json
import pathlib as pathlib

from app.main import config


# importing all objects
objects_path = pathlib.Path.cwd() / "app" / 'Resources' / 'objects.json'
with objects_path.open(mode='r') as file:
    objects = json.load(file)
    
all_objects = {}
for category in objects:
    for object in objects[category]:
        all_objects[object] = objects[category][object]

# importing all items
items_path = pathlib.Path.cwd() / "app" / 'Resources' / 'items.json'
with items_path.open(mode='r') as file:
    items = json.load(file)

all_items = {}
for category in items:
    for item in items[category]:
        all_items[item] = items[category][item]

# importing all npcs
npcs_path = pathlib.Path.cwd() / "app" / 'Resources' / 'npcs.json'
with npcs_path.open(mode='r') as file:
    npcs = json.load(file)

# importing all enemies
enemies_path = pathlib.Path.cwd() / "app" / 'Resources' / 'enemies.json'
with enemies_path.open(mode='r') as file:
    enemies = json.load(file)


class DataFileMixin(metaclass=abc.ABCMeta):

    @staticmethod
    def _get_by_name(name: str, obj_type: str, file: str, file_format=config.DATA_FORMAT) -> dict:
        with open(file) as fl:
            if file_format == "json":
                data = json.load(fl, parse_int=int, parse_float=float)
            else:
                raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
        return data[str(name)]

    def get_player_by_name(self, name: str, file=config.PLAYER_FILE) -> dict:
        return self._get_by_name(name, 'players', file)

    def get_area_by_name(self, name: str, file=config.ROOM_FILE) -> dict:
        return self._get_by_name(name, 'tiles', file)

    def get_item_by_name(self, name: str, file=config.ITEM_FILE) -> dict:
        return self._get_by_name(name, 'items', file)

    def get_enemy_by_name(self, name: str, file=config.ENEMY_FILE) -> dict:
        return self._get_by_name(name, 'enemies', file)

    def get_npc_by_name(self, name: str, file=config.NPC_FILE) -> dict:
        return self._get_by_name(name, 'npcs', file)

    def get_object_by_name(self, name: str, file=config.OBJECT_FILE) -> dict:
        return self._get_by_name(name, 'objects', file)

    def get_quest_by_name(self, name: str, file=config.QUEST_FILE) -> dict:
        return self._get_by_name(name, 'quests', file)
    
    def get_skill_category_by_name(self, name: str, file=config.SKILLS_FILE) -> dict:
        return self._get_by_name(name, 'skills', file)
    
    def get_stat_by_name(self, name: str, file=config.STATS_FILE) -> dict:
        return self._get_by_name(name, 'stats', file)


class ReprMixin(metaclass=abc.ABCMeta):

    def __repr__(self):
        attributes = [f"{key}={value}" if type(value) != str
                      else f'{key}="{value}"'
                      for key,value in vars(self).items()]
        v_string = ", ".join(attributes)
        class_name = self.__class__.__name__
        return f"{class_name}({v_string})"


