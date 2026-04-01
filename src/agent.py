from colorama import Fore, init
from litellm import completion
import litellm
import time
import random

# Initialize colorama for colored terminal output
init(autoreset=True)


class Agent:
    """
    @title AI Agent Class
    @notice This class defines a simple AI agent with no function calling capabilities
    """

    def __init__(self, name, model, system_prompt="", temperature=0.1):
        """
        @notice Initializes the Agent class.
        @param model The AI model to be used for generating responses.
        @param tools A list of tools that the agent can use.
        @param available_tools A dictionary of available tools and their corresponding functions.
        @param system_prompt system prompt for agent behaviour.
        """
        self.name = name
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt

    def invoke(self, message, max_retries=3, base_delay=5):
        """
        @notice Invokes the AI agent with retry logic for API errors.
        @param message The message to send to the agent.
        @param max_retries Maximum number of retry attempts.
        @param base_delay Base delay in seconds for exponential backoff.
        @return The AI response content.
        """
        print(Fore.GREEN + f"\nCalling Agent: {self.name}")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        for attempt in range(max_retries + 1):
            try:
                response = completion(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
                
            except (litellm.InternalServerError, litellm.RateLimitError, litellm.APIError) as e:
                if attempt == max_retries:
                    print(Fore.RED + f"❌ Agent {self.name} failed after {max_retries + 1} attempts: {str(e)}")
                    raise e
                
                # Calculate delay with exponential backoff and jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(Fore.YELLOW + f"⚠️  Agent {self.name} attempt {attempt + 1} failed: {str(e)}")
                print(Fore.CYAN + f"⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                
            except Exception as e:
                # For unexpected errors, don't retry
                print(Fore.RED + f"❌ Unexpected error in Agent {self.name}: {str(e)}")
                raise e

