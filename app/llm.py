import uuid
import asyncio
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver



class VoiceAgent:
    """
    A voice-enabled agent that uses LangGraph to understand user commands
    and perform file operations using prebuilt tools.

    This class:
    - Maintains conversation context across voice interactions
    - Connects to a prebuilt ReAct agent from LangGraph
    - Sends user messages to the agent and handles its responses
    """

    def __init__(self):
        """
        Initialize the voice agent.

        Sets up:
        - An audio processor for voice I/O
        - A unique thread ID for stateful interaction
        - A LangGraph ReAct agent using built-in file tools
        """
        self.audio_processor = AudioProcessor()
        self.thread_id = str(uuid.uuid4())
        self.conversation_history = []

        # In-memory checkpointing for conversation state
        self.checkpointer = InMemorySaver()

        # Create the ReAct agent with LangGraph
        self.agent = create_react_agent(
            model="gpt-4.1-mini",
            tools=tools,
            checkpointer=self.checkpointer,
            prompt="""
            You are a helpful voice-enabled assistant specialized in file management. 
            You can list directories, read, write, copy, move, delete, and search for files. 
            Keep responses short and clear, since they will be spoken to the user. 
            Always acknowledge the command before executing it.
            """
        )

    async def process_user_input(self, user_message: HumanMessage):
        """
        Process a single user message and return the agent's response.

        Args:
            user_message (HumanMessage): A text message generated from the user's voice input.

        Returns:
            str: The agent's final text response.
        """
        try:
            # Add the incoming message to the conversation history
            self.conversation_history.append(user_message)

            # Use a unique thread ID for conversation continuity
            config = {"thread_id": self.thread_id}
            thread_config = {"configurable": config}

            # Send the message to the agent and get the full response trace
            response = await self.agent.ainvoke(
                {"messages": self.conversation_history},
                config=thread_config
            )

            # Get the last message as the final response
            final_response = response["messages"][-1].content
            self.conversation_history.append(response["messages"][-1])
            return final_response

        except Exception as e:
            error_message = f"I encountered an error: {str(e)}"
            print(error_message)
            return error_message