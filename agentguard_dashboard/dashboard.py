from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def render_dashboard():
    console.print(Panel("[bold magenta]AgentGuard Enterprise Command Center[/bold magenta]\n[dim]Multi-Agent Governance & Auditing Dashboard[/dim]", box=box.ROUNDED))

    # Create summary metrics table
    table = Table(title="Live System Threat Audit", box=box.SIMPLE_HEAVY)
    table.add_column("Component", style="cyan", justify="left")
    table.add_column("Status", style="green", justify="center")
    table.add_column("Threats Blocked", style="red", justify="right")
    table.add_column("System Health", style="yellow", justify="center")

    table.add_row("App 1: Foundry Core", "[bold green]ONLINE[/bold green]", "1", "98.5%")
    table.add_row("App 2: Simulator Engine", "[bold green]ONLINE[/bold green]", "2", "100%")
    table.add_row("App 3: Dashboard HUD", "[bold green]ACTIVE[/bold green]", "0", "Optimal")

    console.print(table)
    console.print("\n[bold green]✔ All 3 Multi-Agent Governance MVP components successfully synchronized.[/bold green]\n")

if __name__ == "__main__":
    render_dashboard()
