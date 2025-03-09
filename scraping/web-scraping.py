import requests
from bs4 import BeautifulSoup
import markdownify
import os
import json

urls = {
    "visit-pittsburgh-thingstodo":"https://www.visitpittsburgh.com/things-to-do/pittsburgh-sports-teams/",
    "pirates": "https://www.mlb.com/pirates",
    "steelers": "https://www.steelers.com/",
    "penguins": "https://www.nhl.com/penguins/",
    "banana-split": "https://bananasplitfest.com/",
    "little-italy":"https://littleitalydays.com/",
    "restaurant-week":"https://pittsburghrestaurantweek.com/",
    "taco-festival":"https://pittsburghrestaurantweek.com/",
    "picklesburgh":"https://www.picklesburgh.com/",
    "visit-pittsburgh-foodfestivals":"https://www.visitpittsburgh.com/events-festivals/food-festivals/",
    "carnegie-museums": "https://carnegiemuseums.org/",
    "heinz-history-center":"https://www.heinzhistorycenter.org/",
    "the-frick":"https://www.thefrickpittsburgh.org/",
    "wiki-museum-list":"https://en.wikipedia.org/wiki/List_of_museums_in_Pittsburgh",
    "symphony":"https://www.pittsburghsymphony.org/",
    "opera":"https://pittsburghopera.org/",
    "cultural-trust":"https://trustarts.org/",
    "cmu-events-calendar":"https://events.cmu.edu/",
    "cmu-in-person-events":"https://www.cmu.edu/engage/alumni/events/campus/index.html",
    "city-paper-events":"https://www.pghcitypaper.com/pittsburgh/EventSearch?v=d",
    "downtown-events-calendar":"https://downtownpittsburgh.com/events/",
    "pittsburgh-events-calendar":"https://pittsburgh.events/",
    "cmu-about":"https://www.cmu.edu/about/",
    "tax-forms":"https://www.pittsburghpa.gov/City-Government/Finances-Budget/Taxes/Tax-Forms",
    "visit-pittsburgh-homepage":"https://www.visitpittsburgh.com/",
    "britannica":"https://www.britannica.com/place/Pittsburgh",
    "the-city-of-pittsburgh":"https://www.pittsburghpa.gov/Home",
    "wiki-pittsburgh":"https://en.wikipedia.org/wiki/Pittsburgh",
    "wiki-history-of-pittsburgh":"https://en.wikipedia.org/wiki/History_of_Pittsburgh"
    }



BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
ERRORS_DIR = os.path.join(BASE_DIR, "errors")


raw_html_directory = os.path.join(DATA_DIR, "raw/html/")

markdown_directory = os.path.join(DATA_DIR, "processed/markdown/")

text_directory = os.path.join(DATA_DIR, "processed/text/")

links_directory = os.path.join(DATA_DIR, "processed/extracted_links/")

error_log = os.path.join(ERRORS_DIR, "errors/scraping_errors.json")

# markdown_directory = "data/processed/markdown/"

# text_directory = "data/processed/text/"

# links_directory = "data/processed/extracted_links/"

os.makedirs(raw_html_directory, exist_ok=True) #ensuring these directories exist
os.makedirs(markdown_directory, exist_ok=True)
os.makedirs(text_directory, exist_ok=True)
os.makedirs(links_directory, exist_ok=True) 
os.makedirs(error_log, exist_ok = True)

scraping_errors = {}

def scrape(url, name):
    header = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=header)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, "html.parser")
        if not soup.find("body"):
            print(f"Body not found for {name}")
            scraping_errors[name] = "Empty or Invalid HTML response."
            return None
        raw_html_path = os.path.join(raw_html_directory, name + ".html")
        with open(raw_html_path, "w", encoding = "utf-8") as f:
            f.write(soup.prettify())
        print(f"Raw HTML Scraped! : {name}")

        return soup
    else:
        print(f"Failed to retrieve {name}. Status code: {response.status_code}")
        scraping_errors[name] = f"HTTP {response.status_code}"
        return None
    
def extract_text(soup, name):
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator="\n", strip = True)
    text_path = os.path.join(text_directory, name + ".txt")
    with open(text_path, "w", encoding = "utf-8") as f:
        f.write(text)
    print(f"Text extracted and saved for file {name}!")

def extract_links(soup, name):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        link = a_tag["href"]
        if link.startswith("http"):
            links.add(link)
    
    links_path = os.path.join(links_directory, name + ".json")
    with open(links_path, "w", encoding = "utf-8") as f:
        json.dump(list(links), f, indent = 4)
    print(f"Links extracted and saved for file {name}!")
    
    #return links

def convert_to_markdown(html_content, name):
    markdown_txt = markdownify.markdownify(html_content, heading_style = "ATX")
    md_path = os.path.join(markdown_directory, name + ".md")
    with open(md_path, "w", encoding = "utf-8") as f:
        f.write(markdown_txt)
    print(f"Markdown created and saved for file {name}!")


all_links = {}

count = 0
    
for key, url in urls.items():
    soup = scrape(url, key)
    if soup:
        count += 1
        extract_text(soup, key)
        extract_links(soup, key)
        convert_to_markdown(soup.prettify(), key)

if scraping_errors:
    with open(error_log, "w", encoding = "utf-8") as f:
        json.dump(scraping_errors, f, indent = 4)
    print(f"Some errors occurred during scraping.. Pls check {error_log} for details.")

print("All pages scraped, processed and saved!")
print("Count of pages: ", count)