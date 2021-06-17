"""


TODO: Exit out of all demon programs when quit
TODO: Check the characters position before it moves or performs certain actions.
TODO: Integrate the BUY function into the shops.

"""

import random as random
import textwrap as textwrap

from app.main import world, routes, enemies, command_parser, config, npcs, combat


verbs = config.verbs
stances = config.stances
action_history = []
wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)


def do_action(action_input, character=None):
    action_history.insert(0,action_input)
    if not character:
        action_result = {"action_success": False,
                         "action_error":  "No character loaded. You will need to create a new character or load an existing character."
        }
        return action_result
    if len(action_input) == 0:
        action_result = {"action_success": False,
                         "action_error":  ""
        }
        return action_result
    kwargs = command_parser.parser(action_input)
    return DoActions.do_action(kwargs['action_verb'], character, **kwargs)


class DoActions:
    def __init__(self, character, **kwargs):
        self.character = character
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
            "status_output":  None
        }

    do_actions = {}

    @classmethod
    def register_subclass(cls, action):
        """Catalogues actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.do_actions[action] = subclass
            return subclass
        return decorator

    @classmethod
    def do_action(cls, action, character, **kwargs):
        """Method used to initiate an action"""
        if action not in cls.do_actions:
            cls.action_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.action_result
        return cls.do_actions[action](character, **kwargs).action_result
    
    def update_room(self, character, old_room_number):
        self.action_result['room_change']['room_change_flag'] = True
        self.action_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.action_result['room_change']['old_room'] = old_room_number
        self.action_result['room_change']['new_room'] = character.room.room_number
        self.action_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
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
        
    def update_room_output(self, room_output_text):
        self.action_result['room_output']['room_output_flag'] = True
        self.action_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.action_result['area_output']['area_output_flag'] = True
        self.action_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.action_result['status_output'] = status_text
        return
        


@DoActions.register_subclass('ask')
class Ask(DoActions):
    """\
    Certain npcs have information that is valuable for you. The ASK verb allows you to interact with these npcs
    and obtain that information.

    Usage:
    ASK <npc> about <subject>\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if kwargs['direct_object']:
            character.target = kwargs['direct_object']
        if not character.target:
            events.game_event("Who are you going to attack? You do not have a target.")
            return
        else:
            for npc in character.room.npcs:
                if set(npc.handle) & set(character.target):
                    events.game_event("{} will probably not appreciate that.".format(npc.name))
                    return
            enemy_found = False
            for enemy in character.room.enemies:
                if set(enemy.handle) & set(character.target):
                    enemy_found = True
                    combat.melee_attack_enemy(character, enemy)
                    return
            if not enemy_found:
                events.game_event("{} is not around here.".format(kwargs['direct_object']))
                return
            
        
