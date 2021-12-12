"""


TODO: Exit out of all demon programs when quit
TODO: Check the characters position before it moves or performs certain actions.
TODO: Integrate the BUY function into the shops.

"""

import random as random
import textwrap as textwrap

from app import db
from app.main import world, routes, enemies, command_parser, config, npcs, combat, spells
from app.main.models import EnemySpawn, Room


verbs = config.verbs
action_history = []
wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)


def do_action(action_input, character_file=None, room_file=None):
    action_history.insert(0,action_input)
    if not character_file:
        action_result = {"action_success": False,
                         "action_error":  "No character loaded. You will need to create a new character or load an existing character."
        }
        return action_result
    if len(action_input) == 0:
        action_result = {"action_success": False,
                         "action_error":  "No action submitted."
        }
        return action_result
    kwargs = command_parser.parser(action_input)
    return DoActions.do_action(kwargs['action_verb'], character_file, room_file, **kwargs)


class DoActions:
    def __init__(self, character_file, room_file, **kwargs):
        character = character_file
        self.action_result = {
            "action_success": True,
            "action_error": None,
            "room_change": {
                "room_change_flag":  False,
                "leave_room_text": None,
                "old_room":  None,
                "new_room":  None,
                "enter_room_text":  None
            },
            "area_change":  {
                "area_change_flag":  False,
                "old_area": None,
                "new_area": None
            },
            "display_room":  {
                "display_room_flag":  False,
                "display_room_text": None
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
        self.action_result_default = self.action_result.copy()

    _do_actions = {}

    @classmethod
    def register_subclass(cls, action):
        """Catalogues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls._do_actions[action] = subclass
            return subclass
        return decorator

    @classmethod
    def do_action(cls, action, character_file, room_file, **kwargs) -> dict:
        """Method used to initiate an action"""
        if action not in cls._do_actions:
            cls.action_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.action_result
        return cls._do_actions[action](character_file, room_file, **kwargs).action_result
    
    def update_room(self, character, old_room_number, leave_text, enter_text):
        self.action_result['room_change']['room_change_flag'] = True
        self.action_result['room_change']['leave_room_text'] = leave_text
        self.action_result['room_change']['old_room'] = old_room_number
        self.action_result['room_change']['new_room'] = character.get_room().room.room_number
        self.action_result['room_change']['enter_room_text'] = enter_text
        self.action_result['display_room_flag'] = True
        return

    def update_area(self, character, old_area):
        self.action_result['area_change']['area_change_flag'] = True
        self.action_result['area_change']['old_area'] = old_area
        self.action_result['area_change']['new_area'] = character.area_name
        return
    
    def update_character_output(self, character_output_text):
        self.action_result['character_output']['character_output_flag'] = True
        self.action_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.action_result['display_room']['display_room_flag'] = True
        self.action_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.action_result['room_output']['room_output_flag'] = True
        self.action_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.action_result['area_output']['area_output_flag'] = True
        self.action_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.action_result['status_output']['status_output_flag'] = True
        self.action_result['status_output']['status_output_text'] = status_text
        return

    def reset_result(self):
        self.action_result = self.action_result_default.copy()
        return
        


@DoActions.register_subclass('ask')
class Ask(DoActions):
    """\
    Certain npcs have information that is valuable for you. The ASK verb allows you to interact with these npcs
    and obtain that information.

    Usage:
    ASK <npc> about <subject>\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)
        
        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("Who are you trying to ask?")
            return
        elif not kwargs['indirect_object']:
            events.game_event("What are you trying to ask about?")
            return
        else:
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    npc.ask_about(object=kwargs['indirect_object'])
                    return
            else:
                events.game_event("That doesn't seem to do any good.")


@DoActions.register_subclass('attack')
class Attack(DoActions):
    """\
    ATTACK allows you to engage in combat with an enemy. Provided you are not in round time, ATTACK swings
    the weapon in your right hand (or your bare fist if there is no weapon) at the enemy. You will not be able
    to attack anyone other than enemies.

    Usage:
    ATTACK <enemy> : Engages an enemy and begins combat.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(status_text=character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(status_text=character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output(character_output_text="Who are you going to attack? You do not have a target.")
            self.update_status(status_text=character.get_status())
            return
        if kwargs['direct_object']:
            for enemy_file in room_file.enemies:
                if set(enemy_file.enemy.handle) & set(kwargs['direct_object']):
                    target_file = db.session.query(EnemySpawn).filter_by(id=enemy_file.id).first()
                    character.target = target_file.id
                    combat_action = combat.do_combat_action(aggressor='character', combat_action='melee', character_file=character_file, enemy_file=target_file, room_file=room_file)
                    self.action_result.update(combat_action.attack())
                    self.update_status(status_text=character.get_status())
                    db.session.commit()
                    return
            for npc in room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    self.update_character_output("{} will probably not appreciate that.".format(npc.name))
                    self.update_status(status_text=character.get_status())
                    return
            self.update_character_output("A {} is not around here.".format(kwargs['direct_object'][0]))
            self.update_status(status_text=character.get_status())
            return
        else:
            self.update_character_output("I'm sorry, I don't understand.")
            self.update_status(status_text=character.get_status())
            return
            
            
@DoActions.register_subclass('attribute')
class Attributes(DoActions):
    """\
    ATTRIBUTES allows you to view various attributes
    
    Usage:
    ATTRIBUTE <attirbute name>\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        self.update_character_output('''
Attribute:  {}
            '''.format(character.attack_strength_base))
        self.update_status(character.get_status())
        
        
@DoActions.register_subclass('buy')
class Buy(DoActions):
    """\
    BUY enables you to purchase an item from a shop.
    
    Usage:
    
    BUY <#>:  Finalize purchase of the selected item.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
         
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
            
        if room.is_shop == False:
            self.update_character_output("You can't seem to find a way to order anything here.")
            self.update_status(character.get_status())
            return
        if room.shop_filled == False:
            self.update_character_output("You will need to ORDER first.")
            self.update_status(character.get_status())
            return
        if character.in_shop == False:
            self.update_character_output("You have exited the shop. You will need to ORDER again.")
            self.update_status(character.get_status())
            return 
        if character.get_dominant_hand_inv() is not None:
            character.in_shop = False
            self.update_character_output("You will need to empty your right hand first. You exit the shop so you can empty your hand.")
            self.update_status(character.get_status())
            return
        if not kwargs['number_1']:
            self.action_result.update(room.shop.buy_item(number=character.shop_item_selected, character=character))
        else:
            self.action_result.update(room.shop.buy_item(number=kwargs['number_1'], character=character))
        if self.action_result['shop_item']['shop_item_flag']:
            try:
                character.set_dominant_hand_inv(self.action_result['shop_item']['shop_item'])
            except:
                print("WARNING: Shop did not deliver item")
        return


@DoActions.register_subclass('cast')
class Cast(DoActions):
    """\
    CAST allows you to engage in magical combat with an enemy. Provided you are not in round time and that you have property prepared your spell, CAST releases
    the spell at the enemy. You will not be able cast spells at anyone other than your enemies.

    Usage:
    CAST <enemy> : Releases a spell at an enemy.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text=f"Round time remaining... {character.get_round_time()} seconds.")
            self.update_status(status_text=character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(status_text=character.get_status())
            return
        if character.active_spell == None:
            self.update_character_output(character_output_text=f"You do not have a spell ready to cast. You need to PREPARE one.")
            self.update_status(status_text=character.get_status())
            return
        if character.check_cast_round_time():
            self.update_character_output(character_output_text=f"Your spell is not yet ready. Cast round time remaining... {character.get_cast_round_time()} seconds.")
            self.update_status(status_text=character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output(character_output_text="At whom are you going to cast the spell? You do not have a target.")
            self.update_status(status_text=character.get_status())
            return
        if kwargs['direct_object']:
            for enemy_file in room_file.enemies:
                if set(enemy_file.enemy.handle) & set(kwargs['direct_object']):
                    target_file = db.session.query(EnemySpawn).filter_by(id=enemy_file.id).first()
                    character.target = target_file.id
                    self.action_result.update(character.active_spell.cast_spell(character_file=character_file, target_file=target_file, room_file=room_file))
                    character.active_spell = None
                    self.update_status(status_text=character.get_status())
                    db.session.commit()
                    return
            for npc in room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    self.update_character_output("{} will probably not appreciate that.".format(npc.name))
                    self.update_status(status_text=character.get_status())
                    return
            self.update_character_output("A {} is not around here.".format(kwargs['direct_object'][0]))
            self.update_status(status_text=character.get_status())
            return
        else:
            self.update_character_output("I'm sorry, I don't understand.")
            self.update_status(status_text=character.get_status())
            return

        
@DoActions.register_subclass('depart')
class Depart(DoActions):
    """\

    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if not character.is_dead():
            self.update_character_output(character_output_text="You have nothing to depart from.")
            self.update_status(character.get_status())
            return
        if character.depart == False:
            character.depart = True
            self.update_character_output(character_output_text="Are you sure you want to depart? If so, please type DEPART CONFIRM.")
            self.update_status(character.get_status())
            return
        if character.depart == True:
            if kwargs['subject_verb'] == 'confirm':
                character.depart = False
                character.health = character.health_max
                old_room_number = room_file.room.room_number
                room_file.characters.remove(character_file)
                character.change_room(x=8, y=5, area='Dochas')
                room_file = character.get_room()
                room_file.characters.append(character_file)
                self.action_result.update(room_file.room.intro_text(character_file=character_file, 
                                                                    room_file=room_file))
                self.update_character_output("The world swirls around you and your body. You feel yourself depart from reality and you begin falling. After some time, you find the world around you materialize into a small shrine in front of you.")
                self.update_room(character=character, 
                                old_room_number=old_room_number,
                                leave_text=f"The body of {character.first_name} slowly fades into nothing.",
                                enter_text=f"{character.first_name} slowly fades into view, appearing relieved and confused.")
                self.update_status(character.get_status())
                return
            else:
                self.update_character_output("I'm sorry, I did not understand. Would you like to depart? If so, type DEPART CONFIRM.")
                self.update_status(character.get_status())  
                return 


@DoActions.register_subclass('drop')
class Drop(DoActions):
    """\
    DROP sets an object within your environment. This verb works the same as PUT <item>.

    Usage:
    DROP <item> : Places an item within an environment.
    DROP <item> in <object/item> : Will put an item within an object or within another item if that object or item
    is a container and if that object or item has enough room within it.
    DROP <item> on <object/item> : Will put an item on top of an object or on top of another item if that object
    or item is stackable.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        elif not kwargs['direct_object']:
            self.update_character_output("I'm sorry, I could not understand what you wanted.")
            self.update_status(character.get_status())
            return
        elif character.get_dominant_hand_inv() is None:
            self.update_character_output("You do not have that item in your hand")
            self.update_status(character.get_status())
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            self.update_character_output("You do not have that item in your right hand.")
            self.update_status(character.get_status())
            return
        else:
            room.add_item(character.get_dominant_hand_inv())
            self.update_character_output("You drop {}.".format(character.get_dominant_hand_inv().name))
            self.update_room_output("{} dropped {}.".format(character.first_name, character.get_dominant_hand_inv().name))
            character.set_dominant_hand_inv(item=None)
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('east')
@DoActions.register_subclass('e')
class East(DoActions):
    """\
    Moves you east, if you can move in that direction.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)   

        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text=f"Round time remaining... {character.get_round_time()} seconds.")
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output(f"You cannot move.  You are {character.position.name}.")
            self.update_status(character.get_status())
            return
        if world.tile_exists(x=character.location_x + 1, y=character.location_y, area=character.area_name):
            if room.shop_filled == True:
                if character.in_shop == True:
                    character.in_shop = False
                    room.shop.exit_shop()
            old_room_number = room_file.room.room_number 
            room_file.characters.remove(character_file)
            character.move_east()
            room_file = character.get_room()
            room_file.characters.append(character_file)
            self.action_result.update(room_file.room.intro_text(character_file=character_file, 
                                                                room_file=room_file))
            self.update_room(character=character, 
                             old_room_number=old_room_number,
                             leave_text=f"{character.first_name} went east.",
                             enter_text=f"{character.first_name} came from the west.")
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
            self.update_status(character.get_status())
            return
            
            
@DoActions.register_subclass('exit')
class Exit(DoActions):
    """\
    When ordering in a shop, EXIT leaves the order menu. In order to see the menu again, you will need to ORDER again.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        if room.is_shop == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return 
        if room.shop_filled == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return
        if character.in_shop == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return            
        else:
            character.in_shop = False
            self.action_result.update(room.shop.exit_shop())
            self.update_status(character.get_status())
            return

            
@DoActions.register_subclass('experience')
@DoActions.register_subclass('exp')
class Experience(DoActions):
    """\
    Displays your experience information.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        self.update_character_output('''\
Experience:  {}
        '''.format(character.experience))
        self.update_status(character.get_status())
        return


@DoActions.register_subclass('flee')
class Flee(DoActions):
    """\
    FLEE sends you in a random direction in your environment. FLEE can only be used when not in round time.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)    

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position.name))
            self.update_status(character.get_status())
            return
        if room.shop_filled == True:
            if character.in_shop == True:
                character.in_shop = False
        available_moves = room.adjacent_moves()
        r = random.randint(0, len(available_moves) - 1)
        flee_action = do_action(action_input=available_moves[r], character=character)
        self.action_result.update(flee_action.action_result)
        return


