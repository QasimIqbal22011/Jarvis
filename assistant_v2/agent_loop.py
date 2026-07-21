from assistant_v2.parser import parse_response


class AgentLoop:

    def __init__(self, agent, executor):

        self.agent = agent
        self.executor = executor


    def run(self, conversation):

        max_steps = 10


        for _ in range(max_steps):

            raw = self.agent.think(
                conversation.get()
            )


            print(
                f"\nLLM -> {raw}"
            )


            if not raw:

                return (
                    "SAY:I did not receive a valid response."
                )


            kind, tool, payload = parse_response(
                raw
            )


            if kind == "SAY":

                return payload

            if kind == "ASK":
                return (
                    f"ASK:{payload}"
                )


            if kind == "ACTION":

                success, result = self.executor.execute(
                    tool,
                    payload
                )


                if success:

                    observation = (
                        "The computer action completed successfully.\n"
                        f"Tool: {tool}\n"
                        f"Result: {result}"
                    )

                else:

                    observation = (
                        "The computer action failed.\n"
                        f"Tool: {tool}\n"
                        f"Error: {result}"
                    )


                conversation.add_assistant(
                    {
                        "role": "assistant",
                        "content": raw
                    }
                )


                conversation.add_user(
                    observation
                )


                continue


            conversation.add_user(
                "Invalid response format. "
                "Only use SAY:, ASK:, or ACTION:."
            )


        return (
            "SAY:I could not complete the task."
        )