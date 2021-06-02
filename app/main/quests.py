
"""


"""

import threading as threading

from app.main import mixins


class Quest(mixins.DataFileMixin, mixins.ReprMixin, threading.Thread):
    def __init__(self, quest_name: str, **kwargs):
        super(Quest, self).__init__()

        self.quest_data = self.get_quest_by_name(name=quest_name)

        self.name = self.quest_data['name']
        self.description = self.quest_data['description']
        self.handle = self.quest_data['handle']
        self.adjectives = self.quest_data['adjectives']
        self.steps_description = self.quest_data['steps_description']
        self.steps_complete = self.quest_data['steps_complete']
        self.quest_complete = self.quest_data['quest_complete']
        self.quest_complete_text = self.quest_data['quest_complete_text']
        self.reward = self.quest_data['reward']

    def set_character(self, character):
        self.character = character

    def run(self):
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        state = state['quest_data']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def save(self):
        save_data = self.__getstate__()
        return save_data

    def load(self, state):
        self.__setstate__(state)
