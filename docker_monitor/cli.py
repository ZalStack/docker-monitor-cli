#!/usr/bin/env python3
"""
Main CLI entry point for Docker Monitor.
Provides command-line interface for monitoring and managing Docker containers.
"""

import click
import sys
import time
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box

from docker_monitor.core.docker_client import DockerClientManager
from docker_monitor.core.monitor import ResourceMonitor
from docker_monitor.core.container_manager import ContainerManager
from docker_monitor.core.exceptions import DockerConnectionError, ContainerNotFoundError
from docker_monitor.utils.formatters import (
    format_size, format_percentage, format_uptime,
    format_container_status, get_status_color
)
from docker_monitor.utils.constants import (
    VERSION, DEFAULT_REFRESH_INTERVAL, MAX_CONTAINER_NAME_LENGTH,
    TABLE_STYLE, SUCCESS_EMOJI, ERROR_EMOJI, WARNING_EMOJI, INFO_EMOJI
)

console = Console()

def get_docker_client():
    """Get Docker client instance with error handling."""
    try:
        return DockerClientManager()
    except DockerConnectionError as e:
        console.print(f"[red]{ERROR_EMOJI} Error: {str(e)}[/red]")
        console.print("[yellow]Make sure Docker daemon is running.[/yellow]")
        sys.exit(1)

def display_banner():
    """Display application banner."""
    banner = f"""
    ╔══════════════════════════════════════════════════════════╗
    ║     🐳 DOCKER MONITOR CLI - Advanced DevOps Tool v{VERSION}    ║
    ║         Real-time Container Monitoring & Management        ║
    ╚══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """🐳 Docker Monitor CLI - Advanced container monitoring and management tool."""
    if version:
        console.print(f"Docker Monitor CLI version {VERSION}", style="bold green")
        sys.exit(0)
    
    if ctx.invoked_subcommand is None:
        display_banner()
        console.print("\n[bold]Available Commands:[/bold]")
        console.print("  [cyan]stats[/cyan]     - Show real-time container statistics")
        console.print("  [cyan]list[/cyan]      - List all containers with details")
        console.print("  [cyan]inspect[/cyan]   - Inspect detailed container information")
        console.print("  [cyan]stop[/cyan]      - Stop running containers")
        console.print("  [cyan]start[/cyan]     - Start stopped containers")
        console.print("  [cyan]restart[/cyan]   - Restart containers")
        console.print("  [cyan]top[/cyan]       - Display running processes in container")
        console.print("  [cyan]logs[/cyan]      - Fetch container logs")
        console.print("  [cyan]prune[/cyan]     - Remove unused containers and resources")
        console.print("\n[dim]Run 'docker-monitor COMMAND --help' for more information.[/dim]")

@main.command()
@click.option('--watch', '-w', is_flag=True, help='Watch mode with auto-refresh')
@click.option('--interval', '-i', default=DEFAULT_REFRESH_INTERVAL, 
              help=f'Refresh interval in seconds (default: {DEFAULT_REFRESH_INTERVAL})')
@click.option('--container', '-c', multiple=True, help='Filter by container name or ID')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show all containers including stopped')
def stats(watch, interval, container, show_all):
    """📊 Display real-time container resource usage statistics."""
    client = get_docker_client()
    monitor = ResourceMonitor(client)
    
    def generate_stats_table():
        """Generate statistics table."""
        containers_stats = monitor.get_containers_stats(
            container_names=list(container) if container else None,
            all_containers=show_all
        )
        
        table = Table(
            title="🐳 Container Resource Statistics",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="bright_blue"
        )
        
        table.add_column("Container ID", style="dim", width=12)
        table.add_column("Name", style="cyan", width=MAX_CONTAINER_NAME_LENGTH)
        table.add_column("Status", width=10)
        table.add_column("CPU %", justify="right", width=8)
        table.add_column("Memory", justify="right", width=12)
        table.add_column("Memory %", justify="right", width=9)
        table.add_column("Network I/O", justify="right", width=15)
        table.add_column("Block I/O", justify="right", width=15)
        table.add_column("PIDs", justify="right", width=6)
        
        if not containers_stats:
            table.add_row("No containers found", "", "", "", "", "", "", "", "")
        else:
            for stat in containers_stats:
                status_color = get_status_color(stat['status'])
                
                table.add_row(
                    stat['id'][:12],
                    stat['name'],
                    f"[{status_color}]{stat['status']}[/{status_color}]",
                    format_percentage(stat['cpu_percent']),
                    f"{format_size(stat['memory_usage'])} / {format_size(stat['memory_limit'])}",
                    format_percentage(stat['memory_percent']),
                    f"↓{format_size(stat['net_rx'])} ↑{format_size(stat['net_tx'])}",
                    f"↓{format_size(stat['block_read'])} ↑{format_size(stat['block_write'])}",
                    str(stat['pids'])
                )
        
        return table
    
    if watch:
        display_banner()
        console.print(f"[dim]Live monitoring - Press Ctrl+C to exit[/dim]\n")
        
        try:
            with Live(generate_stats_table(), refresh_per_second=1/interval, 
                     console=console, screen=True) as live:
                while True:
                    time.sleep(interval)
                    live.update(generate_stats_table())
        except KeyboardInterrupt:
            console.print("\n[green]✓ Monitoring stopped[/green]")
    else:
        display_banner()
        table = generate_stats_table()
        console.print(table)
        console.print(f"\n[dim]💡 Tip: Use --watch flag for real-time monitoring[/dim]")

@main.command()
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show all containers')
@click.option('--running', '-r', is_flag=True, help='Show only running containers')
@click.option('--format', '-f', 'output_format', type=click.Choice(['table', 'json', 'simple']), 
              default='table', help='Output format')
def list(show_all, running, output_format):
    """📋 List Docker containers with detailed information."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    filters = {}
    if running:
        filters['status'] = 'running'
    elif not show_all:
        filters['status'] = 'running'
    
    containers = manager.list_containers(all_containers=show_all or running, filters=filters)
    
    if output_format == 'json':
        import json
        console.print(json.dumps(containers, indent=2, default=str))
    elif output_format == 'simple':
        for container in containers:
            status_color = get_status_color(container['status'])
            console.print(f"[cyan]{container['name']}[/cyan] - [{status_color}]{container['status']}[/{status_color}] - {container['image']}")
    else:
        table = Table(title="📦 Docker Containers", box=box.ROUNDED, header_style="bold cyan")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Name", style="cyan")
        table.add_column("Image", style="green")
        table.add_column("Status")
        table.add_column("Created")
        table.add_column("Ports", width=20)
        
        for container in containers:
            status_color = get_status_color(container['status'])
            ports = ', '.join(container['ports']) if container['ports'] else '-'
            
            table.add_row(
                container['id'][:12],
                container['name'],
                container['image'],
                f"[{status_color}]{container['status']}[/{status_color}]",
                container['created'],
                ports
            )
        
        console.print(table)
    
    console.print(f"\n[dim]Total containers: {len(containers)}[/dim]")

