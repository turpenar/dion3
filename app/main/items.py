
"""


TODO:  Introduce stackable items
"""

from app.main import mixins


def loot():
    pass

def create_item(item_category, item_name, **kwargs):
    return Item.new_item(item_category, item_name, **kwargs)


class Item(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, item_data, **kwargs):

        item_data = item_data

        self.name = item_data['name']
        self.description = item_data['description']
        self.value = item_data['value']
        self.handle = item_data['handle']
        self.adjectives = item_data['adjectives']
        self.material = item_data['material']
        self.container = item_data['container']
        self.wearable = item_data['wearable']
        self.stackable = item_data['stackable']
        self.capacity = item_data['capacity']
        self.category = item_data['category']
        self.sub_category = item_data['sub_category']
        self.visibility = item_data['visibility']
        self.enchant = item_data['enchant']
        self.rarity = item_data['rarity']
        self.level = item_data['level']
        self.loot = item_data['loot']
        self.area = item_data['area']
        self.items = []

        self.item_result = {
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
            "status_output":  None
        }
        self.item_result_default = self.item_result.copy()

    def update_room(self, character, old_room_number):
        self.item_result['room_change']['room_change_flag'] = True
        self.item_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.item_result['room_change']['old_room'] = old_room_number
        self.item_result['room_change']['new_room'] = character.room.room_number
        self.item_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.item_result['display_room_flag'] = True
        return
    
    def update_character_output(self, character_output_text):
        self.item_result['character_output']['character_output_flag'] = True
        self.item_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.item_result['display_room']['display_room_flag'] = True
        self.item_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.item_result['room_output']['room_output_flag'] = True
        self.item_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.item_result['area_output']['area_output_flag'] = True
        self.item_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.item_result['status_output'] = status_text
        return

    def reset_result(self):
        self.item_result = self.item_result_default.copy()
        return

    def contents(self):
        self.reset_result()
        if self.container == False:
            self.update_character_output(character_output_text="A {} cannot hold anything".format(self.handle[0]))
            return self.item_result
        all_items = []
        if len(self.items) == 0:
            self.update_character_output(character_output_text="{} is empty".format(self.name))
            return self.item_result
        for item in self.items:
            all_items.append(item.name)
        if len(all_items) > 1:
            all_items_output = ', '.join(all_items[:-1])
            all_items_output = all_items_output + ', and ' + all_items[-1]
        else:
            all_items_output = all_items[0]
        self.update_character_output(character_output_text="Inside {} you see {}".format(self.name, all_items_output))
        return self.item_result

    def view_description(self):
        self.reset_result()
        self.update_character_output("You see " + self.description)
        return self.item_result

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    item_categories = {}
    
    @classmethod
    def register_subclass(cls, item_category):
        """Catologues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.item_categories[item_category] = subclass
            return subclass
        return decorator
    
    @classmethod
    def new_item(cls, item_category, item_name, **kwargs):
        """Method used to initiate an action"""
        if item_category not in cls.item_categories:
            events.game_event("I am sorry, I did not understand.")
            return
        return cls.item_categories[item_category](item_name, **kwargs)


@Item.register_subclass('clothing')
class Clothing(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('clothing')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)


@Item.register_subclass('weapon')
class Weapon(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('weapons')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)
        
        self.classification = item_data['classification']


@Item.register_subclass('money')
class Money(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('money')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)


@Item.register_subclass('armor')
class Armor(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('armor')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)

        self.classification = item_data['classification']

@Item.register_subclass('ring')
class Ring(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('rings')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)


@Item.register_subclass('neck')
class Neck(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('neck')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)


@Item.register_subclass('skin')
class Skin(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('skin')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)


@Item.register_subclass('miscellaneous')
class Miscellaneous(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('miscellaneous')
        item_data = category_data[item_name]
        Item.__init__(self, item_data=item_data, **kwargs)




