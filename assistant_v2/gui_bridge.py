from assistant_v2.state import AssistantState

import gui


class GUIBridge:


    def __init__(self, events):

        self.events = events
        self.enabled = True

        self.events.subscribe(
            self.handle_event
        )


    def disable(self):

        self.enabled = False



    def safe_call(self, function, *args):

        if not self.enabled:
            return


        try:

            function(*args)

        except Exception as e:

            print(
                f"[GUI ERROR] {e}"
            )

            self.enabled = False



    def handle_event(self, event, data):

        if not self.enabled:
            return



        if event == "state_changed":

            self.update_state(
                data
            )



        elif event == "message":

            sender, text = data

            self.safe_call(
                gui.add_message,
                sender,
                text
            )



        elif event == "audio_level":

            self.safe_call(
                gui.set_audio_level,
                data
            )



    def update_state(self, state):

        if state == AssistantState.IDLE:

            self.safe_call(
                gui.set_state,
                "idle"
            )


        elif state == AssistantState.LISTENING:

            self.safe_call(
                gui.set_state,
                "listening"
            )


        elif state == AssistantState.THINKING:

            self.safe_call(
                gui.set_state,
                "thinking"
            )


        elif state == AssistantState.EXECUTING:

            self.safe_call(
                gui.set_state,
                "executing"
            )


        elif state == AssistantState.SPEAKING:

            self.safe_call(
                gui.set_state,
                "speaking"
            )