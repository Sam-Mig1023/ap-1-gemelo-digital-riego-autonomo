"""
Quick Test Script for Phenology Agent with LangChain
Run this to verify the AI agent is working correctly
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.phenology_agent_service import get_phenology_agent
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


async def test_basic_phenology():
    """Test basic phenology calculation"""
    console.print("\n[bold cyan]🧪 Test 1: Basic Phenology Calculation[/bold cyan]")
    
    try:
        agent = get_phenology_agent()
        result = agent._calculate_phenology_raw("zone-1-nw")
        
        table = Table(title="Phenology Data - zone-1-nw")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Crop", result.crop_name)
        table.add_row("Stage", f"{result.stage_name} ({result.current_stage})")
        table.add_row("Kc", str(result.kc))
        table.add_row("Days Since Planting", str(result.days_since_planting))
        table.add_row("Days to Flowering", str(result.days_to_flowering))
        table.add_row("Days to Harvest", str(result.days_to_harvest))
        table.add_row("Progress", f"{result.progress_pct}%")
        
        console.print(table)
        console.print("[green]✓ Basic calculation works![/green]\n")
        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]\n")
        return False


async def test_agent_tools():
    """Test agent tools"""
    console.print("[bold cyan]🧪 Test 2: Agent Tools[/bold cyan]")
    
    try:
        agent = get_phenology_agent()
        
        console.print(f"\n[yellow]Available Tools: {len(agent.tools)}[/yellow]")
        for tool in agent.tools:
            console.print(f"  • [cyan]{tool.name}[/cyan]: {tool.description[:80]}...")
        
        console.print("\n[green]✓ All tools loaded![/green]\n")
        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]\n")
        return False


async def test_ai_analysis():
    """Test AI-powered analysis"""
    console.print("[bold cyan]🧪 Test 3: AI Analysis with ReAct Agent[/bold cyan]")
    console.print("[yellow]⚠️  This may take 10-30 seconds...[/yellow]\n")
    
    try:
        agent = get_phenology_agent()
        result = agent.get_phenology_with_reasoning("zone-1-nw")
        
        console.print(Panel(
            f"[bold]Zone:[/bold] {result['phenology']['zone_id']}\n"
            f"[bold]Crop:[/bold] {result['phenology']['crop_name']}\n"
            f"[bold]Stage:[/bold] {result['phenology']['stage_name']}\n"
            f"[bold]Kc:[/bold] {result['phenology']['kc']}\n\n"
            f"[bold cyan]AI Reasoning:[/bold cyan]\n{result['ai_reasoning'][:500]}...",
            title="🤖 AI Phenology Analysis",
            border_style="green"
        ))
        
        console.print("[green]✓ AI analysis works![/green]\n")
        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print("[yellow]Note: Make sure GROQ_API_KEY is set in .env[/yellow]\n")
        return False


async def test_irrigation_recommendation():
    """Test AI irrigation recommendation"""
    console.print("[bold cyan]🧪 Test 4: AI Irrigation Recommendation[/bold cyan]")
    
    try:
        agent = get_phenology_agent()
        recommendation = agent.get_irrigation_recommendation(
            zone_id="zone-1-nw",
            current_moisture=22.0,
            et0=5.5,
            rain_forecast=0.0
        )
        
        console.print(Panel(
            f"[bold]Recommended:[/bold] {recommendation.recommended_mm} mm\n"
            f"[bold]Confidence:[/bold] {recommendation.confidence * 100:.0f}%\n\n"
            f"[bold cyan]Reasoning:[/bold cyan]\n{recommendation.reasoning}\n\n"
            f"[bold yellow]Risk Factors:[/bold yellow]\n" + 
            "\n".join(f"  • {r}" for r in recommendation.risk_factors) + "\n\n"
            f"[bold green]Tips:[/bold green]\n" +
            "\n".join(f"  • {t}" for t in recommendation.optimization_tips),
            title="💧 Irrigation Recommendation",
            border_style="blue"
        ))
        
        console.print("[green]✓ Irrigation recommendation works![/green]\n")
        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]\n")
        return False


async def run_all_tests():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold magenta]🌱 Phenology Agent Test Suite[/bold magenta]\n"
        "Testing LangChain integration with ReAct pattern",
        border_style="magenta"
    ))
    
    results = []
    
    # Test 1: Basic calculation
    results.append(await test_basic_phenology())
    
    # Test 2: Tools
    results.append(await test_agent_tools())
    
    # Test 3: AI Analysis (requires Groq API)
    results.append(await test_ai_analysis())
    
    # Test 4: Irrigation Rec
    results.append(await test_irrigation_recommendation())
    
    # Summary
    console.print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        console.print(f"[bold green]✓ All tests passed! ({passed}/{total})[/bold green]")
    else:
        console.print(f"[bold yellow]⚠️  {passed}/{total} tests passed[/bold yellow]")
        console.print("[yellow]Note: AI tests require GROQ_API_KEY in .env[/yellow]")
    
    console.print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
