# Smartphone Scraper


### Class: `SmartphoneScraper`

#### Attributes:
- `input_csv` (str): Path to the input CSV file containing smartphone links.
- `output_csv` (str): Path to the output CSV file where scraped data is saved.
- `links` (list): List of URLs extracted from the input CSV file.

#### Methods:
1. `__init__(self, input_csv, output_csv)`:
   - Initializes the scraper, reads links, and prepares the output CSV.

2. `_read_links(self)`:
   - Reads URLs from the input CSV file.

3. `_initialize_output_csv(self)`:
   - Creates the output CSV file with default headers if it does not exist.

4. `_scrape_data(self, url)`:
   - Scrapes data from a smartphone webpage and returns it as a dictionary.

5. `_update_csv(self, scraped_data)`:
   - Updates the output CSV with scraped data, adding new headers dynamically if required.

6. `scrape_all(self)`:
   - Iterates over all links, scrapes data, and appends results to the output CSV.


## OOP Concepts Used
1. **Encapsulation**:
   - Data and methods related to scraping are encapsulated within the `SmartphoneScraper` class.

2. **Abstraction**:
   - Internal methods like `_read_links` and `_scrape_data` handle detailed operations, abstracted from the user.

3. **Reusability**:
   - The class can be reused for different input and output files, making it adaptable to various scenarios.

4. **Modularity**:
   - Each part of the scraping process is handled by a separate method, ensuring clean and maintainable code.

