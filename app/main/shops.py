


from app.main import mixins, items
    
    
class Shop(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, shop_name: str, shop_items: list, **kwargs):
        
        self._shop_name = shop_name
        self._shop_data = shop_items
        self._shop_items = []
        self._item_selected = None
        self._shop_menu = False
        
        for category in self._shop_data:
            for item in self._shop_data[category]:
                self._shop_items.append(items.create_item(item_category=category, item_name=item))    

        self.shop_result = {
            "shop_success": True,
            "shop_error": None,
            "room_change": {
                "room_change_flag":  False,
                "leave_room_text": None,
                "old_room":  None,
                "new_room":  None,
                "enter_room_text":  None
            },
            "display_room_flag":  False,
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
            "status_output":  None,
            "shop_item":  {
                "shop_item_flag":  False,
                "shop_item": None
            }
        }          

    def update_room(self, character, old_room_number):
        self.shop_result['room_change']['room_change_flag'] = True
        self.shop_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.shop_result['room_change']['old_room'] = old_room_number
        self.shop_result['room_change']['new_room'] = character.room.room_number
        self.shop_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.shop_result['display_room_flag'] = True
        return
    
    def update_character_output(self, character_output_text):
        self.shop_result['character_output']['character_output_flag'] = True
        self.shop_result['character_output']['character_output_text'] = character_output_text

    def update_display_room(self):
        self.shop_result['display_room_flag'] = True
        
    def update_room_output(self, room_output_text):
        self.shop_result['room_output']['room_output_flag'] = True
        self.shop_result['room_output']['room_output_text'] = room_output_text
        
    def update_area_output(self, area_output_text):
        self.shop_result['area_output']['area_output_flag'] = True
        self.shop_result['area_output']['area_output_text'] = area_output_text
    
    def update_status(self, status_text):
        self.shop_result['status_output'] = status_text

    def update_shop_item(self, shop_item):
        self.shop_result['shop_item']['shop_item_flag'] = True
        self.shop_result['shop_item']['shop_item'] = shop_item

    @property
    def shop_menu(self):
        return self._shop_menu
    @shop_menu.setter
    def shop_menu(self, menu_item):
        self._shop_menu = menu_item

    @property
    def item_selected(self):
        return self._item_selected
    @item_selected.setter
    def item_selected(self, item_selected):
        self._item_selected = item_selected
        
    def write_shop_menu(self):
        item_number = 1
        self.shop_menu = []
        self.shop_menu.append("<b>" + self._shop_name + "</b>")
        for item in self._shop_items:
            self.shop_menu.append("{}.  {}".format(item_number, item.name))
            item_number += 1
        self.shop_menu.append("")
        self.shop_menu.append("To order, ORDER <#>.")
        self.shop_menu.append("To exit, EXIT.")
        return

    def get_shop_menu(self):
        self.update_status(status_text=self.shop_menu)
        return
        
    def enter_shop(self):   
        self.get_shop_menu()
        self.update_character_output(character_output_text="Welcome to the shop. Please see the menu to the right.")
        return self.shop_result
        
    def exit_shop(self):
        self.update_character_output(character_output_text="You have exited the shop")
        return self.shop_result
        
    def order_item(self, number):
        if number == None:
            self.update_character_output(character_output_text="You need to specify an item to order or EXIT.")
            return self.shop_result
        elif number[0] > len(self._shop_items) or number[0] <= 0:
            self.update_character_output(character_output_text="That is an improper selection. Choose again.")
            return self.shop_result
        else:
            self.update_character_output(character_output_text="You have selected {}.  If you would like to buy this item, please respond BUY.".format(self._shop_items[number[0] - 1].name))
            return self.shop_result
        
    def buy_item(self, number):
        if number is None:
            self.update_character_output(character_output_text="You need to specify an item to buy or EXIT.")
            return self.shop_result
        else:
            if number[0] > len(self._shop_items) or number[0] <= 0:
                self.update_character_output(character_output_text="That is an improper selection. Choose again.")
                return self.shop_result
            else:
                self.update_character_output(character_output_text="Congratulations! You have purchased {}.".format(self._shop_items[number[0] - 1].name))
                self.update_shop_item(shop_item=self._shop_items[number[0] - 1])
                return self.shop_result
        
        
        
        