@main.command()
@click.argument('container_name')
def inspect(container_name):
    """🔍 Inspect detailed information of a container."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    try:
        info = manager.inspect_container(container_name)
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["header"].update(
            Panel(f"[bold cyan]Container: {info['Name']} [dim]({info['Id'][:12]})[/dim][/bold cyan]", 
                  border_style="cyan")
        )
        
        # Main info panel
        info_text = Text()
        info_text.append("📦 Image: ", style="bold green")
        info_text.append(f"{info['Config']['Image']}\n")
        info_text.append("📊 State: ", style="bold yellow")
        info_text.append(f"{info['State']['Status']}\n")
        info_text.append("🔄 Started: ", style="bold blue")
        info_text.append(f"{info['State']['StartedAt']}\n")
        info_text.append("💻 Platform: ", style="bold magenta")
        info_text.append(f"{info['Platform']}\n")
        info_text.append("🏠 Hostname: ", style="bold cyan")
        info_text.append(f"{info['Config']['Hostname']}\n")
        
        if info['NetworkSettings']['IPAddress']:
            info_text.append("🌐 IP Address: ", style="bold")
            info_text.append(f"{info['NetworkSettings']['IPAddress']}")
        
        layout["body"].update(Panel(info_text, title="Container Details", border_style="green"))
        layout["footer"].update(Panel(f"[dim]Created: {info['Created']}[/dim]", border_style="dim"))
        
        console.print(layout)
        
    except ContainerNotFoundError as e:
        console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")

@main.command()
@click.argument('containers', nargs=-1, required=True)
@click.option('--time', '-t', default=10, help='Seconds to wait before killing container')
@click.option('--force', '-f', is_flag=True, help='Force stop the container')
def stop(containers, time, force):
    """🛑 Stop one or more running containers."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    for container_name in containers:
        try:
            if force:
                result = manager.kill_container(container_name)
                console.print(f"[yellow]{WARNING_EMOJI} Force killed container: {container_name}[/yellow]")
            else:
                result = manager.stop_container(container_name, timeout=time)
                console.print(f"[green]{SUCCESS_EMOJI} Stopped container: {container_name}[/green]")
        except ContainerNotFoundError as e:
            console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red]{ERROR_EMOJI} Failed to stop {container_name}: {str(e)}[/red]")

