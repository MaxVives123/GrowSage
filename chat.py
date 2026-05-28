"""
CLI de chat para el RAG botánico.

Uso:
  python chat.py
  python chat.py --question "¿Cuándo trasplantar tomates?"
"""
import argparse
import sys
import io
from dotenv import load_dotenv

# Fix Windows console encoding for UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from src.rag import build_chain, ask

load_dotenv()
console = Console()


def interactive_loop(chain):
    console.print(Panel(
        "[bold green]Botanica RAG[/bold green] — Huerto y plantas comestibles\n"
        "[dim]Escribe tu pregunta o 'salir' para terminar.[/dim]",
        border_style="green"
    ))

    while True:
        question = Prompt.ask("\n[bold cyan]Pregunta[/bold cyan]").strip()
        if not question or question.lower() in ("salir", "exit", "quit"):
            console.print("[dim]Hasta luego.[/dim]")
            break

        with console.status("[bold yellow]Buscando en la base de conocimiento...[/bold yellow]"):
            answer = ask(question, chain)

        console.print(Panel(
            Text(answer),
            title="[bold green]Respuesta[/bold green]",
            border_style="green",
        ))


def main():
    parser = argparse.ArgumentParser(description="Chat con el RAG botánico")
    parser.add_argument("--question", "-q", help="Pregunta directa (sin modo interactivo)")
    args = parser.parse_args()

    chain = build_chain()

    if args.question:
        answer = ask(args.question, chain)
        console.print(Panel(Text(answer), title="Respuesta", border_style="green"))
    else:
        interactive_loop(chain)


if __name__ == "__main__":
    main()
