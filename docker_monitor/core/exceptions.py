"""Custom exceptions for Docker Monitor CLI."""

class DockerMonitorError(Exception):
    """Base exception for Docker Monitor CLI."""
    pass

class DockerConnectionError(DockerMonitorError):
    """Raised when cannot connect to Docker daemon."""
    pass

class ContainerNotFoundError(DockerMonitorError):
    """Raised when container is not found."""
    pass

class ContainerOperationError(DockerMonitorError):
    """Raised when container operation fails."""
    pass

class ResourceMonitoringError(DockerMonitorError):
    """Raised when resource monitoring fails."""
    pass