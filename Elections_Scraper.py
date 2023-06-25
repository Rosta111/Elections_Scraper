"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Rostislav Vymazal
email: rostislav.vymazal@sentrum.cz
discord: Rostislav V.
"""
import csv
import sys
from typing import List

import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, url: str):
        self.url = url
        self.html = self._get_html(url)
        self.registered_voters = []
        self.envelopes_issued = []
        self.valid_votes = []

    def _get_html(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        html = BeautifulSoup(response.text, "html.parser")
        print(f"STAHUJI DATA Z URL: {url}")
        return html

    def get_municipalities(self) -> List[str]:
        municipalities_search = self.html.find_all("td", "overflow_name")
        municipalities = []
        for m in municipalities_search:
            municipalities.append(m.text)
        return municipalities

    def get_municipality_links(self) -> List[str]:
        link_search = self.html.find_all("td", "cislo", "href")
        municipality_links = []
        for link_municipality in link_search:
            municipality_links.append(f"https://volby.cz/pls/ps2017nss/{link_municipality.a['href']}")
        return municipality_links

    def get_municipality_ids(self) -> List[str]:
        ids = self.html.find_all("td", "cislo")
        municipality_ids = []
        for i in ids:
            municipality_ids.append(i.text)
        return municipality_ids

    def get_parties(self) -> List[str]:
        municipality_link = self.get_municipality_links()
        html = requests.get(municipality_link[0])
        html_villages = BeautifulSoup(html.text, "html.parser")
        party = html_villages.find_all("td", "overflow_name")
        parties = []
        for p in party:
            parties.append(p.text)
        return parties
    def _get_voter_data(self) -> None:
        path = self.get_municipality_links()
        for p in path:
            html_path = requests.get(p)
            html_village = BeautifulSoup(html_path.text, "html.parser")
            voter = html_village.find_all("td", headers="sa2")
            for v in voter:
                v = v.text
                self.registered_voters.append(v.replace('\xa0', ' '))
            attend = html_village.find_all("td", headers="sa3")
            for a in attend:
                a = a.text
                self.envelopes_issued.append(a.replace('\xa0', ' '))
            correct = html_village.find_all("td", headers="sa6")
            for c in correct:
                c = c.text
                self.valid_votes.append(c.replace('\xa0', ' '))

    def get_votes(self) -> List[List[str]]:
        links = self.get_municipality_links()
        votes = []
        for li in links:
            html = self._get_html(li)
            votes_search = html.find_all("td", "cislo", headers=["t1sb4", "t2sb4"])
            temporary = []
            for v in votes_search:
                temporary.append(v.text + ' %')
            votes.append(temporary)
        return votes

    def create_rows(self) -> List[List[str]]:
        rows = []
        self._get_voter_data()
        municipalities = self.get_municipalities()
        ids = self.get_municipality_ids()
        votes = self.get_votes()
        zipped = zip(ids, municipalities, self.registered_voters, self.envelopes_issued, self.valid_votes)
        aux_var = []
        for i, m, rv, ei, vv in zipped:
            aux_var.append([i, m, rv, ei, vv])
        zip_all = zip(aux_var, votes)
        for av, vs in zip_all:
            rows.append(av + vs)
        return rows

def election_results(url: str, file: str) -> None:
        try:
            scraper = Scraper(url)
            header = ['Kód obce', 'Název obce', 'Voliči v seznamu', 'Vydané obálky', 'Platné hlasy']
            content = scraper.create_rows()
            parties = scraper.get_parties()
            print(f"UKLÁDÁM DATA DO SOUBORU: {file}")
            for party in parties:
                header.append(party)
            with open(file, 'w', newline='') as f:
                f_writer = csv.writer(f)
                f_writer.writerow(header)
                f_writer.writerows(content)
            print(f"UKONČUJI: {sys.argv[0]}")
        except IndexError:
            print("Nastala chyba. Nejspíš máte špatný odkaz nebo jste jej zapomněli dát do uvozovek.")
            sys.exit()

if __name__ == '__main__':
    address = sys.argv[1]
    file_name = sys.argv[2]
    election_results(address, file_name)