@DoActions.register_subclass('attribute')
class Attributes(DoActions):
    """\
    ATTRIBUTES allows you to view various attributes\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
         
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
            
        if character.room.is_shop == False:
            self.update_character_output("You can't seem to find a way to order anything here.")
            self.update_status(character.get_status())
            return
        if character.room.shop_filled == False:
            self.update_character_output("You will need to ORDER first.")
            self.update_status(character.get_status())
            return
        if character.room.shop.in_shop == False:
            self.update_character_output("You have exited the shop. You will need to ORDER again.")
            self.update_status(character.get_status())
            return 
        if character.get_dominant_hand_inv() is not None:
            self.update_character_output("You will need to empty your right hand first.")
            self.update_status(character.get_status())
            return
        self.action_result.update(character.room.shop.buy_item(number=kwargs['number_1']))
        if self.action_result['shop_item']['shop_item_flag']:
            try:
                character.set_dominant_hand_inv(self.action_result['shop_item']['shop_item'])
            except:
                print("WARNING: Shop did not deliver item")
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
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
            character.room.items.append(character.get_dominant_hand_inv())
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)     
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if world.world_map.tile_exists(x=character.location_x + 1, y=character.location_y, area=character.area):
            old_room = character.get_room()
            if old_room.shop_filled == True:
                if old_room.shop.in_shop == True:
                    old_room.shop.exit_shop()
            old_room_number = old_room.room_number 
            self.character.move_east()
            self.action_result.update(character.get_room().intro_text())
            self.update_room(character=character, old_room_number=old_room_number)
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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.room.is_shop == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return 
        if character.room.shop_filled == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return
        if character.room.shop.in_shop == False:
            self.update_character_output("You have nothing to exit.")
            self.update_status(character.get_status())
            return            
        else:
            self.action_result.update(character.room.shop.exit_shop())
            self.update_status(character.get_status())
            return

            
@DoActions.register_subclass('experience')
@DoActions.register_subclass('exp')
class Experience(DoActions):
    """\
    Displays your experience information.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)       

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if character.room.shop_filled == True:
            if character.room.shop.in_shop == True:
                character.room.shop.exit_shop()
        available_moves = character.room.adjacent_moves()
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
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
        for room_object in character.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                self.update_character_output("Perhaps picking up {} is not a good idea.".format(room_object.name))
                return
        if character.get_dominant_hand_inv() is None:
            item_found = False
            for room_item in character.room.items:
                if set(room_item.handle) & set(kwargs['direct_object']):
                    character.set_dominant_hand_inv(room_item)
                    character.room.items.remove(room_item)
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.check_round_time():
            return
        if character.is_dead():
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if not kwargs['direct_object']:
            self.update_character_output("Go where?")
            self.update_status(character.get_status())
            return
        for room_object in character.room.objects:
            if set(room_object.handle) & set(kwargs['direct_object']):
                self.update_character_output("You move toward {}.".format(room_object.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_object.name))
                self.action_result.update(room_object.go_object(character=character))
                return
        for room_item in character.room.items:
            if set(room_item.handle) & set(kwargs['direct_object']):
                self.update_character_output("You move toward {}.".format(room_item.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_item.name))
                self.update_status(character.get_status())
                return
        for room_npc in character.room.npcs:
            if set(room_npc.handle) & set(kwargs['direct_object']):
                self.update_character_output("You move toward {}.".format(room_npc.name))
                self.update_room_output("{} moves toward {}.".format(character.first_name, room_npc.name))
                self.update_status(character.get_status())
                return
        
