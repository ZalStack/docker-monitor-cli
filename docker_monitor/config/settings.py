"""Settings management for Docker Monitor CLI."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """
    Application settings manager.
    Handles configuration loading and saving.
    """
    
    CONFIG_DIR = Path.home() / '.docker-monitor'
    CONFIG_FILE = CONFIG_DIR / 'config.json'
    
    DEFAULT_SETTINGS = {
        'refresh_interval': 2,
        'max_container_name_length': 20,
        'show_all_containers': False,
        'default_log_lines': 100,
        'color_output': True,
        'docker_socket': 'unix://var/run/docker.sock'
    }
    
    def __init__(self):
        """Initialize settings."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> None:
        """Load settings from config file."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded_settings = json.load(f)
                    self._settings.update(loaded_settings)
            except Exception:
                # Use defaults if loading fails
                pass
    
    def save(self) -> bool:
        """
        Save current settings to config file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._settings, f, indent=2)
            return True
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
        
        Returns:
            Setting value
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
    
    def reset(self) -> None:
        """Reset to default settings."""
        self._settings = self.DEFAULT_SETTINGS.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return self._settings.copy()