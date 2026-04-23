"""Resource monitoring module for Docker containers."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import docker

from docker_monitor.core.docker_client import DockerClientManager
from docker_monitor.core.exceptions import ResourceMonitoringError


class ResourceMonitor:
    def __init__(self, docker_client: DockerClientManager):
        self.docker_client = docker_client
    
    def get_container_stats(self, container) -> Dict[str, Any]:
        """Get stats from a container object directly."""
        try:
            info = container.attrs
            
            # Default values
            cpu_percent = 0.0
            memory_usage = 0
            memory_limit = 0
            memory_percent = 0.0
            net_rx = 0
            net_tx = 0
            block_read = 0
            block_write = 0
            pids_current = 0
            
            try:
                stats = container.stats(stream=False)
                
                # CPU
                try:
                    cpu_stats = stats.get('cpu_stats', {})
                    precpu_stats = stats.get('precpu_stats', {})
                    cpu_usage = cpu_stats.get('cpu_usage', {})
                    precpu_usage = precpu_stats.get('cpu_usage', {})
                    cpu_delta = cpu_usage.get('total_usage', 0) - precpu_usage.get('total_usage', 0)
                    system_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
                    if system_delta > 0 and cpu_delta > 0:
                        online_cpus = cpu_stats.get('online_cpus', 1)
                        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100
                except:
                    pass
                
                # Memory
                mem = stats.get('memory_stats', {})
                if mem:
                    memory_usage = mem.get('usage', 0)
                    memory_limit = mem.get('limit', 0)
                    if memory_limit > 0:
                        memory_percent = (memory_usage / memory_limit) * 100
                
                # Network
                networks = stats.get('networks', {})
                if networks:
                    net_rx = sum(net.get('rx_bytes', 0) for net in networks.values())
                    net_tx = sum(net.get('tx_bytes', 0) for net in networks.values())
                
                # Block I/O
                blkio = stats.get('blkio_stats', {})
                if blkio:
                    io_bytes = blkio.get('io_service_bytes_recursive', [])
                    if io_bytes:
                        block_read = sum(io.get('value', 0) for io in io_bytes if io.get('op') == 'Read')
                        block_write = sum(io.get('value', 0) for io in io_bytes if io.get('op') == 'Write')
                
                # PIDs
                pids = stats.get('pids_stats', {})
                if pids:
                    pids_current = pids.get('current', 0)
                    
            except:
                pass
            
            return {
                'id': container.id,
                'name': info.get('Name', '').lstrip('/'),
                'status': info.get('State', {}).get('Status', 'unknown'),
                'cpu_percent': cpu_percent,
                'memory_usage': memory_usage,
                'memory_limit': memory_limit,
                'memory_percent': memory_percent,
                'net_rx': net_rx,
                'net_tx': net_tx,
                'block_read': block_read,
                'block_write': block_write,
                'pids': pids_current,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ResourceMonitoringError(f"Failed: {str(e)}")
    
    def get_containers_stats(self, container_names=None, all_containers=False):
        """Get stats for multiple containers."""
        stats_list = []
        
        try:
            # Get containers
            if container_names:
                containers = []
                for name in container_names:
                    try:
                        c = self.docker_client.client.containers.get(name)
                        containers.append(c)
                    except:
                        continue
            else:
                containers = self.docker_client.client.containers.list(all=all_containers)
            
            # Get stats for each container
            for container in containers:
                try:
                    stats = self.get_container_stats(container)
                    stats_list.append(stats)
                except Exception as e:
                    # Skip containers with errors but continue
                    continue
            
            return stats_list
            
        except Exception as e:
            raise ResourceMonitoringError(f"Failed: {str(e)}")
