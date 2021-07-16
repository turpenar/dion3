
import random as random

from app import db
from app.main import mixins, items
from app.main.models import Room


all_items_categories = mixins.items


def create_object(object_category, object_name, **kwargs):
    return Object.new_object(object_category, object_name, **kwargs)


class Object(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, object_data, **kwargs):

        self.object_result =  {"action_success": True,
                                "action_error": None,
                                "room_change": {
                                    "room_change_flag":  False,
                                    "leave_room_text": None,
                                    "old_room":  None,
                                    "new_room":  None,
                                    "enter_room_text":  None
                                },
                                "area_change": {
                                    "area_change_flag":  False,
                                    "old_area":  None,
                                    "new_area":  None
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
                                    "spawn_generator_flag":  False
                                },
                                "status_output":  None
        }
        self.object_result_default = self.object_result.copy()

        self.object_data = object_data

        self.name = self.object_data['name']
        self.description = self.object_data['description']
        self.handle = self.object_data['handle']
        self.adjectives = self.object_data['adjectives']
        self.container = self.object_data['container']
        
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
            cls.object_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.object_result
        return cls.object_categories[object_category](object_name, **kwargs)

    def update_room(self, character, new_room_number, old_room_number):
        self.object_result['room_change']['room_change_flag'] = True
        self.object_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.object_result['room_change']['old_room'] = old_room_number
        self.object_result['room_change']['new_room'] = new_room_number
        self.object_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.object_result['display_room_flag'] = True
        return

    def update_area(self, new_area, old_area):
        self.object_result['area_change']['area_change_flag'] = True
        self.object_result['area_change']['old_area'] = old_area
        self.object_result['area_change']['new_area'] = new_area
        return

    def update_character_output(self, character_output_text):
        self.object_result['character_output']['character_output_flag'] = True
        self.object_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.object_result['display_room']['display_room_flag'] = True
        self.object_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.object_result['room_output']['room_output_flag'] = True
        self.object_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.object_result['area_output']['area_output_flag'] = True
        self.object_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.object_result['status_output'] = status_text
        return

    def reset_result(self):
        self.object_result = self.object_result_default.copy()
        return

    def contents(self):
        # Currently there are no objects that are containers.
        self.reset_result()
        if self.container == False:
            self.update_character_output(character_output_text="{} cannot hold anything".format(self.name))
            return self.object_result

    def go_object(self, **kwargs):
        self.reset_result()
        self.update_character_output(character_output_text="I'm not sure how you intend on doing that.")
        return self.object_result

    def view_description(self):
        self.reset_result()
        self.update_character_output(character_output_text="{}".format(self.description))
        return self.object_result

    def skin(self, room):
        self.reset_result()
        self.update_character_output(character_output_text="You cannot skin {}.".format(self.name))
        return self.object_result

    def search(self, character):
        self.reset_result()
        NotImplementedError()


@Object.register_subclass('doors')
class Door(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Doors')
        object_data = category_data[object_name]
        Object.__init__(self, object_data=object_data, **kwargs)

    def go_object(self, character_file, room_file):
        self.reset_result()
        character = character_file.char
        if room_file.room.room_name == self.object_data['location_1']['name']:
            new_location = self.object_data['location_2']
        elif room_file.room.room_name == self.object_data['location_2']['name']:
            new_location = self.object_data['location_1']
        if room_file.room.shop_filled == True:
            if character.in_shop == True:
                character.in_shop = False
                room_file.room.shop.exit_shop() 
        room_file.characters.remove(character_file)
        character.change_room(x=new_location['x'], y=new_location['y'], area=new_location['area'])
        new_room = character.get_room()
        new_room.characters.append(character_file)
        if new_room:
            self.object_result.update(new_room.room.intro_text(character_file=character_file, room_file=new_room))
            self.update_room(character=character, new_room_number=new_room.room_number, old_room_number=room_file.room.room_number)
            self.update_area(new_area=new_room.area, old_area=room_file.room.area)
            self.update_status(status_text=character.get_status())
            return self.object_result
        else:
            print('WARNING: Did not create room at x:  {}, y:  {}, in area:  {} for object {}'.format(new_location['x'], new_location['y'], new_location['area'], self.name))
            return

    def search(self, character):
        self.reset_result()
        pass
    
    
@Object.register_subclass('furniture')
class Furniture(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Furniture')
        object_data = category_data[object_name]
        Object.__init__(self, object_data=object_data, **kwargs)

    def search(self, character):
        self.reset_result()
        pass
    
@Object.register_subclass('miscellaneous')
class Miscellaneous(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Miscellaneous')
        object_data = category_data[object_name]
        Object.__init__(self, object_data=object_data, **kwargs)

    def search(self, character):
        self.reset_result()
        pass


@Object.register_subclass('corpse')
class Corpse(Object):
    def __init__(self, object_name, room, **kwargs):
        category_data = self.get_object_by_name('Corpse')
        object_data = category_data[object_name]
        Object.__init__(self, object_data=object_data, **kwargs)

        self.level = self.object_data['level']

        self.skin = self.object_data['skin']
        self.loot_drop_rate = self.object_data['loot']['drop_rate']
        self.loot_categories = self.object_data['loot']['item_categories']
        self.loot_money = self.object_data['loot']['money']

    def skin_corpse(self, character_file, room_file):
        self.reset_result()
        if self.skin == None:
            self.update_character_output(f"You cannot skin {self.name}")
        else:
            # room_file.room.add_item(items.create_item(item_category='skin', item_name=self.skin))
            # self.update_character_output(character_output_text=f"You skin {self.name} to yield {all_items_categories['skin'][self.skin]['name']}.")
            # self.update_room_output(room_output_text=f"{character_file.char.first_name} skinned {self.name}.")
            try:
                self.update_character_output(character_output_text=f"You skin {self.name} to yield {all_items_categories['skin'][self.skin]['name']}.")
                self.update_room_output(room_output_text=f"{character_file.char.first_name} skinned {self.name}.")
                room_file.room.add_item(items.create_item(item_category='skin', item_name=self.skin))
            except:
                print(f"WARNING:  Could not create {self.skin} for {self.name}")
        return self.object_result

    def search(self, character_file, room_file):
        self.reset_result()        
        possible_items = {}
        area = "Wilds"
        for category in self.loot_categories:
            for item in all_items_categories[category]:
                if all_items_categories[category][item]['level'] <= self.level and all_items_categories[category][item]['area'] == area:
                    possible_items[item] = all_items_categories[category][item]
        if len(possible_items) == 0:
            found_item_text = f"You did not find any items on {self.name}."
        else:
            found_item_category, found_item_name = random.choice(list(possible_items))
            found_item = items.create_item(item_category=found_item_category, item_name=found_item_name)
            room_file.room.add_item(found_item)
            found_item_text = f"You found {found_item.name}!"
        if self.loot_money == 0:
            found_loot_text = f"You did not find any gulden on {self.name}."
        else:
            character_file.char.add_money(self.loot_money)
            found_loot_text = f"You found {self.loot_money} gulden on {self.name}!"
        room_file.room.remove_object(self)
        self.update_character_output(character_output_text=f"""
You search {self.name}.
{found_item_text}
{found_loot_text}
{self.name.capitalize()} decays into compost.
        """)
        self.update_room_output(room_output_text=f"{character_file.char.first_name} searched {self.name}.")
        return self.object_result

