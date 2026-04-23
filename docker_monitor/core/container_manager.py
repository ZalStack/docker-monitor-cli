"""Container management module for Docker operations."""

import docker
from typing import List, Dict, Any, Optional, Union, Generator
from datetime import datetime

from docker_monitor.core.docker_client import DockerClientManager
from docker_monitor.core.exceptions import (
    ContainerNotFoundError, 
    ContainerOperationError
)
from docker_monitor.utils.formatters import format_timestamp


class ContainerManager:
    """
    Manage Docker containers - start, stop, restart, inspect, etc.
    """
    
    def __init__(self, docker_client: DockerClientManager):
        """
        Initialize container manager.
        
        Args:
            docker_client: DockerClientManager instance
        """
        self.docker_client = docker_client
    
    def _get_container(self, container_id: str) -> docker.models.containers.Container:
        """
        Get container object with error handling.
        
        Args:
            container_id: Container ID or name
        
        Returns:
            Container object
        
        Raises:
            ContainerNotFoundError: If container doesn't exist
        """
        try:
            return self.docker_client.client.containers.get(container_id)
        except docker.errors.NotFound:
            raise ContainerNotFoundError(f"Container '{container_id}' not found")
        except Exception as e:
            raise ContainerOperationError(f"Failed to get container '{container_id}': {str(e)}")
    
    def list_containers(self, all_containers: bool = False, 
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List containers with their details.
        
        Args:
            all_containers: Include stopped containers
            filters: Docker filters for listing
        
        Returns:
            List of container information dictionaries
        """
        try:
            containers = self.docker_client.client.containers.list(
                all=all_containers,
                filters=filters
            )
            
            container_list = []
            for container in containers:
                container_info = {
                    'id': container.id,
                    'short_id': container.short_id,
                    'name': container.name,
                    'image': ' '.join(container.image.tags) if container.image.tags else container.image.id[:12],
                    'status': container.status,
                    'created': format_timestamp(container.attrs.get('Created', '')),
                    'ports': self._format_ports(container.attrs.get('NetworkSettings', {}).get('Ports', {})),
                    'labels': container.labels,
                    'command': container.attrs.get('Config', {}).get('Cmd', [])
                }
                container_list.append(container_info)
            
            return container_list
            
        except Exception as e:
            raise ContainerOperationError(f"Failed to list containers: {str(e)}")
    
    def _format_ports(self, ports: Dict) -> List[str]:
        """Format port mappings for display."""
        formatted = []
        for container_port, host_bindings in ports.items():
            if host_bindings:
                for binding in host_bindings:
                    host_ip = binding.get('HostIp', '0.0.0.0')
                    host_port = binding.get('HostPort', '')
                    formatted.append(f"{host_ip}:{host_port}->{container_port}")
            else:
                formatted.append(container_port)
        return formatted
    
    def inspect_container(self, container_id: str) -> Dict[str, Any]:
        """
        Get detailed container information.
        
        Args:
            container_id: Container ID or name
        
        Returns:
            Detailed container information
        """
        container = self._get_container(container_id)
        return container.attrs
    
    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """
        Stop a running container.
        
        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing
        
        Returns:
            True if successful
        
        Raises:
            ContainerOperationError: If operation fails
        """
        try:
            container = self._get_container(container_id)
            container.stop(timeout=timeout)
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to stop container '{container_id}': {str(e)}")
    
    def start_container(self, container_id: str) -> bool:
        """
        Start a stopped container.
        
        Args:
            container_id: Container ID or name
        
        Returns:
            True if successful
        """
        try:
            container = self._get_container(container_id)
            container.start()
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to start container '{container_id}': {str(e)}")
    
    def restart_container(self, container_id: str, timeout: int = 10) -> bool:
        """
        Restart a container.
        
        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing during stop
        
        Returns:
            True if successful
        """
        try:
            container = self._get_container(container_id)
            container.restart(timeout=timeout)
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to restart container '{container_id}': {str(e)}")
    
    def kill_container(self, container_id: str, signal: str = "SIGKILL") -> bool:
        """
        Kill a container immediately.
        
        Args:
            container_id: Container ID or name
            signal: Signal to send
        
        Returns:
            True if successful
        """
        try:
            container = self._get_container(container_id)
            container.kill(signal=signal)
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to kill container '{container_id}': {str(e)}")
    
    def pause_container(self, container_id: str) -> bool:
        """Pause a container."""
        try:
            container = self._get_container(container_id)
            container.pause()
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to pause container '{container_id}': {str(e)}")
    
    def unpause_container(self, container_id: str) -> bool:
        """Unpause a container."""
        try:
            container = self._get_container(container_id)
            container.unpause()
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to unpause container '{container_id}': {str(e)}")
    
    def remove_container(self, container_id: str, force: bool = False, 
                        volumes: bool = False) -> bool:
        """
        Remove a container.
        
        Args:
            container_id: Container ID or name
            force: Force remove running container
            volumes: Remove associated volumes
        
        Returns:
            True if successful
        """
        try:
            container = self._get_container(container_id)
            container.remove(force=force, v=volumes)
            return True
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to remove container '{container_id}': {str(e)}")
    
    def get_container_logs(self, container_id: str, tail: Union[int, str] = 'all',
                          follow: bool = False, since: Optional[str] = None,
                          timestamps: bool = False) -> Union[bytes, Generator]:
        """
        Get container logs.
        
        Args:
            container_id: Container ID or name
            tail: Number of lines to return
            follow: Follow log output
            since: Show logs since timestamp
            timestamps: Show timestamps
        
        Returns:
            Log output as bytes or generator
        """
        try:
            container = self._get_container(container_id)
            return container.logs(
                tail=tail,
                follow=follow,
                since=since,
                timestamps=timestamps,
                stream=follow
            )
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to get logs for '{container_id}': {str(e)}")
    
    def get_container_processes(self, container_id: str, 
                               ps_args: str = 'aux') -> List[Dict[str, str]]:
        """
        Get running processes in a container.
        
        Args:
            container_id: Container ID or name
            ps_args: ps command arguments
        
        Returns:
            List of process information
        """
        try:
            container = self._get_container(container_id)
            return container.top(ps_args=ps_args)['Processes']
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to get processes for '{container_id}': {str(e)}")
    
    def exec_command(self, container_id: str, command: Union[str, List[str]],
                    workdir: Optional[str] = None) -> tuple:
        """
        Execute a command in a container.
        
        Args:
            container_id: Container ID or name
            command: Command to execute
            workdir: Working directory
        
        Returns:
            Tuple of (exit_code, output)
        """
        try:
            container = self._get_container(container_id)
            result = container.exec_run(command, workdir=workdir)
            return result.exit_code, result.output
        except ContainerNotFoundError:
            raise
        except Exception as e:
            raise ContainerOperationError(f"Failed to execute command in '{container_id}': {str(e)}")
    
    def prune_containers(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Remove unused containers.
        
        Args:
            filters: Filters for pruning
        
        Returns:
            Dictionary with pruning results
        """
        try:
            return self.docker_client.client.containers.prune(filters=filters)
        except Exception as e:
            raise ContainerOperationError(f"Failed to prune containers: {str(e)}")