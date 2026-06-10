"""macOS Keychain integration for TradeSight API keys."""
import subprocess
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_CONFIG_JSON_PATH = Path(__file__).resolve().parent.parent.parent / 'config' / 'api_keys.json'

def _load_json_config() -> dict:
    """Load API keys from config/api_keys.json as a fallback."""
    if _CONFIG_JSON_PATH.exists():
        try:
            with open(_CONFIG_JSON_PATH) as f:
                return json.load(f)
        except Exception as e:
            logger.debug(f"Failed to read {_CONFIG_JSON_PATH}: {e}")
    return {}

class KeychainManager:
    """Manages API keys in macOS Keychain with fallback to environment variables."""
    
    def __init__(self, service_prefix="TradeSight"):
        self.service_prefix = service_prefix
        
    def _run_security_command(self, args):
        """Run macOS security command with error handling."""
        try:
            result = subprocess.run(
                ['security'] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.debug(f"Security command failed: {e}")
            return None
        except FileNotFoundError:
            logger.warning("macOS security command not found - not running on macOS?")
            return None
    
    def get_api_key(self, key_name, account="api-key", fallback_env=None, json_key=None):
        """
        Get API key from Keychain with environment variable and JSON file fallback.
        
        Args:
            key_name: Name of the service/API (e.g., "Alpaca-Key", "Alpaca-Secret")
            account: Account name in keychain (default: "api-key")  
            fallback_env: Environment variable name to check if keychain fails
            json_key: Key name in config/api_keys.json (e.g. "alpaca_key")
            
        Returns:
            str: API key or empty string if not found
        """
        service_name = f"{self.service_prefix}-{key_name}"
        
        # Try keychain first
        api_key = self._run_security_command([
            'find-generic-password',
            '-s', service_name,
            '-a', account,
            '-w'  # output password only
        ])
        
        if api_key:
            logger.debug(f"Retrieved {key_name} API key from keychain")
            return api_key
            
        # Fallback to environment variable
        if fallback_env:
            env_key = os.environ.get(fallback_env, "")
            if env_key:
                logger.info(f"Using {key_name} API key from environment variable {fallback_env}")
                return env_key
        
        # Fallback to config/api_keys.json
        if json_key:
            cfg = _load_json_config()
            value = cfg.get(json_key, "")
            if value:
                logger.info(f"Using {key_name} API key from config/api_keys.json")
                return value
        
        logger.warning(f"No {key_name} API key found in keychain, environment, or config/api_keys.json")
        return ""
    
    def set_api_key(self, key_name, api_key, account="api-key"):
        """
        Store API key in Keychain.
        
        Args:
            key_name: Name of the service/API (e.g., "Alpaca-Key", "Alpaca-Secret")
            api_key: The API key to store
            account: Account name in keychain (default: "api-key")
            
        Returns:
            bool: True if successful, False otherwise
        """
        service_name = f"{self.service_prefix}-{key_name}"
        
        result = self._run_security_command([
            'add-generic-password',
            '-s', service_name,
            '-a', account,
            '-w', api_key,
            '-U'  # update if exists
        ])
        
        # security command returns empty string on success
        if result is not None:
            logger.info(f"Successfully stored {key_name} API key in keychain")
            return True
        else:
            logger.error(f"Failed to store {key_name} API key in keychain")
            return False

# Global instance for easy import
keychain = KeychainManager()

# Convenience functions for trading API keys
def get_alpaca_api_key():
    """Get Alpaca API key from keychain, env, or config/api_keys.json."""
    key = keychain.get_api_key('Alpaca-Key', account='luckyai', fallback_env='ALPACA_API_KEY', json_key='alpaca_key')
    if not key:
        key = keychain.get_api_key('Alpaca-Key', fallback_env='ALPACA_API_KEY', json_key='alpaca_key')
    return key

def get_alpaca_secret_key():
    """Get Alpaca secret key from keychain, env, or config/api_keys.json."""
    key = keychain.get_api_key('Alpaca-Secret', account='luckyai', fallback_env='ALPACA_SECRET_KEY', json_key='alpaca_secret')
    if not key:
        key = keychain.get_api_key('Alpaca-Secret', fallback_env='ALPACA_SECRET_KEY', json_key='alpaca_secret')
    return key

def get_polygon_api_key():
    """Get Polygon API key from keychain with POLYGON_API_KEY fallback."""
    return keychain.get_api_key("Polygon", fallback_env="POLYGON_API_KEY")

def get_yahoo_api_key():
    """Get Yahoo Finance API key from keychain with YAHOO_API_KEY fallback."""
    return keychain.get_api_key("Yahoo", fallback_env="YAHOO_API_KEY")

def get_openai_api_key():
    """Get OpenAI API key from keychain with OPENAI_API_KEY fallback."""
    return keychain.get_api_key("OpenAI", fallback_env="OPENAI_API_KEY")