@DoActions.register_subclass('get')
@DoActions.register_subclass('take')
class Get(DoActions):
    """\
    GET retrieves an item from your surroundings. Many objects cannot be moved from their current position.
    The item will be taken by your right hand, therefore you right hand will need to be empty. This
    verb functions the same as TAKE.

    Usage:
    GET <item>\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output("I'm sorry, I could not understand what you wanted.")
            self.update_status(character.get_status())
            return
        for room_object in room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                self.update_character_output("Perhaps picking up {} is not a good idea.".format(room_object.name))
                return
        for enemy_file in room_file.enemies:
            if set(enemy_file.enemy.handle) & set(kwargs['direct_object']):
                self.update_character_output("Perhaps pickping up {} is not a good idea.".format(enemy_file.enemy.name))
                return
        if character.get_dominant_hand_inv() is None:
            item_found = False
            for room_item in room.items:
                if set(room_item.handle) & set(kwargs['direct_object']):
                    character.set_dominant_hand_inv(room_item)
                    room.remove_item(room_item)
                    self.update_character_output("You pick up {}.".format(room_item.name))
                    self.update_room_output("{} picks up {}.".format(character.first_name, room_item.name))
                    self.update_status(character.get_status())
                    return
            if not item_found:
                for inv_item in character.inventory:
                    if inv_item.container:
                        for sub_item in inv_item.items:
                            if set(sub_item.handle) & set(kwargs['direct_object']):
                                character.set_dominant_hand_inv(sub_item)
                                inv_item.items.remove(sub_item)
                                self.update_character_output("You take {} from {}.".format(sub_item.name, inv_item.name))
                                self.update_room_output("{} takes {} from {}.".format(character.first_name, sub_item.name, inv_item.name))
                                self.update_status(character.get_status())
                                return
            if not item_found:
                self.update_character_output("A " + kwargs['direct_object'][0] + " is nowhere to be found")
                self.update_status(character.get_status())
        else:
            self.update_character_output('You already have something in your right hand')
            self.update_status(character.get_status())


@DoActions.register_subclass('give')
class Give(DoActions):
    """\
    GIVE allows you to exchange items between you and various npcs. In order to give an item to an npc, you
    must have the item in your right hand.

    Usage:
    GIVE <item> to <npc> : Gives the item to the npc if the npc has the ability to accept the item.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        elif not kwargs['direct_object']:
            events.game_event("What are you trying to give?")
            return
        elif character.get_dominant_hand_inv() is None:
            events.game_event("You don't seem to be holding that item in your hand.")
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            events.game_event("You don't seem to be holding that item in your hand.")
            return
        elif not kwargs['indirect_object']:
            events.game_event("To whom do you want to give?")
            return
        else:
            for npc in character.room.npcs:
                if {npc.first_name.lower()} & set(kwargs['indirect_object']):
                    if npc.give_item(character.get_dominant_hand_inv()):
                        character.set_dominant_hand_inv(item=None)
                        character.print_status()
                        return
                    else:
                        return
            events.game_event("That didn't seem to work.")
            return


