
import time as time
import textwrap as textwrap

from app.main import mixins, items, config, quests


wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)

all_items_categories = mixins.items


def create_npc(npc_category, npc_name, **kwargs):
    return NPC.new_npc(npc_category.title().replace(" ",""), npc_name, **kwargs)


class NPC(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, npc_name: str, character: object, room: object, **kwargs):
        super(NPC, self).__init__()

        self.npc_data = self.get_npc_by_name(npc_name)

        if self.npc_data['gender'] == "female":
            self.object_pronoun = "She"
            self.possessive_pronoun = "Her"
        if self.npc_data['gender'] == "male":
            self.object_pronoun = "He"
            self.possessive_pronoun = "His"

        self.name = self.npc_data['name']
        self.first_name = self.npc_data['first_name']
        self.last_name = self.npc_data['last_name']
        self.description = self.npc_data['description']
        self.handle = self.npc_data['handle']
        self.adjectives = self.npc_data['adjectives']
        self.spawn_location = self.npc_data['spawn_location']
        self.entrance_text = self.npc_data['entrance_text']
        self.right_hand_inv = self.npc_data['right_hand']
        self.left_hand_inv = self.npc_data['left_hand']

        self.character = character
        self.room = room

        self.inventory = []

        for category in self.npc_data['inventory']:
            for item_handle in self.npc_data['inventory'][category]:
                try:
                    print(item_handle)
                    print(items.create_item(item_category=category, item_name=item_handle).name)
                    self.inventory.append(items.create_item(item_category=category, item_name=item_handle))
                except:
                    print("WARNING:  Could not create " + item_handle + " for " + self.name + " in " + self.room.room_name)

    def view_description(self):
        if len(self.right_hand_inv) == 1:
            right_hand = "{} has {} in {} right hand.".format(self.first_name, self.right_hand_inv[0], self.object_pronoun.lower())
        else:
            right_hand = "{} right hand is empty.".format(self.possessive_pronoun)
        if len(self.left_hand_inv) == 1:
            left_hand = "{} has {} in {} left hand.".format(self.first_name, self.left_hand_inv[0], self.object_pronoun.lower())
        else:
            left_hand = "{} left hand is empty.".format(self.possessive_pronoun)
        if len(self.inventory) == 0:
                inventory_clothing = "{} is not wearing anything.".format(self.object_pronoun)
        inventory_clothing = [x.name for x in self.inventory if x.category == 'Clothing']
        if len(inventory_clothing) > 1:
            inventory_clothing = "{} is wearing {} and {}.".format(self.object_pronoun, ', '.join(inventory_clothing[:-1]), inventory_clothing[-1])
        elif len(inventory_clothing) == 1:
            inventory_clothing = "{} is wearing {}.".format(self.object_pronoun, inventory_clothing[0])
        else:
            inventory_clothing = "{} is wearing nothing.".format(self.object_pronoun)
        inventory_armor = [x.name for x in self.inventory if x.category == 'Armor']
        if len(inventory_armor) > 1:
            inventory_armor ="{} is also wearing {} and {}.".format(self.object_pronoun, ', '.join(inventory_armor[:-1]), inventory_armor[-1])
        elif len(inventory_armor) == 1:
            inventory_armor = "{} is also wearing {}.".format(self.object_pronoun, inventory_armor[0])
        else:
            inventory_armor = "{} is also wearing no armor.".format(self.object_pronoun)
        events.game_event('''\
{}
{}
{}
{}
{}
                        \
                        '''.format(right_hand,
                                   left_hand,
                                   wrapper.fill(self.description),
                                   wrapper.fill(inventory_clothing),
                                   wrapper.fill(inventory_armor)))

    def intro_text(self):
        return self.entrance_text

    def ask_about(self,object):
        NotImplementedError()

    def run(self):
        NotImplementedError()

    def give_item(self, item):
        NotImplementedError()
        
    npc_categories = {}
    
    @classmethod
    def register_subclass(cls, npc_category):
        """Catalogues npcs in a dictionary for reference purposes"""
        def decorator(subclass):
            cls.npc_categories[npc_category] = subclass
            return subclass
        return decorator
    
    @classmethod
    def new_npc(cls, npc_category, npc_name, **kwargs):
        """Method used to initiate an npc"""
        if npc_category not in cls.npc_categories:
            events.game_event("I am sorry, I did not understand.")
            return
        return cls.npc_categories[npc_category](npc_name, **kwargs)


