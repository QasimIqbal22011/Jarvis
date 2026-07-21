from assistant_v2.state import AssistantState


class StateManager:

    def __init__(self, events=None):

        self.state = AssistantState.IDLE
        self.events = events


    def set(self, state):

        self.state = state

        print(f"[STATE] {state.value}")

        if self.events:

            self.events.emit(
                "state_changed",
                state
            )


    def get(self):

        return self.state