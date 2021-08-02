


from app.main import mixins, config, combat


spell_levels = config.SPELL_LEVELS


def get_spells_skill_level(spell_base, skill_level):
    spells = spell_levels.loc[0:skill_level][spell_base].tolist()
    return [int(x) for x in spells if str(x) != 'nan']


def create_spell(spell_category, spell_number, **kwargs):
    return Spell.create_spell(spell_category, spell_number, **kwargs)


class Spell(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, spell_data, **kwargs):

        self.spell_data = spell_data
        self.spell_number = spell_data['number']
        self.name = spell_data['name']
        self.description = spell_data['description']
        self.spell_type = spell_data['spell_type']
        self.prepare_round_time = spell_data['prepare_round_time']
        self.cast_round_time = spell_data['cast_round_time']

        self.text_cast_character = spell_data['text_output']['text_cast_character']
        self.text_cast_room = spell_data['text_output']['text_cast_room']

        self.spell_result = {
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
            "status_output": {
                "status_output_flag": False,
                "status_output_text": None
            }
        }
        self.spell_result_default = self.spell_result.copy()

    def update_room(self, character, old_room_number):
        self.spell_result['room_change']['room_change_flag'] = True
        self.spell_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.spell_result['room_change']['old_room'] = old_room_number
        self.spell_result['room_change']['new_room'] = character.room.room_number
        self.spell_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.spell_result['display_room_flag'] = True
        return
    
    def update_character_output(self, character_output_text):
        self.spell_result['character_output']['character_output_flag'] = True
        self.spell_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.spell_result['display_room']['display_room_flag'] = True
        self.spell_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.spell_result['room_output']['room_output_flag'] = True
        self.spell_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.spell_result['area_output']['area_output_flag'] = True
        self.spell_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.spell_result['status_output']['status_output_flag'] = True
        self.spell_result['status_output']['status_output_text'] = status_text
        return

    def reset_result(self):
        self.spell_result = self.spell_result_default.copy()
        return

    spell_categories = {}

    @classmethod
    def register_subclass(cls, spell_category):
        """Catologues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.spell_categories[spell_category] = subclass
            return subclass
        return decorator
    
    @classmethod
    def create_spell(cls, spell_category, spell_name, **kwargs):
        """Method used to initiate an action"""
        if spell_category not in cls.spell_categories:
            cls.item_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.item_result
        return cls.spell_categories[spell_category](spell_name, **kwargs)

    def prepare_spell(self):
        pass

    def cast_spell(self):
        pass


@Spell.register_subclass('enchanter')
class EnchanterSpell(Spell):
    def __init__(self, spell_number: int, **kwargs):
        category_data = self.get_spell_category_by_name('enchanter')
        spell_data = category_data[str(spell_number)]
        Spell.__init__(self, spell_data=spell_data, **kwargs)

    def prepare_spell(self, character_file, room_file):
        self.reset_result()
        self.update_character_output(character_output_text=f"""\
You make a brief gesture.
Casting round time is {character_file.char.get_cast_round_time()} seconds.\
        """)
        self.update_room_output(room_output_text=f"{character_file.char.first_name} makes a brief gesture.")
        character_file.char.set_cast_round_time(self.prepare_round_time)
        return self.spell_result

    def cast_spell(self, character_file, target_file, room_file):
        self.reset_result()
        if self.spell_type == "bolt":
            self.spell_result.update(combat.bolt_attack_enemy(target_file=target_file, character_file=character_file, room_file=room_file))
            return self.spell_result

@Spell.register_subclass('elemental')
class ElementalSpell(Spell):
    def __init__(self, spell_number: int, **kwargs):
        category_data = self.get_spell_category_by_name('elemental')
        spell_data = category_data[str(spell_number)]
        Spell.__init__(self, spell_data=spell_data, **kwargs)