@DoActions.register_subclass('go')
class Go(DoActions):
    """\
    GO allows you to move toward a certain object. If the object can be passed through, you will pass through it.

    Usage:

    GO <object> : move toward or through an object.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position.name))
            self.update_status(character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output("Go where?")
            self.update_status(character.get_status())
            return
        found_object = False
        for room_object in room_file.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                found_object = True
                self.update_character_output("You move toward {}.".format(room_object.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_object.name)) 
                self.action_result.update(room_object.go_object(character_file=character_file, room_file=room_file))
                return
        for room_item in room_file.room.items:
            if set(room_item.handle) & set(kwargs['direct_object']):
                found_object = True
                self.update_character_output("You move toward {}.".format(room_item.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_item.name))
                self.update_status(character.get_status())
                return
        for room_npc in room_file.room.npcs:
            if set(room_npc.handle) & set(kwargs['direct_object']):
                found_object = True
                self.update_character_output("You move toward {}.".format(room_npc.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_npc.name))
                self.update_status(character.get_status())
                return
        for enemy_file in room_file.enemies:
            if set(enemy_file.enemy.handle) & set(kwargs['direct_object']):
                found_object = True
                self.update_character_output("You move toward {}.".format(enemy_file.enemy.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, enemy_file.enemy.name))
                self.update_status(character.get_status())
                return
        if found_object == False:
            self.update_character_output("You cannot seem to find a {}".format(kwargs['direct_object'][0]))
            return

        
@DoActions.register_subclass('health')
class Health(DoActions):
    """\
    HEALTH shows your current health attributes.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        self.update_character_output('''
Health:  {} of {} hit points
            '''.format(character.health,
                       character.health_max))
        self.update_status(character.get_status())
        return


