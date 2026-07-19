class CommandRouter:

    def __init__(self, actions):
        self.actions = actions

    def execute(self, action_name, payload):
        args = payload.split("|")

        action = self.actions.get(action_name)

        if action is None:
            return False, f"Unknown action: {action_name}"

        try:
            result = action(args)
            return True, result
        except Exception as e:
            return False, str(e)