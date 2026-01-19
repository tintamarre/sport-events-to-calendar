"""
Basketball calendar generator for CPLiège clubs.

Fetches match schedules from cpliege.be and generates ICS calendar files and JSON data.
"""

import json
import logging
import os
import uuid
import warnings
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
import slugify
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from requests.adapters import HTTPAdapter
from rich import print as rprint
from urllib3.util.retry import Retry

# Suppress BeautifulSoup warning about from_encoding with unicode markup
# This is triggered by pandas read_html internally
warnings.filterwarnings(
    "ignore",
    message="You provided Unicode markup but also provided a value for from_encoding",
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "http://www.cpliege.be"
CLUBS_URL = f"{BASE_URL}/caleclub.asp"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
EVENT_DURATION_MINUTES = 120
TIMEZONE = "Europe/Brussels"
BASE_RAW_PATH = (
    "https://raw.githubusercontent.com/tintamarre/sport-events-to-calendar/main/"
)

# Expected column names after renaming
COLUMN_NAMES = [
    "Code",
    "Unknown",
    "Weekday",
    "Date",
    "Heure",
    "Équipe 1",
    "Équipe 2",
    "Catégorie",
    "Autre",
]


def create_session() -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_clubs(session: requests.Session) -> dict[str, str]:
    """Fetch list of clubs from CPLiège website."""
    try:
        response = session.get(CLUBS_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch clubs list: {e}")
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    clubs = soup.find_all("a")

    clubs_dict = {}
    for club in clubs:
        club_name = " ".join(club.text.split())
        if club_name and club.get("href"):
            clubs_dict[club_name] = f"{BASE_URL}/" + club["href"]

    logger.info(f"Found {len(clubs_dict)} clubs")
    return clubs_dict


def get_club_agenda(club_url: str) -> Optional[pd.DataFrame]:
    """
    Fetch and parse club agenda from the website.

    Returns None if the agenda cannot be parsed.
    """
    try:
        tables = pd.read_html(club_url, header=5, encoding="ISO-8859-1")
        if not tables:
            logger.warning(f"No tables found at {club_url}")
            return None
        agenda = tables[0]
    except Exception as e:
        logger.error(f"Failed to read HTML table from {club_url}: {e}")
        return None

    # Validate we have enough columns
    if len(agenda.columns) < 9:
        logger.warning(
            f"Table has {len(agenda.columns)} columns, expected 9 at {club_url}"
        )
        return None

    # Check if "Unnamed: 7" exists (the category column)
    if "Unnamed: 7" not in agenda.columns:
        logger.warning(f"Missing expected column 'Unnamed: 7' at {club_url}")
        return None

    # Convert the column to string safely before using .str accessor
    cat_col = agenda["Unnamed: 7"].fillna("").astype(str)

    # Filter out rows where category is empty or is a parenthetical note
    mask = ~(
        (cat_col == "")
        | (cat_col == "nan")
        | (cat_col.str.startswith("(") & cat_col.str.endswith(")"))
    )
    agenda = agenda[mask]

    if agenda.empty:
        logger.warning(f"No valid events found at {club_url}")
        return None

    logger.info(f"Agenda shape: {agenda.shape} from {club_url}")

    # Rename columns
    agenda.columns = COLUMN_NAMES

    # Drop "Unknown" column
    agenda = agenda.drop("Unknown", axis=1)

    # Filter out rows with missing Date or Heure
    agenda = agenda[agenda["Date"].notna()]
    agenda = agenda[agenda["Heure"].notna()]

    if agenda.empty:
        logger.warning(f"No events with valid dates found at {club_url}")
        return None

    # Convert Heure to string and clean up
    agenda["Heure"] = agenda["Heure"].astype(str)

    # If Heure is ".", set it to 00:00
    agenda.loc[agenda["Heure"] == ".", "Heure"] = "00:00"

    # Replace . and ; in Heure by :
    agenda["Heure"] = agenda["Heure"].str.replace(".", ":", regex=False)
    agenda["Heure"] = agenda["Heure"].str.replace(";", ":", regex=False)

    # If Heure contains only one digit after : add a 0
    def fix_time_format(time_str: str) -> str:
        if ":" not in time_str:
            return "00:00"
        parts = time_str.split(":")
        if len(parts) != 2:
            return "00:00"
        hours, minutes = parts
        if len(minutes) == 1:
            minutes = minutes + "0"
        elif len(minutes) == 0:
            minutes = "00"
        return f"{hours}:{minutes}"

    agenda["Heure"] = agenda["Heure"].apply(fix_time_format)

    # Remove Weekday column
    agenda = agenda.drop("Weekday", axis=1)

    # Parse Date as datetime
    try:
        agenda["Date"] = pd.to_datetime(agenda["Date"], format="%d/%m/%y")
    except Exception as e:
        logger.error(f"Failed to parse dates from {club_url}: {e}")
        return None

    # Sort by category and date
    agenda = agenda.sort_values(by=["Catégorie", "Date"])

    return agenda


def generate_ics(
    agenda: pd.DataFrame, filename: str, cal_name: str, club_url: str
) -> bool:
    """
    Generate an ICS calendar file from the agenda.

    Returns True on success, False on failure.
    """
    try:
        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//CPLiège Calendar//cpliege.be//")
        cal.add("x-wr-calname", cal_name)

        for _, event_row in agenda.iterrows():
            e = Event()

            equipe1 = event_row.get("Équipe 1", "")
            equipe2 = event_row.get("Équipe 2", "")
            categorie = event_row.get("Catégorie", "")

            if pd.isna(equipe1):
                equipe1 = ""
            if pd.isna(equipe2):
                equipe2 = ""
            if pd.isna(categorie):
                categorie = ""

            name = f"🏀 {categorie}: {equipe1} et {equipe2}"

            code = event_row.get("Code", "")
            if pd.isna(code):
                code = ""
            description = f"[{code}] — {name}"

            # Build datetime
            date_str = pd.to_datetime(event_row["Date"]).strftime("%Y-%m-%d")
            time_str = event_row["Heure"]
            datetime_str = f"{date_str} {time_str}"

            try:
                start_dt = pd.to_datetime(datetime_str)
                end_dt = start_dt + pd.Timedelta(minutes=EVENT_DURATION_MINUTES)

                # Localize to timezone and convert to UTC
                start_dt = start_dt.tz_localize(TIMEZONE).tz_convert("UTC")
                end_dt = end_dt.tz_localize(TIMEZONE).tz_convert("UTC")
            except Exception as e:
                logger.warning(f"Failed to parse datetime '{datetime_str}': {e}")
                continue

            # Location is Équipe 1 (home team)
            location = equipe1 if equipe1 else ""

            # Generate deterministic UUID from name and date
            event_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"{name}-{date_str}")

            e.add("summary", name)
            e.add("dtstart", start_dt)
            e.add("dtend", end_dt)
            e.add("location", location)
            e.add("priority", 5)
            e.add("sequence", 1)
            e.add("description", description)
            e.add("url", club_url)
            e.add("uid", str(event_uuid))

            cal.add_component(e)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as f:
            f.write(cal.to_ical())

        return True

    except Exception as e:
        logger.error(f"Failed to generate ICS file {filename}: {e}")
        return False


def generate_club_json(
    agenda: pd.DataFrame, filename: str, club_id: str, club_name: str, club_slug: str
) -> bool:
    """
    Generate a JSON file with club events data.

    Returns True on success, False on failure.
    """
    try:
        events = []

        for _, event_row in agenda.iterrows():
            equipe1 = event_row.get("Équipe 1", "")
            equipe2 = event_row.get("Équipe 2", "")
            categorie = event_row.get("Catégorie", "")
            code = event_row.get("Code", "")
            autre = event_row.get("Autre", "")

            if pd.isna(equipe1):
                equipe1 = ""
            if pd.isna(equipe2):
                equipe2 = ""
            if pd.isna(categorie):
                categorie = ""
            if pd.isna(code):
                code = ""
            if pd.isna(autre):
                autre = ""

            date_str = pd.to_datetime(event_row["Date"]).strftime("%Y-%m-%d")
            time_str = event_row["Heure"]

            events.append({
                "code": str(code),
                "date": date_str,
                "time": time_str,
                "team1": str(equipe1),
                "team2": str(equipe2),
                "category": str(categorie),
                "location": str(equipe1),  # Home team is location
                "other": str(autre),
            })

        club_data = {
            "club": {
                "id": club_id,
                "name": club_name,
                "slug": club_slug,
            },
            "events": events,
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(club_data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        logger.error(f"Failed to generate JSON file {filename}: {e}")
        return False


def generate_all_events_json(all_agendas: pd.DataFrame, filename: str) -> bool:
    """
    Generate a global JSON file with all events.

    Returns True on success, False on failure.
    """
    try:
        events = []

        for _, event_row in all_agendas.iterrows():
            equipe1 = event_row.get("Équipe 1", "")
            equipe2 = event_row.get("Équipe 2", "")
            categorie = event_row.get("Catégorie", "")
            code = event_row.get("Code", "")
            autre = event_row.get("Autre", "")

            if pd.isna(equipe1):
                equipe1 = ""
            if pd.isna(equipe2):
                equipe2 = ""
            if pd.isna(categorie):
                categorie = ""
            if pd.isna(code):
                code = ""
            if pd.isna(autre):
                autre = ""

            date_str = pd.to_datetime(event_row["Date"]).strftime("%Y-%m-%d")
            time_str = event_row["Heure"]

            events.append({
                "code": str(code),
                "date": date_str,
                "time": time_str,
                "team1": str(equipe1),
                "team2": str(equipe2),
                "category": str(categorie),
                "location": str(equipe1),
                "other": str(autre),
            })

        global_data = {
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "events": events,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(global_data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        logger.error(f"Failed to generate global JSON file {filename}: {e}")
        return False


def main():
    """Main entry point."""
    session = create_session()

    # Fetch clubs
    try:
        clubs_dict = fetch_clubs(session)
    except Exception as e:
        logger.error(f"Failed to fetch clubs: {e}")
        return 1

    if not clubs_dict:
        logger.error("No clubs found")
        return 1

    rprint(f"[bold green]Found {len(clubs_dict)} clubs[/bold green]")

    # Build markdown listing
    md = "# 🏀 Les clubs du CPLiège\n\n"
    md += "Ce dépôt contient les agendas des clubs de basket du CPLiège.\n\n"
    md += "Les agendas sont disponibles au format CSV et ICS.\n\n"
    md += "Les agendas sont mis à jour automatiquement toutes semaines.\n\n"
    md += f"[L'agenda global]({BASE_RAW_PATH}data/CPLi%C3%A8ge.ics) est également disponible.\n\n"
    md += f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"

    all_agendas = pd.DataFrame()
    successful_clubs = 0
    failed_clubs = []

    for club_name, club_url in clubs_dict.items():
        rprint(f"[blue]Processing {club_name}...[/blue]")

        try:
            club_agenda = get_club_agenda(club_url)

            if club_agenda is None or club_agenda.empty:
                logger.warning(f"No agenda data for {club_name}")
                failed_clubs.append((club_name, "No agenda data"))
                continue

            md += f"## [{club_name}]({club_url})\n\n"

            all_agendas = pd.concat([all_agendas, club_agenda], ignore_index=True)

            club_slug = slugify.slugify(club_name)
            storage_path = f"data/{club_slug}"
            os.makedirs(storage_path, exist_ok=True)

            # Extract club_id from club_name (format: "1034 - RBC HANEFFE")
            club_id = club_name.split()[0] if club_name.split() else ""

            # Save CSV
            csv_filename = f"{storage_path}/{club_slug}.csv"
            club_agenda.to_csv(csv_filename, index=False)
            md += f"* [Agenda]({BASE_RAW_PATH}{csv_filename})\n"

            # Generate JSON file for the club
            json_filename = f"{storage_path}/events.json"
            if generate_club_json(club_agenda, json_filename, club_id, club_name, club_slug):
                rprint(f"  [green]Generated JSON: {json_filename}[/green]")
                md += f"* [JSON]({BASE_RAW_PATH}{json_filename})\n"

            # Generate ICS for each category
            categories = club_agenda["Catégorie"].dropna().unique()

            for category in categories:
                club_category_agenda = club_agenda[
                    club_agenda["Catégorie"] == category
                ]

                ics_filename = f"{storage_path}/{slugify.slugify(category)}.ics"
                cal_name = f"{club_name} - {category}"

                rprint(f"  Generating {cal_name}")

                if generate_ics(club_category_agenda, ics_filename, cal_name, club_url):
                    md += f"* [{category}]({BASE_RAW_PATH}{ics_filename})\n"

            md += "\n"
            successful_clubs += 1

        except Exception as e:
            logger.error(f"Failed to process club {club_name}: {e}")
            failed_clubs.append((club_name, str(e)))
            continue

    # Generate global calendar and JSON
    if not all_agendas.empty:
        all_agendas = all_agendas.drop_duplicates()
        os.makedirs("data", exist_ok=True)
        if generate_ics(all_agendas, "data/CPLiège.ics", "CPLiège", CLUBS_URL):
            rprint("[bold green]Generated global calendar (ICS)[/bold green]")
        if generate_all_events_json(all_agendas, "data/all-events.json"):
            rprint("[bold green]Generated global events (JSON)[/bold green]")

    # Save markdown listing
    with open("listing.md", "w") as f:
        f.write(md)

    # Print summary
    rprint("\n[bold]Summary:[/bold]")
    rprint(f"  [green]Successful: {successful_clubs}[/green]")
    rprint(f"  [red]Failed: {len(failed_clubs)}[/red]")

    if failed_clubs:
        rprint("\n[bold red]Failed clubs:[/bold red]")
        for club_name, error in failed_clubs:
            rprint(f"  - {club_name}: {error}")

    return 0 if successful_clubs > 0 else 1


if __name__ == "__main__":
    exit(main())
