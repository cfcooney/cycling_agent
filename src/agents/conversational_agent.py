import os
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from langchain.agents import create_agent

from ..models.azure_openai_models import get_azure_openai_model
from ..tools.tools import find_bike_rentals, get_weather_now, get_weather_forecast
from ..prompts.system_prompt import agent_system_prompt, advanced_agent_system_prompt

load_dotenv()


class ConversationalCyclingAgent:
    """
    A conversational cycling assistant that maintains chat history and provides
    an interactive command-line interface for cycling-related queries.
    """
    
    def __init__(self, model_provider: str = "azure_openai"):
        """
        Initialize the conversational cycling agent.
        
        Args:
            model_provider: The model provider to use ("azure_openai", "anthropic", etc.)
        """
        self.console = Console()
        self.model_provider = model_provider
        self.history = InMemoryHistory()
        self.conversation_history = []
        
        # Initialize model and agent
        self.model = self._get_model(model_provider)
        self.agent = self._create_agent()
        
    def _get_model(self, provider: str):
        """
        Factory method to get different model providers.
        
        Args:
            provider: The model provider name
            
        Returns:
            The initialized model instance
        """
        if provider == "azure_openai":
            return get_azure_openai_model(os.getenv("MODEL", "gpt-4o-mini"))
        elif provider == "anthropic":
            # Future implementation
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(model="claude-3-sonnet-20240229")
            except ImportError:
                raise ImportError("Install langchain-anthropic to use Anthropic models")
        elif provider == "google":
            # Future implementation
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(model="gemini-pro")
            except ImportError:
                raise ImportError("Install langchain-google-genai to use Google models")
        elif provider == "ollama":
            try:
                from ..models.open_source_models import get_ollama_model
                # Use a function-calling compatible model by default
                model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
                return get_ollama_model(model_name, chat=True)
            except ImportError:
                raise ImportError("Install langchain-ollama to use Ollama models: pip install langchain-ollama")

        else:
            raise ValueError(f"Unsupported model provider: {provider}")
    
    def _create_agent(self):
        """
        Create the agent using your existing approach.
        
        Returns:
            The initialized agent
        """
       
        
        return create_agent(
            self.model,
            tools=[find_bike_rentals, get_weather_now, get_weather_forecast],
            system_prompt=advanced_agent_system_prompt()
        )
    
    def _extract_response_content(self, response: Any) -> str:
        """
        Extract content from agent response, handling different formats.
        
        Args:
            response: The raw agent response
            
        Returns:
            The extracted content as a string
        """
        if isinstance(response, dict):
            # Handle different response structures
            if 'messages' in response and response['messages']:
                last_message = response['messages'][-1]
                if isinstance(last_message, dict):
                    return last_message.get('content', str(last_message))
                else:
                    # Handle message objects
                    return getattr(last_message, 'content', str(last_message))
            elif 'output' in response:
                return response['output']
            elif 'content' in response:
                return response['content']
            else:
                return str(response)
        else:
            return str(response)
    
    def display_welcome(self):
        """Display the welcome message and available commands."""
        welcome_text = Text()
        welcome_text.append("🚴 Welcome to your Cycling Assistant! 🚴\n", style="bold cyan")
        welcome_text.append("I can help you find bike rentals, cycling routes, and local cycling advice.\n\n")
        welcome_text.append("Commands:\n", style="bold")
        welcome_text.append("  /help    - Show this help message\n", style="dim")
        welcome_text.append("  /clear   - Clear conversation history\n", style="dim")
        welcome_text.append("  /history - Show conversation history\n", style="dim")
        welcome_text.append("  /quit    - Exit the application\n", style="dim")
        welcome_text.append("  /exit    - Exit the application\n", style="dim")
        welcome_text.append("\nJust type your cycling questions and I'll help you out!", style="italic")
        
        panel = Panel(welcome_text, title="Cycling Assistant", border_style="blue")
        self.console.print(panel)
    
    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands that start with '/'.
        
        Args:
            user_input: The user's input string
            
        Returns:
            True if a command was handled, False otherwise
        """
        if not user_input.startswith('/'):
            return False
            
        command = user_input[1:].lower().strip()
        
        if command == 'help':
            self.display_welcome()
            return True
            
        elif command == 'clear':
            self.conversation_history.clear()
            self.console.print("[yellow]💭 Conversation history cleared![/yellow]")
            return True
            
        elif command == 'history':
            self.show_conversation_history()
            return True
            
        elif command in ['quit', 'exit', 'q']:
            self.console.print("[cyan]👋 Thanks for using Cycling Assistant! Happy cycling![/cyan]")
            return True
            
        else:
            self.console.print(f"[red]❌ Unknown command: {user_input}[/red]")
            self.console.print("[dim]Type /help for available commands[/dim]")
            return True
    
    def show_conversation_history(self):
        """Display the current conversation history."""
        if not self.conversation_history:
            self.console.print("[yellow]📝 No conversation history yet.[/yellow]")
            return
        
        self.console.print("\n[bold]Conversation History:[/bold]")
        for i, message in enumerate(self.conversation_history, 1):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            
            if role == 'user':
                self.console.print(f"[cyan]{i}. You:[/cyan] {content}")
            elif role == 'assistant':
                self.console.print(f"[green]{i}. Assistant:[/green] {content}")
        self.console.print()
    
    def add_to_history(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: Either 'user' or 'assistant'
            content: The message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })
    
    def create_messages_with_history(self, current_input: str) -> List[Dict[str, str]]:
        """
        Create a messages array including conversation history.
        
        Args:
            current_input: The current user input
            
        Returns:
            List of message dictionaries with history context
        """
        # For now, we'll use a simple approach that includes recent history
        # You can enhance this to be more sophisticated
        messages = []
        
        # Add recent conversation context (last 5 exchanges to avoid token limits)
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        
        for msg in recent_history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": current_input
        })
        
        return messages
    
    def process_user_input(self, user_input: str) -> Optional[str]:
        """
        Process user input through the agent and return the response.
        
        Args:
            user_input: The user's input string
            
        Returns:
            The agent's response or None if there was an error
        """
        try:
            # Create messages with conversation history
            messages = self.create_messages_with_history(user_input)
            
            # Show thinking indicator
            with self.console.status("[bold green]🤔 Thinking...", spinner="dots"):
                response = self.agent.invoke({"messages": messages})
            
            # Extract response content
            agent_response = self._extract_response_content(response)
            
            return agent_response
            
        except Exception as e:
            error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
            self.console.print(f"[red]{error_msg}[/red]")
            self.console.print("[dim]Please try rephrasing your question or check your configuration.[/dim]")
            return None
    
    def display_response(self, response: str):
        """
        Display the agent's response with nice formatting.
        
        Args:
            response: The response string to display
        """
        response_text = Text(response)
        response_panel = Panel(
            response_text,
            title="🤖 Cycling Assistant",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(response_panel)
    
    def run(self):
        """Main conversation loop."""
        self.display_welcome()
        
        try:
            while True:
                # Get user input with history and auto-suggest
                try:
                    user_input = prompt(
                        "🚴 You: ",
                        history=self.history,
                        auto_suggest=AutoSuggestFromHistory(),
                    ).strip()
                except (EOFError, KeyboardInterrupt):
                    self.console.print("\n[cyan]👋 Goodbye![/cyan]")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    # Check if it was a quit command
                    if user_input.lower().startswith('/quit') or user_input.lower().startswith('/exit'):
                        break
                    continue
                
                # Process the user input through the agent
                response = self.process_user_input(user_input)
                
                if response:
                    # Add to conversation history
                    self.add_to_history('user', user_input)
                    self.add_to_history('assistant', response)
                    
                    # Display the response
                    self.display_response(response)

        except KeyboardInterrupt:
            self.console.print("\n[cyan]👋 Interrupted. Goodbye![/cyan]")


def main():
    """Entry point for the conversational agent."""
    # You can change the model provider here for future flexibility
    model_provider = os.getenv("MODEL_PROVIDER", "azure_openai")
    
    try:
        agent = ConversationalCyclingAgent(model_provider=model_provider)
        agent.run()
    except Exception as e:
        console = Console()
        console.print(f"[red]Failed to initialize agent: {e}[/red]")
        console.print("[dim]Please check your configuration and try again.[/dim]")


if __name__ == "__main__":
    main()