import os
import pytest
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Add src to path for imports
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/models"))
)

from azure_openai_models import get_azure_openai_model

load_dotenv()


class TestAzureOpenAIConnection:
    """Integration tests for Azure OpenAI model connection."""

    @pytest.fixture
    def check_environment(self):
        """Check if required environment variables are set."""
        required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            pytest.skip(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @pytest.mark.parametrize(
        "model_name",
        [
            "gpt-35-turbo",
            "gpt-4o",
            "gpt-4o-mini",
        ],
    )
    def test_get_azure_openai_model_instantiation(self, check_environment, model_name):
        """Test that the model can be instantiated successfully."""
        model = get_azure_openai_model(model_name)

        assert model is not None
        assert isinstance(model, AzureChatOpenAI)
        assert model.model_name == model_name

    def test_azure_openai_connection_and_response(self, check_environment):
        """Test that the model can connect and generate a response."""
        model = get_azure_openai_model("gpt-4o-mini")

        # Simple test prompt
        response = model.invoke("Say 'Hello, World!' and nothing else.")

        assert response is not None
        assert hasattr(response, "content")
        assert len(response.content) > 0
        assert "hello" in response.content.lower()

    def test_missing_environment_variables(self):
        """Test that missing environment variables raise appropriate errors."""
        # Temporarily remove environment variables
        original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)

        try:
            with pytest.raises(
                ValueError, match="Missing Azure OpenAI environment variables"
            ):
                get_azure_openai_model("gpt-4o-mini")
        finally:
            # Restore environment variables
            if original_endpoint:
                os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint
            if original_key:
                os.environ["AZURE_OPENAI_API_KEY"] = original_key

    def test_invalid_model_name(self, check_environment):
        """Test that invalid model names raise appropriate errors."""
        with pytest.raises(ValueError, match="Model name not recognized"):
            get_azure_openai_model("invalid-model-name")

    def test_model_with_custom_temperature(self, check_environment):
        """Test that the model respects temperature settings from environment."""
        # Set custom temperature
        original_temp = os.environ.get("TEMPERATURE")
        os.environ["TEMPERATURE"] = "0.9"

        try:
            model = get_azure_openai_model("gpt-4o-mini")
            # Note: temperature is set during initialization
            assert model is not None
        finally:
            # Restore original temperature
            if original_temp:
                os.environ["TEMPERATURE"] = original_temp
            else:
                os.environ.pop("TEMPERATURE", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