@DoActions.register_subclass('help')
class Help(DoActions):
    """\
    Provides help on all parts of the game

    Usage:

    HELP <subject> : Output help on a specific subject.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        verb_list = ""

        if kwargs['subject_verb'] == None:
                    
            for a, b, c in zip(verbs[::3], verbs[1::3], verbs[2::3]):
                verb_list = verb_list + '{:30s}{:30s}{:30s}\n'.format(a,b,c)
            
            self.update_character_output("""
Below are the list of actions for which you can ask for help.
Type HELP <verb> for more information about that specific verb.
{}\
            """.format(verb_list))
            self.update_status(character.get_status())
            return
        elif kwargs['subject_verb'] in DoActions._do_actions:
            self.update_character_output(DoActions._do_actions[kwargs['subject_verb']].__doc__)
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("I'm sorry, what did you need help with?")
            self.update_status(character.get_status())
            return
            
@DoActions.register_subclass('info')
@DoActions.register_subclass('information')
class Information(DoActions):
    """\
    Provides general information on your character including level, experience, and other attributes.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        self.update_character_output(f'''\
Name:  {character.first_name} {character.last_name}
Gender:  {character.gender.name}
Heritage:  {character.heritage.name}
Profession:  {character.profession.name}
Level:  {character.level}\
            ''')
        self.update_status(character.get_status())
        return


@DoActions.register_subclass('inventory')
class Inventory(DoActions):
    """\
    INVENTORY allows you to view your inventory. It will list all items you have in your possession.  INVENTORY
    will not list the items within any containers you have.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.get_dominant_hand_inv():
            right_hand = "You have {} in your {} hand.".format(character.get_dominant_hand_inv().name, character.dominance)
        else:
            right_hand = "Your right hand is empty."
        if character.get_non_dominant_hand_inv():
            left_hand = "You have {} in your {} hand.".format(character.get_non_dominant_hand_inv().name, character.non_dominance)
        else:
            left_hand = "Your left hand is empty."
        inventory_clothing = [x.name for x in character.inventory if x.category == 'clothing']
        if len(inventory_clothing) > 1:
            inventory_clothing = "You are wearing {} and {}.".format(', '.join(inventory_clothing[:-1]), inventory_clothing[-1])
        elif len(inventory_clothing) == 1:
            inventory_clothing = "You are wearing {}.".format(inventory_clothing[0])
        else:
            inventory_clothing = "You are wearing nothing."
        
        inventory_armor = []  
        for category in character.armor:
            inventory_armor.append(character.armor[category])
        if len(inventory_armor) > 1:
            inventory_armor ="You are also wearing {} and {}.".format(character.object_pronoun, ', '.join(inventory_armor[:-1]), inventory_armor[-1])
        elif len(inventory_armor) == 1:
            inventory_armor = "You are also wearing {}.".format(inventory_armor[0].name)
        else:
            inventory_armor = "You are also wearing no armor.".format(character.object_pronoun)
        wealth = "You have {} gulden.".format(character.money)
        self.update_character_output('''\
{}
{}
{}
{}
{}
                                    \
                                    '''.format(right_hand,
                                               left_hand,
                                               wrapper.fill(inventory_clothing),
                                               wrapper.fill(inventory_armor),
                                               wrapper.fill(wealth)))
        self.update_status(character.get_status())
        
        
@DoActions.register_subclass('kneel')
class Kneel(DoActions):
    """\
    Moves you to a kneeling position. While you may perform many actions from this position,
    movement is not possible.
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
    
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == config.Position.kneeling:
            self.update_character_output('You seem to already be kneeling.')
            self.update_status(character.get_status())
            return 
        else:
            character.position = config.Position.kneeling
            self.update_character_output(character_output_text=f"You move yourself to a {character.position.name} position.")
            self.update_room_output(room_output_text=f"{character.first_name} move {character.possessive_pronoun}self to a kneeling position.")
            self.update_status(status_text=character.get_status())
            return
        
        