@DoActions.register_subclass('health')
class Health(DoActions):
    """\
    HEALTH shows your current health attributes.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
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
        elif kwargs['subject_verb'] in DoActions.do_actions:
            self.update_character_output(DoActions.do_actions[kwargs['subject_verb']].__doc__)
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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.update_character_output('''
Name:  {} {}
Gender:  {}
Race:  {}
Profession:  {}
Level:  {}
            '''.format(character.first_name, character.last_name,
                       character.gender,
                       character.race,
                       character.profession,
                       character.level))
        self.update_status(character.get_status())
        return


@DoActions.register_subclass('inventory')
class Inventory(DoActions):
    """\
    INVENTORY allows you to view your inventory. It will list all items you have in your possession.  INVENTORY
    will not list the items within any containers you have.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
    
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == 'kneeling':
            self.update_character_output('You seem to already be kneeling.')
            self.update_status(character.get_status())
            return 
        else:
            character.position = 'kneeling'
            self.update_character_output(character_output_text="You move yourself to a kneeling position.")
            self.update_room_output(room_output_text="{} move {}self to a kneeling position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return
        
        
@DoActions.register_subclass('lie')
class Lie(DoActions):
    """\
    Moves you to a lying position on the ground. While many actions can be performed on the ground, 
    movement is not possible.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == 'lying':
            self.update_character_output('You seem to already be lying down.')
            self.update_status(character.get_status())
            return 
        else:
            character.position = 'lying'
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if kwargs['preposition'] == None:
            self.action_result.update(character.room.intro_text())
            self.update_status(character.get_status())
            return
        if kwargs['preposition'][0] == 'in':
            item_found = False
            if kwargs['indirect_object'] is None:
                self.update_character_output("I am not sure what you are referring to.")
                self.update_status(character.get_status())
                return
            for item in character.room.items + character.room.objects + character.room.npcs + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if isinstance(item, npcs.NPC):
                    self.update_character_output("It wouldn't be advisable to look in " + item.name)
                    self.update_status(character.get_status())
                    return
                if set(item.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(item.contents())
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
            for item in character.room.items + character.room.objects + character.room.npcs + character.room.enemies + character.inventory + [character.get_dominant_hand_inv()] + [character.get_non_dominant_hand_inv()]:
                if not item:
                    pass
                elif set(item.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(item.view_description())
                    self.update_status(character.get_status())
                    return
            for item in character.inventory:
                if set(item.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(item.view_description())
                    self.update_status(character.get_status())
                    return
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['indirect_object']):
                    self.action_result.update(object.view_description())
                    self.update_status(character.get_status())
                    return
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['indirect_object']):
                    self.update_character_output(npc.view_description())
                    self.update_status(character.get_status())
                    return
            for enemy in character.room.enemies:
                if set(npc.handle) & set(kwargs['indirect_object']):
                    self.update_character_output(enemy.view_description())
                    self.update_status(character.get_status())
                    return
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)      
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if world.world_map.tile_exists(x=character.location_x, y=character.location_y - 1, area=character.area):
            old_room = character.get_room()
            if old_room.shop_filled == True:
                if old_room.shop.in_shop == True:
                    old_room.shop.exit_shop()
            old_room_number = old_room.room_number 
            self.character.move_north()
            self.action_result.update(character.get_room().intro_text())
            self.update_room(character=character, old_room_number=old_room_number)
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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
         
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
            
        if character.room.is_shop == False:
            self.update_character_output("You can't seem to find a way to order anything here.")
            self.update_status(character.get_status())
            return 
        elif character.room.is_shop == True:  
            if character.room.shop_filled == False:             
                character.room.fill_shop()
                self.action_result.update(character.room.shop.enter_shop())
                return
            if character.room.shop.in_shop == False:
                self.action_result.update(character.room.shop.enter_shop())
                return
            self.action_result.update(character.room.shop.order_item(kwargs['number_1']))
            return

                

@DoActions.register_subclass('position')
@DoActions.register_subclass('pos')
class Position(DoActions):
    """\
    Displays the position you are currently in.\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.update_character_output('''You are currently in the {} position.'''.format(self.character.position))
        self.update_status(character.get_status())


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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
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
            for room_item in character.room.items:
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

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.update_character_output("You will need to find a way to exit the game.")


@DoActions.register_subclass('search')
class Search(DoActions):
    """\
    SEARCH allows you to explore your environment if the object, enemy, or area can be explored.

    Usage:
    SEARCH : Searches the environment around you and uncovers hidden items or objects.
    SEARCH <enemy> : Searches an enemy, uncovers any potential items that the enemy could be hiding, and places
    them in your environment.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        if not kwargs['direct_object']:
            items_found = 0
            for hidden_item in character.room.hidden:
                if 100 - character.level >= hidden_item.visibility:
                    character.room.add_item(hidden_item)
                    character.room.remove_hidden_item(hidden_item)
                    events.game_event('You found {}!'.format(hidden_item.name))
                    items_found += 1
            if items_found == 0:
                events.game_event("There doesn't seem to be anything around here.")
            return
        else:
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.search(character=character)
                    return
            for item in character.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    events.game_event("Searching {} will not do you much good.".format(item.name))
                    return
            for char in character.room.enemies + character.room.npcs:
                if set(char.handle) & set(kwargs['direct_object']):
                    events.game_event("{} probably will not appreciate that.".format(char.first_name))
                    return
            else:
                events.game_event("That doesn't seem to be around here.")
                return


@DoActions.register_subclass('sell')
class Sell(DoActions):
    """\
    SELL allows you to exchange items for gulden. Certain merchants look for items you may find in the wilds.
    Different merchants look for different items. The item must be in your right hand.

    Usage:
    SELL <item> to <npc>  : Exchanges items for gulden with an npc if an item can be exchanged.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if character.position == 'sitting':
            self.update_character_output(character_output_text="You seem to already be sitting.")
            self.update_status(status_text=character.get_status())
            return
        else:
            self.character.position = 'sitting'
            self.update_character_output(character_output_text="You move yourself to a sitting position.")
            self.update_room_output(room_output_text="{} moves {}self to a sitting position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('skills')
class Skills(DoActions):
    """\
    SKILLS displays the skills available to you as well as the skill rating for your character. Different skills
    allow you to accomplish different tasks.

    Usage:
    SKILLS:  Shows your available skills and their rating.
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        self.update_character_output(character_output_text='''
Edged Weapons:    {}  ({})          Shield:             {}  ({})
Blunt Weapons:    {}  ({})          Dodging:            {}  ({})
Polearm Weapons:  {}  ({})          Physical Fitness:   {}  ({})
Armor:            {}  ({})          Perception:         {}  ({})      
         
         

            '''.format(character.skills['edged_weapons'], character.skills_bonus['edged_weapons'],
                       character.skills['blunt_weapons'], character.skills_bonus['blunt_weapons'],
                       character.skills['polearm_weapons'], character.skills_bonus['polearm_weapons'],
                       character.skills['armor'], character.skills_bonus['armor'],
                       character.skills['shield'], character.skills_bonus['shield'],
                       character.skills['dodging'], character.skills_bonus['dodging'],
                       character.skills['physical_fitness'], character.skills_bonus['physical_fitness'],
                       character.skills['perception'], character.skills_bonus['perception'])
              )
        self.update_status(character.get_status())


@DoActions.register_subclass('skin')
class Skin(DoActions):
    """\
    Many enemies are able to be skinned for various pelts, hides, etc. The SKIN verb allows you to skin enemies.
    if successful the resulting item will be places within the environment. Not all enemies are able to be skinned.

    Usage:
    SKIN <enemy> : Skins an enemy and, if successful, leaves a skin.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if character.check_round_time():
            return
        if character.is_dead():
            return
        elif not kwargs['direct_object']:
            events.game_event("What are you trying to skin?")
            return
        else:
            for object in character.room.objects:
                if set(object.handle) & set(kwargs['direct_object']):
                    object.skin_corpse()
                    return
            for item in character.room.items:
                if set(item.handle) & set(kwargs['direct_object']):
                    events.game_event("You can seem to find any way to skin {}.".format(item.name))
                    return
            for npc in character.room.npcs:
                if set(npc.handle) & set(kwargs['direct_object']):
                    events.game_event("You approach {}, but think better of it.".format(npc.name))
                    return


@DoActions.register_subclass('south')
@DoActions.register_subclass('s')
class South(DoActions):
    """\
    Moves you south, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)        
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())            
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if world.world_map.tile_exists(x=character.location_x, y=character.location_y + 1, area=character.area):
            old_room = character.get_room()
            if old_room.shop_filled == True:
                if old_room.shop.in_shop == True:
                    old_room.shop.exit_shop()
            old_room_number = old_room.room_number 
            self.character.move_south()
            self.action_result.update(character.get_room().intro_text())
            self.update_room(character=character, old_room_number=old_room_number)
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
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
    offense
    forward
    neutral
    guarded
    defense\
    """
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        desired_stance=kwargs['adjective_1']

        if not desired_stance:
            self.update_character_output('''You are currently in the {} stance.'''.format(character.stance))
            self.update_status(character.get_status())
            return
        if set(desired_stance) & set(stances):
            character.stance = desired_stance[0]
            self.update_character_output('''You are now in {} stance.'''.format(desired_stance[0]))
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
    
    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)
        
        self.character = character
        
        self.stand(character=self.character)
        
    def stand(self, character):
        if self.character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if self.character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if self.character.position == 'standing':
            self.update_character_output(character_output_text="You seem to already be standing.")
            self.update_status(status_text=character.get_status())
            return
        else:
            self.character.position = 'standing'
            self.update_character_output(character_output_text="You raise yourself to a standing position.")
            self.update_room_output(room_output_text="{} raises {}self to a standing position.".format(character.first_name, character.possessive_pronoun))
            self.update_status(status_text=character.get_status())
            return


@DoActions.register_subclass('stats')
class Stats(DoActions):
    """\
    Displays your general statistics.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

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




@DoActions.register_subclass('target')
class Target(DoActions):
    """\
    When in combat, you must TARGET an enemy before you can ATTACK them. Use the TARGET verb to set the enemy
    for which you want to ATTACK. TARGET only needs to be set once for the duration of the combat. The enemy
    does not have to be within sight in order for you to TARGET it.

    Usage:
    TARGET <enemy> : Targets an enemy.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)

        if not kwargs['direct_object']:
            events.game_event("What do you want to target?")
            return
        else:
            character.target = kwargs['direct_object']
            events.game_event("You are now targeting {}".format(self.target[0]))
            return
        

