
import random as random

from app.main import world, mixins, items, npcs


all_items_categories = mixins.items


def create_object(object_category, object_name, **kwargs):
    return Object.new_object(object_category, object_name, **kwargs)


class Object(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, object_data, **kwargs):

        self.object_data = object_data

        self.name = self.object_data['name']
        self.description = self.object_data['description']
        self.handle = self.object_data['handle']
        self.adjectives = self.object_data['adjectives']
        self.container = self.object_data['container']

    def contents(self):
        # Currently there are no objects that are containers.
        if self.container == False:
            return "{} cannot hold anything".format(self.name)

    def go_object(self, **kwargs):
        events.game_event("I'm not sure how you intend on doing that.")

    def view_description(self):
        events.game_event("{}".format(self.description))

    def skin(self, room):
        events.game_event("You cannot skin {}.".format(self.name))

    def search(self, character):
        NotImplementedError()
        
    object_categories = {}
        
    @classmethod
    def register_subclass(cls, object_category):
        """Catologues object categories in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.object_categories[object_category] = subclass
            return subclass
        return decorator
    
    @classmethod
    def new_object(cls, object_category, object_name, **kwargs):
        """Method used to initiate an object"""
        if object_category not in cls.object_categories:
            events.game_event("I am sorry, I did not understand.")
            return
        return cls.object_categories[object_category](object_name, **kwargs)


@Object.register_subclass('doors')
class Door(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Doors')
        object_data = category_data[object_name]
        super().__init__(object_data=object_data, **kwargs)

        self.room = room

    def go_object(self, character):
        if character.room.room_name == self.object_data['location_1']['name']:
            new_location = self.object_data['location_2']
        elif character.room.room_name == self.object_data['location_2']['name']:
            new_location = self.object_data['location_1']
        character.room = world.tile_exists(x=new_location['x'], y=new_location['y'], area=new_location['area'].replace(" ",""))
        character.location_x = new_location['x']
        character.location_y = new_location['y']
        character.area = new_location['area']
        character.room.fill_room(character=character)
        print("does code go here?")
        character.room.intro_text()
        character.print_status()
        character.room.run(character=character)

    def search(self, character):
        pass
    
    
@Object.register_subclass('furniture')
class Furniture(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Furniture')
        object_data = category_data[object_name]
        super().__init__(object_data=object_data, **kwargs)

        self.room = room

    def search(self, character):
        pass
    
@Object.register_subclass('miscellaneous')
class Miscellaneous(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Miscellaneous')
        object_data = category_data[object_name]
        super().__init__(object_data=object_data, **kwargs)

        self.room = room

    def search(self, character):
        pass


@Object.register_subclass('corpse')
class Corpse(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Corpse')
        object_data = category_data[object_name]
        super().__init__(object_data=object_data, **kwargs)

        self.room = room

        self.level = self.object_data['level']

        self.skin = self.object_data['skin']
        self.loot_drop_rate = self.object_data['loot']['drop_rate']
        self.loot_categories = self.object_data['loot']['items']
        self.loot_money = self.object_data['loot']['money']

    def skin_corpse(self):
        if self.skin == None:
            events.game_event("You cannot skin {}".format(self.name))
        else:
            events.game_event("You skin {} to yield {}.".format(self.name, all_items_categories['skin'][self.skin]['name']))
            self.room.add_item(items.create_item(item_category='skin', item_name=self.skin))
        return

    def search(self, character):
        possible_items = {}
        area = "Wilds"
        for category in self.loot_categories:
            for item in all_items_categories[category]:
                if all_items_categories[category][item]['level'] <= self.level and all_items_categories[category][item]['area'] == area:
                    possible_items[item] = all_items_categories[category][item]
        if len(possible_items) == 0:
            events.game_event("You did not find any items on {}.".format(self.name))
        else:
            found_item = random.choice(list(possible_items))
            found_item = getattr(__import__('items'), possible_items[found_item]['category'])(item_name=found_item)
            events.game_event("You found {}!".format(found_item.name))
            self.room.add_item(found_item)
        if self.loot_money == 0:
            events.game_event("You did not find any gulden on {}.".format(self.name))
        else:
            character.add_money(self.loot_money)
            events.game_event("You found {} gulden on {}!".format(self.loot_money, self.name))
        self.room.remove_object(self)
        self.room = None
        return