@NPC.register_subclass('SanndRedra')
class SanndRedra(NPC):
    def __init__(self, npc_name: str, character: object, room: object, **kwargs):
        super().__init__(npc_name=npc_name, character=character, room=room, **kwargs)

    def ask_about(self, object):
        pass

    def give_item(self, item):
        pass

    def run(self):
        time.sleep(1)
        while self.character.room != self.room:
            time.sleep(1)
        self.room.add_npc(self)
        self.room.remove_hidden_npc(self)
        # if not self.character.check_quest(quest=self.quests['the_first_quest']):
        #     self.character.add_quest(quest_name='the_first_quest', quest=self.quests['the_first_quest'])
        # if self.character.room == self.room and self.character.quests['the_first_quest'].steps_complete['step_1'] == False:
        #     self.character.set_round_time(seconds=13)
        #     print(wrapper.fill(self.intro_text()))
        events.game_event('''\
{} says, 'Hey {}, how have you been?!"\
            '''.format(self.first_name, self.character.first_name))
#             time.sleep(3)
#             print('''\
# {} continues, "I'm glad I caught you. Gander wants to see you. He says he needs some help."\
#             '''.format(self.first_name))
#             time.sleep(5)
#             print('''\
# In an agreeable tone, He says, "I think he's in his shop right now, on the north end of town. You know he loves his
# work. He said something about needing something for shipment. I'm not exactly sure, you'll have to talk to him."\
#             ''')
#             time.sleep(5)
#             print('''\
# He chuckles and says, "That's all I have for you. Hopefully you find him and can help him. I'll see you around."\
#             ''')
#             print('''\
# Sannd waves and heads back over to his group to continues his previous conversation.\
#             ''')
#         elif self.character.room == self.room and self.character.quests['the_first_quest'].quest_complete == False:
#             self.character.set_round_time(seconds=9)
#             print(wrapper.fill(self.intro_text()))
#             print('''\
# {} says, "Hey {}, how have you been?!"\
#             '''.format(self.first_name, self.character.first_name))
#             time.sleep(3)
#             print('''\
# "Have you been up to see Gander? He's been looking for you."\
#             ''')
#             print('''\
# You mention you've stopped by that he's set you out on one of his tasks. You also mention your reluctance, but that
# you'll do it anyway.\
#             ''')
#             time.sleep(4)
#             print('''\
# "Oh whew! That's one less thing I have to remember."\
#             ''')
#             time.sleep(2)
#             print('''\
# He continues, "Well, you've probably got to get a start, so I'll leave you alone. Good luck and just holler if you
# need anything."\
#             ''')
#             print('''\
# Sannd waves and heads back over to his group to continue his previous conversation.\
#             ''')
#         else:
#             print(wrapper.fill(self.intro_text()))
#             print('''\
#             {} says, "Hey {}, how have you been?!"\
#                         '''.format(self.first_name, self.character.first_name))
#             time.sleep(3)
#             print('''\
# Sannd waves and heads back over to his group to continues his previous conversation.\
#                         ''')
        return


@NPC.register_subclass('GanderDiggle')
class GanderDiggle(NPC):
    def __init__(self, npc_name: str, character: object, room: object, **kwargs):
        super().__init__(npc_name=npc_name, character=character, room=room, **kwargs)

    def sell_item(self, item):
        events.game_event("""\
Gander takes {} and gives it a quizzitive look.\
        """.format(item.name))

        if not isinstance(item, items.Skin):
            events.game_event("""\
"Why did you bring this to me? I have no use for it, unfortunately."
Gander hands you back {}.
            """.format(item.name))
            return False

        if item.value == 0:
            events.game_event("""\
He quickly returns it to you, mutters something under his breath, and shakes his head. "This is worth nothing to me."\
            """)
            return False

        events.game_event("""\
Gander smiles. "Thank you for finding this. I can definitely put it to use."
He gives you {} gulden which you quickly pocket.\
        """.format(item.name, item.value))
        self.character.money = self.character.money + item.value
        return True

    def ask_about(self, object):
#         if set(object) & {"job", "task"}:
#             if not self.character.check_quest(quest=self.quests['the_first_quest']):
#                 print("""\
# Gander looks you up and down. "Did someone tell you to come to me? No? Then I can't help you unfortunately."\
#                 """)
#                 return
#             self.quest01_step1()
#         else:
            events.game_event("""\
Gander glances quickly at you and raises an eyebrow. "I'm not sure what you're talking about."\
            """)

    def give_item(self, item):
