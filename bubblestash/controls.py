class KeyboardInputHandler(object):

    def __init__(self, key_map):
        self.key_map = key_map
        self._key_states = {}

    def key_down(self, target):
        return self._key_states.setdefault(target, False)

    def on_key_press(self, symbol, modifiers):
        action = self.key_map.get(symbol)
        if action is not None:
            self.set_on(action)

    def on_key_release(self, symbol, modifiers):
        action = self.key_map.get(symbol)
        if action is not None:
            self.set_off(action)

    def set_on(self, target):
        self._key_states[target] = True

    def set_off(self, target):
        self._key_states[target] = False