@main.command()
@click.argument('containers', nargs=-1, required=True)
def start(containers):
    """▶️ Start one or more stopped containers."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    for container_name in containers:
        try:
            result = manager.start_container(container_name)
            console.print(f"[green]{SUCCESS_EMOJI} Started container: {container_name}[/green]")
        except ContainerNotFoundError as e:
            console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red]{ERROR_EMOJI} Failed to start {container_name}: {str(e)}[/red]")

@main.command()
@click.argument('containers', nargs=-1, required=True)
@click.option('--time', '-t', default=10, help='Seconds to wait before killing container')
def restart(containers, time):
    """🔄 Restart one or more containers."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    for container_name in containers:
        try:
            result = manager.restart_container(container_name, timeout=time)
            console.print(f"[green]{SUCCESS_EMOJI} Restarted container: {container_name}[/green]")
        except ContainerNotFoundError as e:
            console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red]{ERROR_EMOJI} Failed to restart {container_name}: {str(e)}[/red]")

@main.command()
@click.argument('container_name')
@click.option('--ps-args', '-p', default='aux', help='ps arguments to use')
def top(container_name, ps_args):
    """📊 Display running processes in a container."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    try:
        processes = manager.get_container_processes(container_name, ps_args)
        
        if not processes:
            console.print(f"[yellow]No processes found in container {container_name}[/yellow]")
            return
        
        table = Table(title=f"📋 Processes in {container_name}", box=box.ROUNDED)
        
        # Add columns based on first process keys
        for key in processes[0].keys():
            table.add_column(key, style="cyan")
        
        for process in processes:
            row = [str(value) for value in process.values()]
            table.add_row(*row)
        
        console.print(table)
        
    except ContainerNotFoundError as e:
        console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")

@main.command()
@click.argument('container_name')
@click.option('--tail', default=100, help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--since', help='Show logs since timestamp')
@click.option('--timestamps', '-t', is_flag=True, help='Show timestamps')
def logs(container_name, tail, follow, since, timestamps):
    """📜 Fetch logs from a container."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    console.print(f"[bold cyan]Logs from container: {container_name}[/bold cyan]\n")
    
    try:
        if follow:
            console.print("[dim]Following logs - Press Ctrl+C to exit[/dim]\n")
            try:
                for log_line in manager.get_container_logs(
                    container_name, tail=tail, follow=True, 
                    since=since, timestamps=timestamps
                ):
                    console.print(log_line.decode('utf-8').rstrip())
            except KeyboardInterrupt:
                console.print("\n[green]✓ Log following stopped[/green]")
        else:
            logs_output = manager.get_container_logs(
                container_name, tail=tail, follow=False,
                since=since, timestamps=timestamps
            )
            console.print(logs_output.decode('utf-8'))
            
    except ContainerNotFoundError as e:
        console.print(f"[red]{ERROR_EMOJI} {str(e)}[/red]")

@main.command()
@click.option('--all', '-a', is_flag=True, help='Remove all unused containers, not just dangling ones')
@click.option('--volumes', '-v', is_flag=True, help='Prune volumes as well')
@click.option('--force', '-f', is_flag=True, help='Do not prompt for confirmation')
def prune(all, volumes, force):
    """🧹 Remove unused Docker containers and resources."""
    client = get_docker_client()
    manager = ContainerManager(client)
    
    display_banner()
    
    if not force:
        if not click.confirm(f"{WARNING_EMOJI} This will remove unused containers. Continue?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    result = manager.prune_containers(filters={'until': '24h'} if not all else None)
    
    if result['ContainersDeleted']:
        console.print(f"[green]{SUCCESS_EMOJI} Deleted containers:[/green]")
        for container in result['ContainersDeleted']:
            console.print(f"  - {container}")
    else:
        console.print("[yellow]No containers to prune[/yellow]")
    
    console.print(f"\n[green]Space reclaimed: {format_size(result['SpaceReclaimed'])}[/green]")

if __name__ == "__main__":
    main()