@DoActions.register_subclass('lie')
class Lie(DoActions):
    """\
    Moves you to a lying position on the ground. While many actions can be performed on the ground, 
    movement is not possible.
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == config.Position.lying:
            self.update_character_output('You seem to already be lying down.')
            self.update_status(character.get_status())
            return 
        else:
            character.position = config.Position.lying
            self.update_character_output(character_output_text="You lower yourself to the ground and lie down.")
            self.update_room_output(room_output_text="{} lowers {}self to a laying position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('look')
@DoActions.register_subclass('l')
class Look(DoActions):
    """\
    View the environment and objects or items within your environment.

    Usage:
    LOOK : shows the descriptions of the environment around you.
    LOOK <object/item> : shows the description of the object at which you want to look.
    LOOK <npc> : shows the description of the npc at which you want to look.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char

        if character.is_dead():
            self.action_result.update(room_file.room.intro_text(character_file=character_file, room_file=room_file))
            self.update_character_output(character_output_text="You're dead! Your actions will be limited until you can revive yourself.")
            self.update_status(character.get_status())
            return
        if kwargs['preposition'] == None:
            self.action_result.update(room_file.room.intro_text(character_file=character_file, room_file=room_file))
            self.update_status(character.get_status())
            return
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if kwargs['preposition'][0] == 'in':
            item_found = False
            if kwargs['indirect_object'] is None:
                self.update_character_output("I am not sure what you are referring to.")
                self.update_status(character.get_status())
                return
            for item in room_file.room.items + room_file.room.objects + room_file.room.npcs + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if isinstance(item, npcs.NPC):
                    self.update_character_output("It wouldn't be advisable to look in " + item.name)
                    self.update_status(character.get_status())
                    return
                if set(item.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(item.get_contents())
                    self.update_status(character.get_status())
                    return
            for enemy_file in room_file.enemies:
                if set(enemy_file.enemy.handle) & set(kwargs['indirect_object']):
                    self.update_character_output("It wouldn't be advisable to look in " + enemy_file.enemy.name)
                    self.update_status(character.get_status())
                    return
            if item_found is False:
                self.update_character_output("A {} is nowhere to be found.".format(kwargs['indirect_object'][0]))
                self.update_status(character.get_status())
                return
        if kwargs['preposition'][0] == 'at':
            item_found = False
            if kwargs['indirect_object'] is None:
                self.update_character_output("I am not sure what you are referring to.")
                self.update_status(character.get_status())
                return
            for item in room_file.room.items + room_file.room.objects + room_file.room.npcs + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if not item:
                    pass
                elif set(item.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(item.view_description())
                    self.update_status(character.get_status())
                    return
            for enemy_file in room_file.enemies:
                if set(enemy_file.enemy.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(enemy_file.enemy.view_description())
                    self.update_status(character.get_status())
                    return
            for character_file_search in room_file.characters:
                if character_file_search.char.first_name == character_file.char.first_name:
                    self.update_character_output(character_output_text="You take a long look at yourself.")
                    self.update_room_output(room_output_text="{} looks {}self over.".format(character.first_name, character.possessive_pronoun))
            if item_found is False:
                self.update_character_output("At what did you want to look?")
                self.update_status(character.get_status())
                return
        else:
            self.update_character_output("I'm sorry, I didn't understand you.")
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('north')
@DoActions.register_subclass('n')
class North(DoActions):
    """\
    Moves you north, if you can move in that direction.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)   

        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position.name))
            self.update_status(character.get_status())
            return
        if world.tile_exists(x=character.location_x, y=character.location_y - 1, area=character.area_name):
            if room.shop_filled == True:
                if character.in_shop == True:
                    character.in_shop = False
                    room.shop.exit_shop()
            old_room_number = room.room_number 
            room_file.characters.remove(character_file)
            character.move_north()
            room_file = character.get_room()
            room_file.characters.append(character_file)
            self.action_result.update(room_file.room.intro_text(character_file=character_file, 
                                                                room_file=room_file))
            self.update_room(character=character, 
                             old_room_number=old_room_number,
                             leave_text=f"{character.first_name} went north.",
                             enter_text=f"{character.first_name} came from the south.")
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
            self.update_status(character.get_status())
            return
            
            
@DoActions.register_subclass('order')
class Order(DoActions):
    """\
    In certain rooms, you are able to order products through an ordering system. ORDER initiates the ordering system.\
    
    Usage:
    ORDER:  Enters the shop and displays the shop menu in the status window
    ORDER <#>:  Orders the relevant item. You cannot order a specific item until you have entered the shop using the ORDER command by itself.
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
         
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return     
        if room.is_shop == False:
            self.update_character_output("You can't seem to find a way to order anything here.")
            self.update_status(character.get_status())
            return 
        elif room.is_shop == True:  
            if room.shop_filled == False:             
                room.fill_shop()
                character.in_shop = True
                self.action_result.update(room.shop.enter_shop())
                return
            if character.in_shop == False:
                character.in_shop = True
                self.action_result.update(room.shop.enter_shop())
                return
            character.shop_item_selected = kwargs['number_1']
            self.action_result.update(room.shop.order_item(kwargs['number_1']))
            return
                

@DoActions.register_subclass('position')
@DoActions.register_subclass('pos')
class Position(DoActions):
    """\
    Displays the position you are currently in.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        self.update_character_output('''You are currently in the {} position.'''.format(character.position.name))
        self.update_status(character.get_status())


@DoActions.register_subclass('prepare')
@DoActions.register_subclass('prep')
class Prepare(DoActions):
    """
    Prepares a spell for casting. Spell can be cast once soft round time has passed.

    Usage:
    PREPARE <SPELL #>:  Prepares the spell as long as you have learned the spell.
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.active_spell:
            self.update_character_output(character_output_text="You currently have a spell prepared.")
            self.update_status(character.get_status())
            return
        if kwargs['number_1']:
            for spell_category in character.spells:
                if set(character.spells[spell_category]) & set(kwargs['number_1']):
                    character.active_spell = spells.create_spell(spell_category=spell_category, spell_number=kwargs['number_1'][0])
                    self.action_result.update(character.active_spell.prepare_spell(character_file=character_file, room_file=room_file))
                    self.update_status(character.get_status())
                    return
            self.update_character_output(character_output_text="You don't know that spell yet.")
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('put')
class Put(DoActions):
    """\
    PUT sets an object within your environment.  This usage works the same as DROP <item>.

    Usage:
    PUT <item> : Places an item within an environment.
    PUT <item> in <object/item> : Will put an item within an object or within another item if that object or item
    is a container and if that object or item has enough room within it.
    PUT <item> on <object/item> : Will put an item on top of an object or on top of another item if that object
    or item is stackable.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output("What is it you're trying to put down?")
            self.update_status(character.get_status())
            return
        elif character.get_dominant_hand_inv() is None:
            self.update_character_output("You do not have that item in your hand.")
            self.update_status(character.get_status())
            return
        elif not set(character.get_dominant_hand_inv().handle) & set(kwargs['direct_object']):
            self.update_character_output("You do not have that item in your right hand.")
            self.update_status(character.get_status())
            return
        elif kwargs['preposition'][0] == "in":
            for inv_item in character.inventory:
                if set(inv_item.handle) & set(kwargs['indirect_object']):
                    if inv_item.container == False:
                        self.update_character_output("{} won't fit in there.".format(character.get_dominant_hand_inv().name))
                        self.update_status(character.get_status())
                        return
                    if len(inv_item.items) == inv_item.capacity:
                        self.update_character_output("{} can't hold any more items".format(inv_item.name))
                        self.update_status(character.get_status())
                        return
                    inv_item.items.append(character.get_dominant_hand_inv())
                    self.update_character_output("You put {} {} {}".format(character.get_dominant_hand_inv().name, kwargs['preposition'][0], inv_item.name))
                    self.update_room_output("{} puts {} {} {}".format(character.first_name, character.get_dominant_hand_inv().name, kwargs['preposition'][0], inv_item.name))
                    character.set_dominant_hand_inv(item=None)
                    self.update_status(character.get_status())
                    return
            for room_item in room.items:
                if set(room_item.handle) & set(kwargs['indirect_object']):
                    if room_item.container == False:
                        self.update_character_output("{} won't fit {} there.".format(character.right_hand_inv[0].name, kwargs['preposition'][0]))
                        self.update_status(character.get_status())
                        return
                    room_item.items.append(character.get_dominant_hand_inv())
                    character.set_dominant_hand_inv(item=None)
                    self.update_character_output("You put {} {} {}".format(character.get_dominant_hand_inv().name, kwargs['preposition'][0], room_item.name))
                    self.update_room_output("{} puts {} {} {}".format(character.first_name, character.get_dominant_hand_inv().name, kwargs['preposition'][0], room_item.name))
                    character.set_dominant_hand_inv(item=None)
                    self.update_status(character.get_status())
                    return
            for enemy_file in room_file.enemies:
                if set(enemy_file.enemy.handle) & set(kwargs['indirect_object']):
                    self.update_character_output("That might not be a good idea.")
                    self.update_status(character.get_status())
                    return
        elif kwargs['preposition'][0] == "on":
            self.update_character_output("You cannot stack items yet.")
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("That item is not around here, unfortunately.")
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('quit')
class Quit(DoActions):
    """\
    Exits the game.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        self.update_character_output("You will need to find a way to exit the game.")
        return


@DoActions.register_subclass('say')
class Say(DoActions):
    """\
    SAY allows you to communicate with other characters in the game.

    Usage:
    SAY <text>:  Communicate the <text> to the room.
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        self.update_character_output("You say '{}'".format(kwargs['say_text']))
        self.update_room_output("{} says '{}'".format(character.first_name, kwargs['say_text']))
        self.update_status(character.get_status())
        return
        

@DoActions.register_subclass('search')
class Search(DoActions):
    """\
    SEARCH allows you to explore your environment if the object, enemy, or area can be explored.

    Usage:
    SEARCH : Searches the environment around you and uncovers hidden items or objects.
    SEARCH <enemy> : Searches an enemy, uncovers any potential items that the enemy could be hiding, and places
    them in your environment.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not kwargs['direct_object']:
            items_found = 0
            for hidden_item in room.hidden:
                if 100 - character.level >= hidden_item.visibility:
                    room.add_item(hidden_item)
                    room.remove_hidden_item(hidden_item)
                    self.update_character_output(f'You found {hidden_item.name}!')
                    items_found += 1
            if items_found == 0:
                self.update_character_output("There doesn't seem to be anything around here.")
            return
        else:
            for object in room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    self.action_result.update(object.search(character_file=character_file, room_file=room_file))
                    return
            for item in room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    self.update_character_output(f"Searching {item.name} will not do you much good.")
                    return
            for char in room.enemies + character.room.npcs:
                if set(char.handle) & set(kwargs['direct_object']):
                    self.update_character_output(f"{char.first_name} probably will not appreciate that.")
                    return
            else:
                self.update_character_output("That doesn't seem to be around here.")
                return


@DoActions.register_subclass('sell')
class Sell(DoActions):
    """\
    SELL allows you to exchange items for gulden. Certain merchants look for items you may find in the wilds.
    Different merchants look for different items. The item must be in your right hand.

    Usage:
    SELL <item> to <npc>  : Exchanges items for gulden with an npc if an item can be exchanged.
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("What is it you are trying to sell?")
            return
        for npc in character.room.npcs:
            if set(npc.handle) & {kwargs['indirect_object']}:
                npc.sell_item(item=character.get_dominant_hand_inv())
                return
        else:
            events.game_event("Who are you trying to sell to?")
        
        
@DoActions.register_subclass('sit')
class Sit(DoActions):
    """\
    Moves you to a sitting position. While you can perform many actions while in a sitting position,
    movement is no possible.
    """        
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == config.Position.sitting:
            self.update_character_output(character_output_text="You seem to already be sitting.")
            self.update_status(status_text=character.get_status())
            return
        else:
            character.position = config.Position.sitting
            self.update_character_output(character_output_text="You move yourself to a sitting position.")
            self.update_room_output(room_output_text="{} moves {}self to a sitting position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('skills')
class Skills(DoActions):
    """\
    SKILLS displays the skills available to you as well as the skill rating for your character_file. Different skills
    allow you to accomplish different tasks.

    Usage:
    SKILLS:  Shows your available skills and their rating.
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        self.update_character_output(character_output_text=f"""\
[Skill]:        [Rank] ([Bonus])
Edged Weapons:    {character.skills['edged_weapons']}  ({character.skills_bonus['edged_weapons']})          Dodging:            {character.skills['dodging']}  ({character.skills_bonus['dodging']})
Blunt Weapons:    {character.skills['blunt_weapons']}  ({character.skills_bonus['blunt_weapons']})          Physical Fitness:   {character.skills['physical_fitness']}  ({character.skills_bonus['physical_fitness']})
Polearm Weapons:  {character.skills['polearm_weapons']}  ({character.skills_bonus['polearm_weapons']})          Perception:         {character.skills['perception']}  ({character.skills_bonus['perception']})
Armor:            {character.skills['armor']}  ({character.skills_bonus['armor']})                     Spell Research:         {character.skills['spell_research']}  ({character.skills_bonus['spell_research']})
Shield:           {character.skills['shield']}  ({character.skills_bonus['shield']})                     Magic Harnessing:         {character.skills['magic_harnessing']}  ({character.skills_bonus['magic_harnessing']})
         """)
        self.update_status(character.get_status())


@DoActions.register_subclass('skin')
class Skin(DoActions):
    """\
    Many enemies are able to be skinned for various pelts, hides, etc. The SKIN verb allows you to skin enemies.
    if successful the resulting item will be places within the environment. Not all enemies are able to be skinned.

    Usage:
    SKIN <enemy> : Skins an enemy and, if successful, leaves a skin.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == config.Position.sitting:
            self.update_character_output(character_output_text="You seem to already be sitting.")
            self.update_status(status_text=character.get_status())
            return
        elif not kwargs['direct_object']:
            self.update_character_output("What are you trying to skin?")
            return
        else:
            for object in room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    self.action_result.update(object.skin_corpse(character_file=character_file, room_file=room_file))
                    return
            for item in room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    self.update_character_output("You can seem to find any way to skin {}.".format(item.name))
                    return
            for npc in room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    self.update_character_output("You approach {}, but think better of it.".format(npc.name))
                    return


@DoActions.register_subclass('south')
@DoActions.register_subclass('s')
class South(DoActions):
    """\
    Moves you south, if you can move in that direction.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)    

        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position.name))
            self.update_status(character.get_status())
            return
        if world.tile_exists(x=character.location_x, y=character.location_y + 1, area=character.area_name):
            if room.shop_filled == True:
                if character.in_shop == True:
                    character.in_shop = False
                    room.shop.exit_shop()
            old_room_number = room.room_number 
            room_file.characters.remove(character_file)
            character.move_south()
            room_file = character.get_room()
            room_file.characters.append(character_file)
            self.action_result.update(room_file.room.intro_text(character_file=character_file, 
                                                                room_file=room_file))
            self.update_room(character=character, 
                             old_room_number=old_room_number,
                             leave_text=f"{character.first_name} went south.",
                             enter_text=f"{character.first_name} came from the north.")
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('spells')
class Spells(DoActions):
    """\
    SPELLS displays the spells your currently know.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        self.update_character_output(f'''\
Spells:
{character.get_spell_output()}\
            ''')
        self.update_status(character.get_status())
        return
            
            
@DoActions.register_subclass('stance')
class Stance(DoActions):
    """\
    STANCE controls the position in which you carry yourself in combat. Your stance will affect the amount of 
    attack and defensive strength you have during combat.
    
    Usage:
    STANCE:  Shows your current stance.
    STANCE <type>: Changes your stance to the desired stance.
    
    Types of Stances:
    OFFENSE
    FORWARD
    NEUTRAL
    GUARDED
    DEFENSE\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        desired_stance = kwargs['adjective_1']

        if not desired_stance:
            self.update_character_output(f'''You are currently in the {character.stance.name} stance.''')
            self.update_status(character.get_status())
            return
        if config.Stance.check_for_name_match(desired_stance[0]):
            character.stance = config.Stance[desired_stance[0]]
            self.update_character_output(f'''You are now in {character.stance.name} stance.''')
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot form that stance.")
            self.update_status(character.get_status())
            return


