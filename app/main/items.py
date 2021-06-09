
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
        super(Item, self).__init__()

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

    def contents(self):
        if self.container == False:
            return "A {} cannot hold anything".format(self.handle[0])
        all_items = []
        if len(self.items) == 0:
            return "{} are empty".format(self.name)
        for item in self.items:
            all_items.append(item.name)
        if len(all_items) > 1:
            all_items_output = ', '.join(all_items[:-1])
            all_items_output = all_items_output + ', and ' + all_items[-1]
        else:
            all_items_output = all_items[0]
        return "Inside {} you see {}".format(self.name, all_items_output)

    def view_description(self):
        return "You see " + self.description

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
        super().__init__(item_data=item_data, **kwargs)


@Item.register_subclass('weapon')
class Weapon(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('weapons')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)
        
        self.classification = item_data['classification']


@Item.register_subclass('money')
class Money(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('money')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)


@Item.register_subclass('armor')
class Armor(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('armor')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)

        self.classification = item_data['classification']

@Item.register_subclass('ring')
class Ring(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('rings')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)


@Item.register_subclass('neck')
class Neck(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('neck')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)


@Item.register_subclass('skin')
class Skin(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('skin')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)


@Item.register_subclass('miscellaneous')
class Miscellaneous(Item):
    def __init__(self, item_name: str, **kwargs):
        category_data = self.get_item_by_name('miscellaneous')
        item_data = category_data[item_name]
        super().__init__(item_data=item_data, **kwargs)