@DoActions.register_subclass('west')
@DoActions.register_subclass('w')
class West(DoActions):
    """\
    Moves you west, if you can move in that direction.\
    """

    def __init__(self, character, **kwargs):
        DoActions.__init__(self, character, **kwargs)       
        
        if character.check_round_time():
            self.update_character_output(character_output_text="Round time remaining... {} seconds.".format(self.character.get_round_time()))
            self.update_status(character.get_status())
            return
        if character.is_dead():
            self.update_character_output(character_output_text="You're dead!")
            self.update_status(character.get_status())
            return
        if not character.check_position_to_move():
            self.update_character_output("You cannot move.  You are {}.".format(character.position))
            self.update_status(character.get_status())
            return
        if world.world_map.tile_exists(x=character.location_x - 1, y=character.location_y, area=character.area):
            old_room = character.get_room()
            if old_room.shop_filled == True:
                if old_room.shop.in_shop == True:
                    old_room.shop.exit_shop()
            old_room_number = old_room.room_number 
            self.character.move_west()
            self.action_result.update(character.get_room().intro_text())
            self.update_room(character=character, old_room_number=old_room_number)
            self.update_status(character.get_status())
            return
        else:
            self.update_character_output("You cannot find a way to move in that direction.")
            self.update_status(character.get_status())
            return



