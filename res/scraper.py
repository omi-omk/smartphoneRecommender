import requests
from bs4 import BeautifulSoup
import csv
import re
import os

class SmartphoneScraper:
    def __init__(self, input_csv, output_csv):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.links = self._read_links()
        self._initialize_output_csv()

    def _read_links(self):
        if not os.path.exists(self.input_csv):
            raise FileNotFoundError(f"Input file '{self.input_csv}' not found!")

        links = []
        with open(self.input_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if 'links' not in reader.fieldnames:
                raise ValueError("The input CSV must have a column named 'links'.")
            links = [row['links'] for row in reader]
        return links

    def _initialize_output_csv(self):
        if not os.path.exists(self.output_csv):
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Title", "Image", "Good", "Bad", "Price (INR)", "Best buy link", "Summary"])

    def _scrape_data(self, url):
        scraped_data = {}
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch the page: {url}. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        scraped_data["Title"] = soup.h1.text.strip() if soup.h1 else "Unknown Title"

        image_tag = soup.find("img", attrs={"alt": scraped_data["Title"]})
        scraped_data["Image"] = image_tag['src'].split('?')[0] if image_tag and 'src' in image_tag.attrs else "Image not found"

        summary_section = soup.find("div", class_="_inrcntr _shrinkjs")
        scraped_data["Summary"] = summary_section.text.strip() if summary_section else "No summary found"

        specs_section = soup.find("div", class_="_pdswrp")
        if specs_section:
            for spec in specs_section.find_all("li", class_="_flx"):
                key_element = spec.find("span", class_="_ttl")
                value_element = spec.find("span", class_="_vltxt")
                if key_element and value_element:
                    key = f"key.{key_element.text.strip()}"
                    value = value_element.text.strip()
                    scraped_data[key] = value

        specs_tables = soup.find_all("div", class_="_gry-bg _spctbl _ovfhide")
        for table in specs_tables:
            category = table.find("div", class_="_hd").text.strip()
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    key = f"{category}.{cells[0].text.strip()}"
                    value = cells[1].text.strip()
                    scraped_data[key] = value

        good_bad_section = soup.find("div", class_="_flx _pdqty")
        if good_bad_section:
            for ul in good_bad_section.find_all("ul"):
                header = ul.find("li", class_="_flx")
                if header:
                    category = header.text.strip()
                    points = [li.text.strip() for li in ul.find_all("li") if not li.get("class")]
                    scraped_data[category] = ", ".join(points)

        price_container = soup.find("a", class_="_trtprc")
        if price_container:
            scraped_data["Best buy link"] = price_container.get('href', '').strip()
            price = price_container.text.strip()
            scraped_data["Price (INR)"] = re.sub(r'[^\d]', '', price)

        return scraped_data

    def _update_csv(self, scraped_data):
        with open(self.output_csv, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            existing_headers = next(reader)

        new_headers = set(scraped_data.keys()) - set(existing_headers)
        if new_headers:
            existing_headers.extend(new_headers)
            with open(self.output_csv, 'r+', newline='', encoding='utf-8') as file:
                content = file.readlines()
                content[0] = ','.join(existing_headers) + '\n'
                file.seek(0)
                file.writelines(content)

        row = {header: scraped_data.get(header, "") for header in existing_headers}
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=existing_headers)
            writer.writerow(row)

    def scrape_all(self):
        total_links = len(self.links)
        for index, link in enumerate(self.links, start=1):
            scraped_data = self._scrape_data(link)
            if not scraped_data:
                continue
            self._update_csv(scraped_data)
            print(f"Scraping {index}/{total_links} smartphone(s) done.")

        print("Scraping completed, and data saved to the CSV file!")

# Example usage
if __name__ == "__main__":
    scraper = SmartphoneScraper("mobiles.csv", "scraped_mobiles.csv")
    scraper.scrape_all()
