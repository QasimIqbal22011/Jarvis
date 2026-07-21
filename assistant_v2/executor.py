class ToolExecutor:

    def __init__(self, registry):

        self.registry = registry


    def execute(self, tool_name, payload):

        if not tool_name:

            return (
                False,
                "No tool specified."
            )


        tool_name = (
            tool_name
            .strip()
            .lower()
        )


        args = []


        if payload:

            args = [
                arg.strip()
                for arg in payload.split("|")
                if arg.strip()
            ]


        print(
            f"[TOOL] {tool_name} -> {args}"
        )


        try:

            return self.registry.execute(
                tool_name,
                *args
            )

        except Exception as e:

            return (
                False,
                str(e)
            )