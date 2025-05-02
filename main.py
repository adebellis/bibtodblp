import requests
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import time
import re
import os
from rich.table import Table
from rich.console import Console

console = Console()


def normalize_title(title):
    title = re.sub(r"\s+", " ", title).strip().lower()
    title = re.sub(r"[{}\"'\\]", "", title)
    return title


def search_dblp_hits(title, author=None):
    query = title
    if author:
        query = f"{author} {title}"
    url = (
        f"https://dblp.org/search/publ/api?q={requests.utils.quote(query)}&format=json"
    )
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        return results.get("result", {}).get("hits", {}).get("hit", [])
    except Exception as e:
        console.print(f"[red]Error during DBLP search for '{title}': {e}[/red]")
        return []


def select_dblp_entry(title, hits):
    if not hits:
        return None

    console.print(
        f'\n[bold yellow]🔍 Multiple DBLP results for:[/bold yellow] [cyan]"{title}"[/cyan]\n'
    )

    table = Table(title="DBLP Matches", show_lines=True, box=None)
    table.add_column("Index", justify="center", style="bold")
    table.add_column("Title", style="cyan")
    table.add_column("Authors", style="magenta")
    table.add_column("Venue", style="blue")
    table.add_column("Year", justify="center")
    table.add_column("URL", style="dim")

    for idx, hit in enumerate(hits, start=1):
        info = hit.get("info", {})
        hit_title = info.get("title", "—")
        authors = info.get("authors", {}).get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        short_authors = []
        for a in authors[:2]:
            short_authors.append(a["text"] if isinstance(a, dict) else str(a))
        if len(authors) > 2:
            short_authors.append("...")
        authors_str = ", ".join(short_authors)
        venue = str(info.get("venue", "—"))
        year = str(info.get("year", "—"))
        url = info.get("url", "")
        table.add_row(str(idx), hit_title, authors_str, venue, year, url)

    console.print(table)
    console.print("[bold][0][/bold] Skip this entry\n")

    while True:
        try:
            choice = int(
                console.input(
                    "[bold green]Select the correct entry [0-N]: [/bold green]"
                )
            )
            if 0 <= choice <= len(hits):
                return (
                    hits[choice - 1].get("info", {}).get("url", "")
                    if choice > 0
                    else None
                )
        except ValueError:
            pass
        console.print("[red]Invalid input. Please enter a number.[/red]")


def get_dblp_id_by_title_interactive(title, first_author=None):
    hits = search_dblp_hits(title, first_author)
    print(hits)
    if not hits:
        hits = search_dblp_hits(title, None)
    if not hits:
        return None
    if len(hits) == 1:
        return (
            hits[0].get("info", {}).get("url", "").replace("https://dblp.org/rec/", "")
        )
    selected_url = select_dblp_entry(title, hits)
    if selected_url:
        return selected_url.replace("https://dblp.org/rec/", "")
    return None


def get_dblp_bibtex(dblp_id, condensed=True):
    param = 0 if condensed else 1
    bib_url = f"https://dblp.org/rec/{dblp_id}.bib?view=bibtex&param={param}"
    print(bib_url)
    try:
        response = requests.get(bib_url)
        response.raise_for_status()
        return response.content.decode("utf-8")
    except Exception as e:
        print(f"Error fetching BibTeX for {dblp_id}: {e}")
        return None


def replace_key(bibtex_str, new_key):
    return re.sub(r"^@(\w+)\{[^,]+,", rf"@\1{{{new_key},", bibtex_str, count=1)


def update_bib_file(input_bib_path, output_bib_path, condensed=False):
    with open(input_bib_path, "r") as bibtex_file:
        original_bib = bibtexparser.load(bibtex_file)

    updated_entries = []

    for entry in original_bib.entries:
        title = entry.get("title", "")
        original_key = entry.get("ID", "")
        authors = entry.get("author", "")
        first_author = None
        if isinstance(authors, str):
            if len(authors.split(" and\n")) > 1:
                first_author = authors.split(" and\n")[0]
            if len(authors.split(" and ")) > 1:
                first_author = authors.split(" and ")[0]
            else:
                first_author = None
        elif isinstance(authors, list) and authors:
            first_author = authors[0]

        print(f"Processing: {title}...")

        dblp_id = get_dblp_id_by_title_interactive(title, first_author)
        print(dblp_id)
        if dblp_id:
            bibtex_entry = get_dblp_bibtex(dblp_id, condensed=condensed)
            print(condensed)
            print(bibtex_entry)
            if bibtex_entry:
                bibtex_entry = replace_key(bibtex_entry, original_key)
                updated_entries.append(f"% DBLP ID: {dblp_id}\n{bibtex_entry}")
                time.sleep(1)
                continue

        print("Fallback to original entry")
        writer = BibTexWriter()
        fallback_db = BibDatabase()
        fallback_db.entries = [entry]
        updated_entries.append(writer.write(fallback_db).strip())
        time.sleep(1)

    with open(output_bib_path, "w") as f:
        f.write("\n\n".join(updated_entries))

    print(f"\n✅ Updated BibTeX written to: {output_bib_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Replace BibTeX entries with DBLP citations."
    )
    parser.add_argument("--input", required=True, help="Path to the input .bib file")
    parser.add_argument(
        "--output", required=False, help="Path to the output .bib file", default=None
    )
    parser.add_argument(
        "--condensed", action="store_true", help="Use condensed DBLP citation style"
    )
    args = parser.parse_args()
    output_path = args.output
    if not output_path:
        base, ext = os.path.splitext(args.input)
        output_path = f"{base}_dblp{ext}"

    update_bib_file(args.input, output_path, condensed=args.condensed)
