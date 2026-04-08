import os
import requests
import time
import random
from colorama import Fore, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# LM Studio API configuration
LM_STUDIO_API_BASE = os.environ.get("LM_STUDIO_API_BASE", "http://localhost:1234/v1")


class Agent:
    """
    @title AI Agent Class
    @notice This class defines a simple AI agent that calls a local LM Studio server
            via its OpenAI-compatible API.
    """

    def __init__(self, name, model, system_prompt="", temperature=0.1, enable_thinking=False):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.enable_thinking = enable_thinking
        self.api_base = LM_STUDIO_API_BASE

    def invoke(self, message, max_retries=3, base_delay=3):
        """
        @notice Invokes the AI agent with retry logic.
        @param message The message to send to the agent.
        @param max_retries Maximum number of retry attempts.
        @param base_delay Base delay in seconds for exponential backoff.
        @return The AI response content.
        """
        print(Fore.GREEN + f"\nCalling Agent: {self.name}")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": self.temperature,
            "stream": False,
            "extra_body": {
                "chat_template_kwargs": {
                    "enable_thinking": self.enable_thinking,
                }
            }
        }

        url = f"{self.api_base}/chat/completions"

        for attempt in range(max_retries + 1):
            try:
                resp = requests.post(url, json=payload, timeout=600)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]

            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt == max_retries:
                    print(Fore.RED + f"❌ Agent {self.name} failed after {max_retries + 1} attempts: {str(e)}")
                    raise e
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(Fore.YELLOW + f"⚠️  Agent {self.name} attempt {attempt + 1} failed: {str(e)}")
                print(Fore.CYAN + f"⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)

            except requests.HTTPError as e:
                if attempt == max_retries:
                    print(Fore.RED + f"❌ Agent {self.name} failed after {max_retries + 1} attempts: {str(e)}")
                    raise e
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(Fore.YELLOW + f"⚠️  Agent {self.name} attempt {attempt + 1} failed (HTTP {resp.status_code}): {str(e)}")
                print(Fore.CYAN + f"⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)

            except Exception as e:
                print(Fore.RED + f"❌ Unexpected error in Agent {self.name}: {str(e)}")
                raise e