def do_enemy_action(action_input, enemy=None):
    action_history.insert(0,action_input)
    if not enemy:
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
    return EnemyAction.do_enemy_action(kwargs['action_verb'], enemy, **kwargs)


class EnemyAction:
    def __init__(self, enemy, **kwargs):
        self.enemy = enemy
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
            "status_output":  None
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
    def do_enemy_action(cls, action, enemy, **kwargs):
        """Method used to initiate an action"""
        if action not in cls.do_enemy_actions:
            cls.action_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.action_result
        return cls.do_enemy_actions[action](enemy, **kwargs).action_result

    def update_room(self, enemy, old_room_number):
        self.action_result['room_change']['room_change_flag'] = True
        self.action_result['room_change']['leave_room_text'] = enemy.text_move_out
        self.action_result['room_change']['old_room'] = old_room_number
        self.action_result['room_change']['new_room'] = enemy.get_room().room_number
        self.action_result['room_change']['enter_room_text'] = enemy.text_move_in
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


    def __str__(self):
        return "{}: {}".format(self.action, self.name)


@EnemyAction.register_subclass('spawn')
class Spawn(EnemyAction):
    def __init__(self, enemy, **kwargs):
        super().__init__(enemy=enemy,
                         kwargs=kwargs)
        self.enemy = enemy
        routes.enemy_spawn(enter_text=self.enemy.text_entrance, room_number=self.enemy.room.room_number)


@EnemyAction.register_subclass('east')
class MoveEastEnemy(EnemyAction):
    def __init__(self, enemy, **kwargs):
        super().__init__(enemy=enemy,
                         kwargs=kwargs)
        self.enemy = enemy

        if world.world_map.tile_exists(x=enemy.location_x + 1, y=enemy.location_y, area=enemy.area):
            old_room = self.enemy.get_room().room_number
            self.enemy.move_east()
            self.update_room(enemy=enemy, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('north')
class MoveNorthEnemy(EnemyAction):
    def __init__(self, enemy, **kwargs):
        super().__init__(enemy=enemy,
                         kwargs=kwargs)
        self.enemy = enemy

        if world.world_map.tile_exists(x=enemy.location_x, y=enemy.location_y - 1, area=enemy.area):
            old_room = self.enemy.get_room().room_number
            self.enemy.move_north()
            self.update_room(enemy=enemy, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('south')
class MoveSouthEnemy(EnemyAction):
    def __init__(self, enemy, **kwargs):
        super().__init__(enemy=enemy,
                         kwargs=kwargs)
        self.enemy = enemy

        if world.world_map.tile_exists(x=enemy.location_x, y=enemy.location_y + 1, area=enemy.area):
            old_room = self.enemy.get_room().room_number
            self.enemy.move_south()
            self.update_room(enemy=enemy, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return


@EnemyAction.register_subclass('west')
class MoveWestEnemy(EnemyAction):
    def __init__(self, enemy, **kwargs):
        super().__init__(enemy=enemy,
                         kwargs=kwargs)
        self.enemy = enemy

        if world.world_map.tile_exists(x=enemy.location_x - 1, y=enemy.location_y, area=enemy.area):
            old_room = self.enemy.get_room().room_number
            self.enemy.move_west()
            self.update_room(enemy=enemy, old_room_number=old_room)
            routes.enemy_event(action_result=self.action_result)
            return