#         if item.handle[0] != "hide":
#             print('''\
# {} takes one look at {} and says, "What is this? What do you expect me to do with this?" {} shakes {} head and
# walks away from your offer.\
#                 '''.format(self.first_name, item.name, self.object_pronoun, self.possessive_pronoun))
#         else:
#             if not self.character.check_quest(quest=self.quests['the_first_quest']):
                events.game_event("""\
Gander looks you up and down. "Did someone tell you to come to me? No? Then I can't help you unfortunately."\
                            """)
                return
            # self.quest01_step2(item=item)
            # return False

    def quest01_step1(self):
        pass
#         if self.character.quests['the_first_quest'].steps_complete['step_1'] == False:
#             print('''\
# {} says, "Oh yes, now I remember. I was trying to finish this project over here."\
#                         '''.format(self.first_name))
#             print('''\
# {} shuffles over to the corner of the room and picks up an unfinished vest.\
#                         '''.format(self.first_name))
#             time.sleep(6)
#             print('''\
# {} says, "It's supposed to be a cuirass, but I ran out of boar hide to complete it."\
#                         '''.format(self.object_pronoun))
#             print('''\
# {} fumbles with the cuirass and eventually slops it on the table.\
#                         '''.format(self.object_pronoun))
#             time.sleep(6)
#             print('''\
# {} continues, "Do you think you could help me get the rest of the materials to complete it? As I recall, and my memory
# doesn't serve me well these days, I believe there may be some wild boar still roaming the forests east of town. I need
# you to go out there, kill one, and bring back the hide."\
#                         '''.format(self.first_name))
#             print('''\
# {} turns and tosses the cuirass on a back table. It lands with a flat thump.\
#                         '''.format(self.first_name))
#             time.sleep(7)
#             print('''\
# {} examines you for a brief second and says, "Yeah, you look capable enough. You should be able to take down a boar
# no problem."\
#                         '''.format(self.object_pronoun))
#             print('''\
# {} squints his eyes and peers down at your hands.\
#                         '''.format(self.object_pronoun))
#             time.sleep(2)
#             if isinstance(self.character.right_hand_inv, items.Weapon):
#                 print('''\
# {} looks up and says, "Yeah, I suppose {} will do."\
#                             '''.format(self.object_pronoun, self.character.right_hand_inv.name))
#             elif isinstance(self.character.left_hand_inv, items.Weapon):
#                 print('''\
# {} looks up and says, "Yeah, I suppose {} will do."\
#                             '''.format(self.object_pronoun, self.character.left_hand_inv.name))
#             else:
#                 print('''\
# {} looks up and says, "You may want to grab yourself a weapon, though."\
#                             '''.format(self.object_pronoun))
#             time.sleep(4)
#             print('''\
# Without waiting for a response, {} continues, 'Now hurry along and come back when you have a hide. I don't have all
# day you know."\
#                         '''.format(self.first_name))
#             self.character.quests["the_first_quest"].steps_complete['step_1'] = True
#             return
#         print('''\
# Gander look at you incredulously.
# "What are you waiting around for?  This cuirass isn't going to finish itself."
# Gander shuffles away, shaking his head.\
#                 ''')

    def quest01_step2(self, item):
        pass
#         if self.character.quests['the_first_quest'].steps_complete['step_2'] == False:
#             self.character.set_round_time(12)
#             print('''\
# Gander's eyes light up as he peers down at your {}. "This is exactly what I'm looking for.  And it looks to be in
# great condition. You've done well for yourself."
# He grabs the hide, holds it up to the examination light and begins examining every inch. After a few moments, he
# turns and is startled to still see you standing there.
# "You're probably looking for something, aren't ya? You would think this younger generation would be satisfied
# with simply helping out an old man."\
#                 '''.format(item.name))
#             time.sleep(10)
#             print('''\
# {} shakes his head and looks over his workbench. He nods as his gaze fixates on an object at the end of the bench.
# "Here, this ought to hold you for now. Who knows, you might even be able to put it to good use."
# He reaches over and picks up a pair of light leather arm greaves and tosses them your direction. You jerk to the left
# and stretch out your hand to grab the poorly thrown greaves. They are heavier than you expect, but you scoop them
# out of the air without trouble. You smile at Gander and nod in gratitude.
# "Yeah, yeah, yeah. Just don't go telling everyone I'm giving things away." With that, he gets back to his current
# project.\
#                 '''.format(self.first_name))
#             self.character.right_hand_inv = items.Armor(item_name="leather_arm_greaves")
#             self.character.quests['the_first_quest'].steps_complete['step_3'] = True
#             self.character.quests['the_first_quest'].quest_complete = True
#             time.sleep(2)
#             print(self.character.quests['the_first_quest'].quest_complete_text)
#             return
#
#         if self.character.quests['the_first_quest'].steps_complete['step_3'] == True:
#             print("""\
# Gander rants, 'Haven't you gotten enough from me?'
# He shakes his head and walks away.\
#                                     """)
#         return

    def run(self):
        time.sleep(2)
        events.game_event(wrapper.fill(self.intro_text()))
        

