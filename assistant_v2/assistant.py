from assistant_v2.agent import Agent
from assistant_v2.memory import Conversation
from assistant_v2.prompts import SYSTEM_PROMPT
from assistant_v2.router import ToolRegistry
from assistant_v2.tools.actions import register_tools
from assistant_v2.executor import ToolExecutor
from assistant_v2.agent_loop import AgentLoop
from assistant_v2.state_manager import StateManager
from assistant_v2.state import AssistantState
from assistant_v2.events import EventBus


class Assistant:

    def __init__(self):

        self.agent = Agent()

        self.conversation = Conversation()

        self.tools = ToolRegistry()

        register_tools(
            self.tools
        )

        self.executor = ToolExecutor(
            self.tools
        )

        self.loop = AgentLoop(
            self.agent,
            self.executor,
        )

        self.conversation.add_system(
            SYSTEM_PROMPT
        )

        self.events = EventBus()

        self.state = StateManager(
            self.events
        )


    def think(self, text):

        self.state.set(
            AssistantState.THINKING
        )

        self.conversation.add_user(
            text
        )

        reply = self.loop.run(
            self.conversation
        )

        if not reply:

            reply = (
                "SAY:I did not receive a response."
            )

        self.conversation.add_assistant(
            reply
        )

        self.conversation.trim()

        self.state.set(
            AssistantState.IDLE
        )

        return reply