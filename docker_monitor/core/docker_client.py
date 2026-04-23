"""Docker client management module."""

import docker
from typing import Optional, Dict, Any
from docker.errors import DockerException, APIError

from docker_monitor.core.exceptions import DockerConnectionError
from docker_monitor.utils.constants import DOCKER_BASE_URL, DOCKER_VERSION


class DockerClientManager:
    """
    Manages Docker client connections and operations.
    Handles connection errors and provides a unified interface.
    """
    
    def __init__(self, base_url: str = DOCKER_BASE_URL, version: str = DOCKER_VERSION):
        """
        Initialize Docker client connection.
        
        Args:
            base_url: Docker daemon socket URL
            version: Docker API version
        
        Raises:
            DockerConnectionError: If cannot connect to Docker daemon
        """
        self.base_url = base_url
        self.version = version
        self._client = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Docker daemon."""
        try:
            self._client = docker.DockerClient(
                base_url=self.base_url,
                version=self.version,
                timeout=10
            )
            # Test connection
            self._client.ping()
        except DockerException as e:
            raise DockerConnectionError(
                f"Failed to connect to Docker daemon at {self.base_url}. "
                f"Error: {str(e)}"
            )
        except Exception as e:
            raise DockerConnectionError(f"Unexpected error connecting to Docker: {str(e)}")
    
    @property
    def client(self) -> docker.DockerClient:
        """
        Get the Docker client instance.
        
        Returns:
            Docker client instance
        
        Raises:
            DockerConnectionError: If client is not connected
        """
        if self._client is None:
            self._connect()
        return self._client
    
    @property
    def api_client(self) -> docker.APIClient:
        """Get low-level API client."""
        return self.client.api
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get Docker daemon information.
        
        Returns:
            Dictionary containing Docker daemon info
        """
        try:
            info = self.client.info()
            version = self.client.version()
            return {
                'info': info,
                'version': version,
                'connected': True
            }
        except APIError as e:
            raise DockerConnectionError(f"Failed to get Docker info: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        Check if Docker daemon is responsive.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            self._client.close()