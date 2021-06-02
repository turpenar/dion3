


from app.main import mixins, items
    
    
class Shop(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, shop_name: str, shop_items: list, **kwargs):
        
        self._shop_name = shop_name
        self._shop_data = shop_items
        self._shop_items = []
        self._in_shop = False
        self._item_selected = None
        self._shop_menu = False
        
        for category in self._shop_data:
            for item in self._shop_data[category]:
                self._shop_items.append(items.create_item(item_category=category, item_name=item))               
        
    def write_shop_menu(self):
        item_number = 1
        self.shop_menu = []
        self.shop_menu.append(self._shop_name)
        self.shop_menu.append("")
        for item in self._shop_items:
            self.shop_menu.append("{}.  {}".format(item_number, item.name))
            item_number += 1
        self.shop_menu.append("")
        self.shop_menu.append("To order, simply ORDER <#>.")
        self.shop_menu.append("To exit, simply EXIT.")
        return
        
    def enter_shop(self):
        self.in_shop = True
        events.status_window(shop_text=self.shop_menu)        
        events.game_event("Welcome to the shop. Please see the menu to the right.")
        return
        
    def exit_shop(self):
        self.in_shop = False
        events.game_event("You have exited the shop.")
        return
        
    def order_item(self, number):
        
        if number == None:
            events.game_event("You need to specify an item to order or EXIT.")
            return
        elif number[0] > len(self._shop_items) or number[0] <= 0:
            events.game_event("That is an improper selection. Choose again.")
            return
        else:
            events.game_event("You have selected {}.  If you would like to buy this item, please respond BUY.".format(self._shop_items[number[0] - 1].name))
            self._item_selected = number[0] - 1
            return
        
    def buy_item(self, number):
        if number is None and self._item_selected is None:
            events.game_event("You need to specify an item to buy or EXIT.")
            return
        if number is None:
            events.game_event("Congratulations! You have purchased {}.".format(self._shop_items[self._item_selected].name))
            return self._shop_items[self._item_selected]
        else:
            if number[0] > len(self._shop_items) or number[0] <= 0:
                events.game_event("That is an improper selection. Choose again.")
                return
            else:
                events.game_event("Congratulations! You have purchased {}.".format(self._shop_items[number[0] - 1].name))
                return self._shop_items[number[0] - 1]
            
        
    @property
    def shop_menu(self):
        return self._shop_menu
    @shop_menu.setter
    def shop_menu(self, menu_item):
        self._shop_menu = menu_item
        
    
    @property
    def in_shop(self):
        return self._in_shop
    @in_shop.setter
    def in_shop(self, value):
        self._in_shop = value
        
        
        
        