@DoActions.register_subclass('stand')
class Stand(DoActions):
    """\
    Raises you to the standing position if you are not already in the standing position.
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)
        
        character = character_file.char
        room = room_file.room
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == config.Position.standing:
            self.update_character_output(character_output_text="You seem to already be standing.")
            self.update_status(status_text=character.get_status())
            return
        else:
            character.position = config.Position.standing
            self.update_character_output(character_output_text="You raise yourself to a standing position.")
            self.update_room_output(room_output_text="{} raises {}self to a standing position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('stats')
class Stats(DoActions):
    """\
    Displays your general statistics.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room

        self.update_character_output('''
Name:  {} {}
Level: {}
Strength:       {}  ({})        Intellect:      {}  ({})
Constitution:   {}  ({})        Wisdom:         {}  ({})
Dexterity:      {}  ({})        Logic:          {}  ({})
Agility:        {}  ({})        Spirit:         {}  ({})
        '''.format(character.first_name,
                   character.last_name,
                   character.level,
                   character.stats['strength'], character.stats_bonus['strength'],
                   character.stats['intellect'], character.stats_bonus['intellect'],
                   character.stats['constitution'], character.stats_bonus['constitution'],
                   character.stats['wisdom'], character.stats_bonus['wisdom'],
                   character.stats['dexterity'], character.stats_bonus['dexterity'],
                   character.stats['logic'], character.stats_bonus['logic'],
                   character.stats['agility'], character.stats_bonus['agility'],
                   character.stats['spirit'], character.stats_bonus['spirit'])
              )
        self.update_status(character.get_status())


