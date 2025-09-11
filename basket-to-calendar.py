import pandas as pd
from bs4 import BeautifulSoup
import requests
import slugify
import os
from icalendar import Calendar, Event
import uuid
from datetime import datetime
from rich import print


clubs_url = "http://www.cpliege.be/caleclub.asp"

clubs_url_html = requests.get(clubs_url).text

soup = BeautifulSoup(clubs_url_html, "html.parser")

# read html and get every links
clubs = soup.find_all("a")

# tranform to get a dict with club name and url
clubs_dict = {}
for club in clubs:
    # removes "all whitespace characters (space, tab, newline, return, formfeed)"
    club_name = " ".join(club.text.split())
    clubs_dict[club_name] = "http://www.cpliege.be/" + club["href"]

print(clubs_dict)


def get_club_agenda(club_url):
    agenda = pd.read_html(club_url, header=5, encoding="ISO-8859-1")[0]

    # remove if column "Unnamed: 7" is empty OR starts with "(" and ends with ")"
    agenda = agenda[
        ~(
            agenda["Unnamed: 7"].isnull()
            | agenda["Unnamed: 7"].str.startswith("(")
            & agenda["Unnamed: 7"].str.endswith(")")
        )
    ]

    print(f"Agenda shape: {agenda.shape} from {club_url}")

    # rename columns
    agenda.columns = [
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

    # drop "Unknown" column
    agenda = agenda.drop("Unknown", axis=1)

    agenda = agenda[~agenda["Date"].isnull()]
    agenda = agenda[~agenda["Heure"].isnull()]

    # Heure to string
    agenda["Heure"] = agenda["Heure"].astype(str)

    # if Heure is ".", set it to 00:00
    agenda.loc[agenda["Heure"] == ".", "Heure"] = "00:00"

    # replace . and ; in Heure by :
    for char in [".", ";"]:
        agenda["Heure"] = agenda["Heure"].str.replace(char, ":", regex=False)

    # if Heure contains only one number after : add a 0
    agenda["Heure"] = agenda["Heure"].apply(
        lambda x: x if len(x.split(":")[1]) == 2 else x + "0"
    )

    # remove Weekday column
    agenda.drop("Weekday", axis=1, inplace=True)

    # Date as datetime
    agenda["Date"] = pd.to_datetime(agenda["Date"], format="%d/%m/%y")

    # order by catégorie and then by date
    agenda.sort_values(by=["Catégorie", "Date"], inplace=True)

    return agenda


def generate_ics(agenda, filename, cal_name, club_url):
    cal = Calendar()

    cal.add("version", "2.0")

    for event in agenda.iterrows():
        e = Event()

        name = (
            "🏀 "
            + event[1]["Catégorie"]
            + ": "
            + event[1]["Équipe 1"]
            + " et "
            + event[1]["Équipe 2"]
        )

        code = event[1]["Code"]
        description = "[" + code + "] — " + name

        startime = (
            pd.to_datetime(event[1]["Date"]).strftime("%Y-%m-%d")
            + " "
            + event[1]["Heure"]
        )
        endtime = pd.to_datetime(startime) + pd.Timedelta(minutes=120)

        # time zone
        location = "Europe/Brussels"

        # from local time to UTC
        startime = pd.to_datetime(startime).tz_localize(location).tz_convert("UTC")
        endtime = pd.to_datetime(endtime).tz_localize(location).tz_convert("UTC")

        # if ["Équipe 1"] is not empty
        if not pd.isnull(event[1]["Équipe 1"]):
            location = event[1]["Équipe 1"]
        else:
            location = ""

        # generate uuid from name
        event_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, name)

        e.begin = startime.strftime("%Y-%m-%d %H:%M:%S%Z")
        e.end = endtime.strftime("%Y-%m-%d %H:%M:%S%Z")
        e.add("summary", name)
        e.add("dtstart", startime)
        e.add("dtend", endtime)
        # e.add('dtstamp', datetime.now())
        e.add("location", location)
        e.add("priority", 5)
        e.add("sequence", 1)
        e.add("description", description)
        e.add("url", club_url)
        e.add("uid", event_uuid)

        cal.add_component(e)

    # save to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
        f.close()


if __name__ == "__main__":
    base_raw_path = (
        "https://raw.githubusercontent.com/tintamarre/sport-events-to-calendar/main/"
    )

    md = "# 🏀 Les clubs du CPLiège\n\n"

    md += "Ce dépôt contient les agendas des clubs de basket du CPLiège.\n\n"
    md += "Les agendas sont disponibles au format CSV et ICS.\n\n"
    md += "Les agendas sont mis à jour automatiquement toutes semaines.\n\n"
    md += "[L'agenda global](https://raw.githubusercontent.com/tintamarre/sport-events-to-calendar/main/data/CPLi%C3%A8ge.ics) est également disponible.\n\n"
    md += (
        "Dernière mise à jour: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n"
    )

    agenda = pd.DataFrame()

    for club_name, club_url in clubs_dict.items():
        md += "## [" + club_name + "](" + club_url + ")\n\n"

        club_agenda = get_club_agenda(club_url)

        agenda = pd.concat([agenda, club_agenda], ignore_index=True)

        storage_path = "data/" + slugify.slugify(club_name)

        if not os.path.exists(storage_path):
            os.mkdir(storage_path)

        club_agenda.to_csv(
            storage_path + "/" + slugify.slugify(club_name) + ".csv", index=False
        )

        md += (
            "* [Agenda]("
            + base_raw_path
            + storage_path
            + "/"
            + slugify.slugify(club_name)
            + ".csv)\n"
        )

        categories = club_agenda["Catégorie"].unique()

        for category in categories:
            club_category_agenda = club_agenda[club_agenda["Catégorie"] == category]

            filename = (
                storage_path
                + "/"
                + slugify.slugify(club_category_agenda["Catégorie"].iloc[0])
                + ".ics"
            )

            cal_name = club_name + " - " + club_category_agenda["Catégorie"].iloc[0]

            print(f"Generating {cal_name} calendar at {filename}")
            generate_ics(club_category_agenda, filename, cal_name, club_url)

            md += (
                "* ["
                + category
                + "]("
                + base_raw_path
                + storage_path
                + "/"
                + slugify.slugify(category)
                + ".ics)\n"
            )

        md += "\n"

    # remove duplicates from agenda
    agenda.drop_duplicates(inplace=True)
    generate_ics(
        agenda, "data/CPLiège.ics", "CPLiège", "http://www.cpliege.be/caleclub.asp"
    )

    with open("listing.md", "w") as f:
        f.write(md)
        f.close()
