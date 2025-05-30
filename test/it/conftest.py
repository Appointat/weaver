
import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def ensure_app_running():
    """
    Fixture to ensure the Flask app is running before integration tests.
    This will check if the app is already running, and if not, provide instructions.
    """
    base_url = "http://localhost:5000"
    
    try:
        # Check if app is already running
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Flask app is already running")
            yield
            return
    except requests.exceptions.RequestException:
        pass
    
    # App is not running, provide instructions
    pytest.fail(
        "\n" + "="*60 + "\n"
        "Flask app is not running!\n"
        "Please start the app before running integration tests:\n\n"
        "1. Open a terminal and navigate to the project root\n"
        "2. Run: python app.py\n"
        "3. Wait for the app to start (should see 'Running on http://localhost:5000')\n"
        "4. In another terminal, run the integration tests\n"
        "="*60
    )


@pytest.fixture(scope="function")
def clean_test_data():
    """
    Fixture to clean up test data after each test.
    This is a placeholder - implement based on your data storage mechanism.
    """
    yield
    # Add cleanup logic here if needed
    # For example, if you're storing files or database records during tests
    pass


class TestHealthCheck:
    """Basic health check to verify app is accessible"""
    
    def test_app_is_running(self):
        """Verify the Flask app is accessible"""
        response = requests.get("http://localhost:5000/health")
        assert response.status_code == 200