@DoActions.register_subclass('wealth')
class Wealth(DoActions):
    """\
    WEALTH shows your current wealth.\
    """
    
    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)

        character = character_file.char
        room = room_file.room
        
        self.update_character_output(f'''\
You currently have {character.money} gulden after searching through your pockets.\
            ''')
        self.update_status(character.get_status())
        return
        

@DoActions.register_subclass('west')
@DoActions.register_subclass('w')
class West(DoActions):
    """\
    Moves you west, if you can move in that direction.\
    """

    def __init__(self, character_file, room_file, **kwargs):
        DoActions.__init__(self, character_file, room_file, **kwargs)    

        character = character_file.char
        room = room_file.room 
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position.name))
            self.update_status(character.get_status())
            return
        if world.tile_exists(x=character.location_x - 1, y=character.location_y, area=character.area_name):
            if room.shop_filled == True:
                if character.in_shop == True:
                    character.in_shop = False
                    room.shop.exit_shop()
            old_room_number = room.room_number 
            room_file.characters.remove(character_file)
            character.move_west()
            room_file = character.get_room()
            room_file.characters.append(character_file)
            self.action_result.update(room_file.room.intro_text(character_file=character_file, 
                                                                room_file=room_file))
            self.update_room(character=character, 
                             old_room_number=old_room_number,
                             leave_text=f"{character.first_name} went west.",
                             enter_text=f"{character.first_name} came from the east.")
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
            self.update_status(character.get_status())
            return