@NPC.register_subclass('EmmeraSadana')        
class EmmeraSadana(NPC):
    def __init__(self, npc_name: str, character: object, room: object, **kwargs):
        super().__init__(npc_name=npc_name, character=character, room=room, **kwargs)

    def ask_about(self, object):
        pass

    def give_item(self, item):
        pass

    def quest02_step1(self):
        pass
#         self.character.set_round_time(seconds=30)
#         time.sleep(2)
#         print('''\
# As you approach the old tree, you hear some voices. You peer around the trunk of the tree to you get a glimpse of
# the source of the voices on the other side. What you find surprises you. There is a short, stout man that you
# recognize from town standing opposite a woman that you most definitely do not recognize. She would stand out in
# any part of town. She is dressed in dazzlingly clean, metal armor covering her shoulders, arms, and neck. Her clothing
# under her armor is black with the exception of her boots, which are a dark brown leather. Her brown hair drops to
# the middle of her back and lightly blows in the wind. She stands more upright than you see from most people. Her
# motions are purposeful and direct. She doesn't appear to waste any energy with her movements.\
#                         ''')
#         time.sleep(15)
#         print('''\
# You gradually step closer to the conversation they are having, but make a point to stay out of view behind the tree.
# The voice of the short man is timid and fearful, while the woman's voice has a noble tone.
# "...but I don't understand," {} says.
# "Madam, we.. uh.. we don't have a 'king'. We have an assembly of matrons that decides for our town. And..."
# "Well then, can you take me to the head matron?"
# "I... I don't think they are available. You see, it's... a waxing moon and..."
# "When will they be available?" the armored woman interrupted.
# The stout man seemed to shy away.
# "Do you not know, or will you not tell me?" said the woman.
# "I... um, I think I need to go now," the man pleaded. "You may... you may want to try the town guards. They're
# usually pretty knowledgeable about these things."\
#                         '''.format(self.first_name))
#         time.sleep(15)
#         print('''\
# With that the man turned and scuttled south following the wall, and turning west around the corner.
# The woman, keeping her upright posture, sunk her head in thought as the man ran away. She peered up into the sky
# and blinked, as if looking for something in particular. Not finding it there, she started south, following the short
# man's footsteps.
# As she was striding through the grass, you notice a small piece of parchment wisp out of her pocket, carried bythe wind.
# The parchment swirls right and left before landing a few strides behind the woman. Not noticing what she
# dropped, she continued south out of sight.
# You emerge from behind the tree and start toward the parchment, but you couldn't quite see where it landed.\
#                         ''')
#         self.room.add_hidden_item(items.Miscellaneous(item_name='emmera_message'))
#         self.room.remove_npc(npc=self)

    def quest02_voices(self):
        pass
#         messages = ['''\
#         A faint voice suddenly becomes very sharp, "Psst, {}. over here."\
#                                 '''.format(self.character.first_name),
#                     '''\
# You hear a faint, echoed voice. You can't point you finger on the source.\
#                 ''',
#                     '''\
# An voice fades in and and out of your attention. You circle to see if someone is following you, but you do not find
# anything.\
#                 ''',
#                     '''\
# Silently, and with slight whisps, a voice speaks to you, "You are more than this town. Go to where the streets end
# and wait.
# You will find me there."\
#                 ''',
#                     '''\
# Whispers become louder and softer, almost in unison. You become slightly paranoid at the effect.\
#                 ''']
#         message_select = random.randint(0, 4)
#         print(messages[message_select])


    def quest02_step2(self):
        pass
