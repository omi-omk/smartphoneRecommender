import requests
from bs4 import BeautifulSoup
import csv
import re
import os  # For checking file existence

# Input CSV containing links to smartphones
input_csv = "mobiles.csv"
output_csv = "scraped_mobiles.csv"

# Ensure the input CSV exists
if not os.path.exists(input_csv):
    print(f"Input file '{input_csv}' not found!")
    exit()

# Read the links from the input CSV
links = []
with open(input_csv, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    if 'links' not in reader.fieldnames:
        print("The input CSV must have a column named 'links'.")
        exit()
    for row in reader:
        links.append(row['links'])

# Initialize or load the output CSV
if not os.path.exists(output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Image", "Good", "Bad", "Price (INR)", "Best buy link", "Summary"])  # Default headers

def scrape_smartphone_data(url):
    scraped_data = {}
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {url}. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title
    title = soup.h1.text.strip() if soup.h1 else "Unknown Title"
    scraped_data["Title"] = title

    # Extract the main image URL
    image_tag = soup.find("img", attrs={"alt": title})
    image = image_tag['src'].split('?')[0] if image_tag and 'src' in image_tag.attrs else "Image not found"
    scraped_data["Image"] = image

    # Extract summary
    summary_section = soup.find("div", class_="_inrcntr _shrinkjs")
    scraped_data["Summary"] = summary_section.text.strip() if summary_section else "No summary found"

    # Extract key specifications
    specs_section = soup.find("div", class_="_pdswrp")
    if specs_section:
        for spec in specs_section.find_all("li", class_="_flx"):
            key_element = spec.find("span", class_="_ttl")
            value_element = spec.find("span", class_="_vltxt")
            if key_element and value_element:
                key = f"key.{key_element.text.strip()}"
                value = value_element.text.strip()
                scraped_data[key] = value

    # Extract detailed specifications tables
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

    # Extract Good and Bad points
    good_bad_section = soup.find("div", class_="_flx _pdqty")
    if good_bad_section:
        for ul in good_bad_section.find_all("ul"):
            header = ul.find("li", class_="_flx")
            if header:
                category = header.text.strip()  # "Good" or "Bad"
                points = [li.text.strip() for li in ul.find_all("li") if not li.get("class")]
                scraped_data[category] = ", ".join(points)  # Store as a comma-separated string

    # Extract best buy price and link
    price_container = soup.find("a", class_="_trtprc")
    if price_container:
        best_buy_link = price_container.get('href', '').strip()
        price = price_container.text.strip()
        scraped_data["Best buy link"] = best_buy_link
        scraped_data["Price (INR)"] = re.sub(r'[^\d]', '', price)

    return scraped_data

# Process each link and update the output CSV
total_links = len(links)
for index, link in enumerate(links, start=1):
    scraped_data = scrape_smartphone_data(link)
    if not scraped_data:
        continue

    with open(output_csv, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        existing_headers = next(reader)

    new_headers = set(scraped_data.keys()) - set(existing_headers)
    if new_headers:
        existing_headers.extend(new_headers)
        with open(output_csv, 'r+', newline='', encoding='utf-8') as file:
            content = file.readlines()
            content[0] = ','.join(existing_headers) + '\n'
            file.seek(0)
            file.writelines(content)

    row = {header: scraped_data.get(header, "") for header in existing_headers}
    with open(output_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=existing_headers)
        writer.writerow(row)

    print(f"Scraping {index}/{total_links} smartphone(s) done.")

print("Scraping completed, and data saved to the CSV file!")
