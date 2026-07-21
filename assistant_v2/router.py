class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def exists(self, name):
        return name in self.tools

    def list_tools(self):
        return sorted(self.tools.keys())

    def execute(self, name, *args):

        func = self.tools.get(name)

        if func is None:
            return False, f"Unknown tool: {name}"

        try:
            result = func(*args)
            return True, result

        except Exception as e:
            return False, str(e)