#         print('''\
# As you pan around the cul de sac, something seems off. The crates and the refuse do not appear out of place, however
# you have the feeling you have entering the cul de sac being trailed. The message you picked up from outside the gates begins
# to eminate heat.
#
# Suddenly, and without warning, the space between you and the crates bulges as if someone placed a massive magnifying
# glass in your field of vision. As the distortion increases, it quickly disolves into the form of a human figure.
# The shape of armor quickly becomes apparent and you realize that the woman you saw outside the gates is appearing out
# of thin air in front of you.
#
# Emmera approaches you, and you see that her presence is more formidable from this perspective than when you saw her
# by the old tree. She gazes at you and with every stride, you feel less and less confident. She comes within several
# paces and squares you off.
# \
#                     ''')
#         time.sleep(10)
#         print('''\
# "{}," she says.
#
# "It is you I've been looking for," she says with a sound of satisfaction.
#
# You contort your face to show your confusion, but before you can say anything Emmera interrupts, "The parchment you
# found. It is a message for you, and you alone. You must read it when you are ready. Only you will know when you are
# ready."
#
# Instinctually, you reach for the message. As your skin makes contact with the paper, it sends
# a jolt of shock through your system. You get a sudden flash of images through your field of vision. Mountains rush
# before your eyes dotted with towers stretching to the sky and piercing the clouds. They are quickly replaced by islands,
# both desolate and lush, populating tropical waters full of colorful reefs and fish. Just as quickly, the islands blur
# and a thick, dark forest comes into view. Images replace images, all wonderous and grand. You are quickly overwhelmed
# and drop the parchment. The scene reverts back to the cul de sac with Emmera sitting in the center.
#
# Emmera hesitates for a moment, letting you breath in what just happened.
# \
#                     '''.format(self.character.first_name))
#         time.sleep(10)
#         print('''\
# After a few seconds she says, "I understand this must be a little overwhelming, but you must listen. You have never
# met me and I have never met you.  However, this town is where my guides have led me, and they have told me to look
# for the one that would take us into the next age. I did not believe it myself when I was told of my quest, but I
# cannot argue with Determiners. They have led me here and they have led me to you. Looking at you, I cannot understand
# what they see. But it is their will."
#
# Emmera looks over your shoulder as if she sensed someone was entering the cul de sac an interrupting your
# conversaion. She dismisses her thought and continues, "Look, I know that this is tough to hear, but you must believe
# me. I am the protector of Dion. I am trusted by our highest authority to keep the kingdom safe. And it is in this
# bound duty that I am here talking to you."
# \
#                     ''')
#         time.sleep(10)
#         print('''\
# "Please. Take the message and hold it with you. Keep it safe. Keep it quiet. And do not reveal it to anyone you do not
# trust. It is now yours." Emmera gives you a look as if she has done her duty.
#
# She looks into your eyes, penetrating your soul. You have no choice but to look back and, through the locked gaze,
# you understand the gravity of Emmera's words. You slowly realize your life is about to change, either for the better
# or for the worse.
#
# Emmera, looking suddenly fearful, says, " I must be going now. I'm sorry, but I hope you will
# understand." Without warning, she begins to desolve back into the bubble from which she appeared. You reach out,
# hoping to pull her back from her disappearance, but your hand moves through what's left of the distortion without
# any resistance.
#
# Within seconds, you find yourself alone in the cul de sac. You look around, and everything was just the same as
# it was before. You aren't sure whether to open the message yet, or keep it for later, but what you are fairly
# certain of is that this is a defining moment your life.\
#                             '''.format(self.character.first_name))
#
#         time.sleep(10)
#         print("""\
# Congratulations. You have completed the Prologue of Dion. You are free to explore the environment and interact as you
# please.\
#                             """)
#         self.character.quests['prologue'].steps_complete['step_2'] = True
#         self.character.quests['prologue'].quest_complete = True


    def run(self):
        pass
        # if not self.character.check_quest(quest=self.quests['prologue']):
        #     self.character.add_quest(quest_name='prologue', quest=self.quests['prologue'])
        # self.room.add_npc(npc=self)
        # self.room.remove_hidden_npc(npc=self)
        # while self.character.room != self.room:
        #     time.sleep(0.2)
        # self.quest02_step1()
        # while self.character.quests['prologue'].steps_complete['step_1'] == False:
        #     time.sleep(5)
        #     if self.character.check_inventory_for_item(item=items.Miscellaneous(item_name="emmera_message")):
        #         self.character.quests['prologue'].steps_complete['step_1'] = True
        # while self.character.quests['prologue'].steps_complete['step_2'] == False:
        #     time.sleep(30)
        #     if self.character.quests['the_first_quest'].quest_complete == True:
        #         self.quest02_voices()
        #         if (self.character.room.room_name == "Cul De Sac") and (
        #                 self.character.check_inventory_for_item(item=items.Miscellaneous(item_name="emmera_message"))):
        #             self.character.room.add_npc(self)
        #             self.quest02_step2()


@NPC.register_subclass('DochasTownGuard')
class DochasTownGuard(NPC):
    def __init__(self, npc_name: str, character: object, room: object, **kwargs):
        super().__init__(npc_name=npc_name, character=character, room=room, **kwargs)

    def ask_about(self, object):
        pass

    def give_item(self, item):
        pass