def do_enemy_action(action_input, enemy_file=None, character_file=None, room_file=None, **kwargs):
    action_history.insert(0,action_input)
    if not enemy_file:
        action_result = {"action_success": False,
                         "action_error":  "No enemy loaded. You will need to create a new character or load an existing character."
        }
        return action_result
    if len(action_input) == 0:
        action_result = {"action_success": False,
                         "action_error":  ""
        }
        return action_result
    kwargs = command_parser.parser(action_input)
    return EnemyAction.do_enemy_action(kwargs['action_verb'], enemy_file, character_file, room_file, **kwargs)


class EnemyAction:
    def __init__(self, enemy, character_file, room_file, **kwargs):
        self.kwargs = kwargs        
        self.action_result = {
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
                "display_room_text": None
            },
            "character_output":  {
                "character_output_flag":  False,
                "character_output_text":  None
            },
            "room_output":  {
                "room_output_flag":  False,
                "room_output_text":  None,
                "room_output_number":  None
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

    do_enemy_actions = {}

    @classmethod
    def register_subclass(cls, action):
        """Catalogues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.do_enemy_actions[action] = subclass
            return subclass
        return decorator

    @classmethod
    def do_enemy_action(cls, action, enemy_file, character_file, room_file, **kwargs):
        """Method used to initiate an action"""
        if action not in cls.do_enemy_actions:
            cls.action_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.action_result
        return cls.do_enemy_actions[action](enemy_file, character_file, room_file, **kwargs).action_result

    def update_room(self, enemy, leave_text, enter_text, old_room_number):
        self.action_result['room_change']['room_change_flag'] = True
        self.action_result['room_change']['leave_room_text'] = leave_text
        self.action_result['room_change']['old_room'] = old_room_number
        self.action_result['room_change']['new_room'] = enemy.get_room().room.room_number
        self.action_result['room_change']['enter_room_text'] = enter_text
        self.action_result['display_room_flag'] = True
        return
    
    def update_character_output(self, character_output_text):
        self.action_result['character_output']['character_output_flag'] = True
        self.action_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.action_result['display_room']['display_room_flag'] = True
        self.action_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text, room_output_number):
        self.action_result['room_output']['room_output_flag'] = True
        self.action_result['room_output']['room_output_text'] = room_output_text
        self.action_result['room_output']['room_output_number'] = room_output_number
        return
        
    def update_area_output(self, area_output_text):
        self.action_result['area_output']['area_output_flag'] = True
        self.action_result['area_output']['area_output_text'] = area_output_text
        return

    def update_status(self, status_text):
        self.action_result['status_output']['status_output_flag'] = True
        self.action_result['status_output']['status_output_text'] = status_text
        return


    def __str__(self):
        return "{}: {}".format(self.action, self.name)

@EnemyAction.register_subclass('attack')
class Attack(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)

        if character_file:
            combat_action = combat.do_combat_action(aggressor='enemy', combat_action='melee', enemy_file=enemy_file, character_file=character_file, room_file=room_file)
            self.action_result.update(combat_action.attack())
            self.update_status(status_text=character_file.char.get_status())
            routes.enemy_event(action_result=self.action_result, character_file=character_file)
            return


@EnemyAction.register_subclass('leave')
class Leave(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x, y=enemy.location_y, area=enemy.area):
            self.update_room_output(room_output_text=enemy.text_leave, room_output_number=enemy.get_room().room.room_number)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('guard')
class Guard(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x, y=enemy.location_y, area=enemy.area):
            print("enemy is about to guard.")
            self.update_room_output(room_output_text=enemy.text_guard_kill_room, room_output_number=enemy.get_room().room_number)
            self.update_character_output(character_output_text=enemy.text_guard_kill_character)
            routes.enemy_event(action_result=self.action_result)
            print("enemy has guarded.")
            return


@EnemyAction.register_subclass('east')
class MoveEastEnemy(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x + 1, y=enemy.location_y, area=enemy.area):
            old_room = enemy.get_room().room.room_number
            enemy.move_east()
            self.update_room(enemy=enemy, leave_text=enemy.text_move_out + "east.", enter_text=enemy.text_move_in, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('north')
class MoveNorthEnemy(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x, y=enemy.location_y - 1, area=enemy.area):
            old_room = enemy.get_room().room.room_number
            enemy.move_north()
            self.update_room(enemy=enemy, leave_text=enemy.text_move_out + "north.", enter_text=enemy.text_move_in, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('south')
class MoveSouthEnemy(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x, y=enemy.location_y + 1, area=enemy.area):
            old_room = enemy.get_room().room.room_number
            enemy.move_south()
            self.update_room(enemy=enemy, leave_text=enemy.text_move_out + "south.", enter_text=enemy.text_move_in, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('west')
class MoveWestEnemy(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x - 1, y=enemy.location_y, area=enemy.area):
            old_room = enemy.get_room().room.room_number
            enemy.move_west()
            self.update_room(enemy=enemy, leave_text=enemy.text_move_out + "west.", enter_text=enemy.text_move_in, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('spawn')
class Spawn(EnemyAction):
    def __init__(self, enemy_file, character_file, room_file, **kwargs):
        super().__init__(enemy=enemy_file,
                         character_file=character_file,
                         room_file=room_file,
                         kwargs=kwargs)
        enemy = enemy_file.enemy

        if world.tile_exists(x=enemy.location_x - 1, y=enemy.location_y, area=enemy.area):
            self.update_room_output(room_output_text=enemy.text_entrance, room_output_number=enemy.get_room().room.room_number)
            routes.enemy_event(action_result=self.action_result)
        return

