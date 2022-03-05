import csv
import os
from numpy import NaN
import requests
import re


PRIZE_MAP = {
    "Gold Medal" : 4,
    "Silver Medal" : 3,
    "Bronze Medal" : 2,
    "Honourable Mention" : 1,
    "" : 0
}

class StranNeObstaja(Exception):
    pass


vzorec_tekmovalke = re.compile(
    r'<td class="egmo-scores">\d*</td>'
    r'<td class="egmo-scores">\d*</td>'
    r'<td class="egmo-scores"><a href="/people/person\d+/">(?P<code>.*?)</a></td>'
    r'<td class="egmo-scores"><a href="/people/person\d+/">(?P<name>.*?)</a></td>'
    r'<td class="egmo-scores">(?P<P1>\d*)</td>'
    r'<td class="egmo-scores">(?P<P2>\d*)</td>'
    r'<td class="egmo-scores">(?P<P3>\d*)</td>'
    r'<td class="egmo-scores">(?P<P4>\d*)</td>'
    r'<td class="egmo-scores">(?P<P5>\d*)</td>'
    r'<td class="egmo-scores">(?P<P6>\d*)</td>'
    r'<td class="egmo-scores">\d*</td>'
    r'<td class="egmo-scores">(?P<prize>.*?)</td></tr>',
    flags=re.DOTALL
)

vzorec_vrstice = re.compile(
    r'<tr>.*?</tr>',
    flags=re.DOTALL
)

vzorec_tabele = re.compile(
    r'Scores by contestant code.*?'
    r'Ranked scores',
    flags=re.DOTALL
)

vzorec_cutoffs = re.compile(
    r'gold medals \(scores &ge; (?P<gold>\d*).*?'
    r'silver medals \(scores &ge; (?P<silver>\d*).*?'
    r'bronze medals \(scores &ge; (?P<bronze>\d*)',
    flags=re.DOTALL
)

html_dir = os.path.join("podatki", "html")
csv_dir = os.path.join("podatki", "csv")


def url_tabele(n: int) -> str:
    """Vrne tabelo z rezultati n-tega EGMO."""
    return f"https://www.egmo.org/egmos/egmo{n}/scoreboard/"


def file_name(n: int, koncnica: str) -> str:
    """Vrne niz z imenom datoteke za n-ti EGMO s podano končnico."""
    return f"egmo{n}.{koncnica}"


def save_string_to_file(text: str, directory: str, filename: str) -> None:
    """Shrani niz 'text' v datoteko 'filename' v 'directory'."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)


def get_html(n: int) -> str:
    """Shrani niz 'text' v datoteko 'filename' v 'directory'."""
    path = os.path.join("podatki", "html", file_name(n, "html"))
    with open(path, 'r', encoding='utf-8') as file:
        vsebina = file.read()
        return vsebina


def download_nth_egmo(n: int) -> str:
    """Naloži html stran z rezultati n-tega EGMO in jo shrani v datoteko."""
    try:
        page_content = requests.get(url_tabele(n))
        page_content.encoding = 'utf-8'
        vsebina = page_content.text

        if "404 Not Found" in vsebina:
            raise StranNeObstaja

        save_string_to_file(vsebina,
            os.path.join("podatki", "html"),
            file_name(n, 'html'))

    except requests.exceptions.ConnectionError:
        print(
            "Prišlo je do napake.\n"
            "Preverite internetno povezavo in poskusite ponovno."
        )


def izlosci_tekmovalko(vrstica: str) -> dict:
    """Vrstico tabele z rezultati tekmovalke pretvori v slovar."""
    tekmovalka = vzorec_tekmovalke.search(vrstica).groupdict()
    for i in range(1, 7):
        tekmovalka[f"P{i}"] = int(tekmovalka[f"P{i}"])
    tekmovalka["prize"] = PRIZE_MAP[tekmovalka["prize"]]
    return tekmovalka


def vrni_prvo_tabelo(stran_z_rezultati: str) -> str:
    """Na strani z rezultati poišče prvo tabelo in jo vrne kot niz."""
    for x in vzorec_tabele.finditer(stran_z_rezultati):
        return x.group(0)


def save_to_csv(dict: list, directory: str, filename: str) -> None:
    """Seznam slovarjev shrani v csv datoteko."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)

    with open(path, 'w', encoding='utf-8', newline='') as file_out:
        writer = csv.DictWriter(file_out, dict[0].keys())
        writer.writeheader()
        writer.writerows(dict)


def html_to_csv(n: int) -> None:
    """Podatke iz datoteke 'html' pretvori in shrani v 'csv'."""
    stran = get_html(n)

    tekmovalke = []

    tabela = vrni_prvo_tabelo(stran)

    for vrstica in vzorec_vrstice.finditer(tabela):
        try:
            tekmovalke.append(izlosci_tekmovalko(vrstica.group(0)))
        except AttributeError:
            continue

    save_to_csv(tekmovalke, csv_dir, file_name(n, "csv"))

def get_cutoffs(n: int):
    stran = get_html(n)
    cutoffs = {}
    cutoffs['egmo'] = n
    cutoffs |= vzorec_cutoffs.search(stran).groupdict()
    return cutoffs


def main(force_dl: bool = False, force_clean: bool = False) -> None:
    n = 2
    while True:
        try:
            if force_dl or not os.path.isfile(
                os.path.join("podatki", "html", file_name(n, 'html'))
            ):
                download_nth_egmo(n)

            if force_clean or not os.path.isfile(
                os.path.join("podatki", "csv", file_name(n, 'csv'))
            ):
                html_to_csv(n)

        except StranNeObstaja:
            break
        n += 1

    cutoffs = []
    for m in range(2,n):
        cutoffs.append(get_cutoffs(m))

    save_to_csv(cutoffs, csv_dir, "cutoffs.csv")


if __name__ == '__main__':
    main(force_dl=True, force_clean=True)
