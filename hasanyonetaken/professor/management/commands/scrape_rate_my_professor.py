import time
import csv
from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class Command(BaseCommand):
    help = "Scrape all ratings and comments of each professor"

    def handle(self, *args, **options):
        school_id = "1967"  # De Anza College
        url = f"https://www.ratemyprofessors.com/search/professors/{school_id}?q=*"
        professor_ids = set()

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=360*1000)
            try:
                self.stdout.write("Close cookie popup")
                page.locator('"Close"').click()
                self.stdout.write("Clicking 'Show More' button")
                page.locator('"Show More"').click()
                self.stdout.write("Waiting for load ...")
                retry = 0
                while True:
                    time.sleep(2)
                    links = set(page.eval_on_selector_all("a", '''elements => elements.map(a => a.href).filter(href => href.includes("/professor/"))'''))
                    self.stdout.write(f"Professor count: {len(professor_ids)}")
                    with open("professor_ids.csv", "a+") as f:
                        writer = csv.writer(f)
                        for row in links.difference(professor_ids):
                            writer.writerow([row])
                        professor_ids.update(links)
                    if not page.locator('"Show More"').is_visible():
                        self.stdout.write("Cannot locate 'Show More' button")
                        self.stdout.write(f"Retrying ... {retry}")
                        retry += 1
                        if retry > 10:
                            break
                    self.stdout.write("Clicking 'Show More' button")
                    page.locator('"Show More"').click()
            except PlaywrightTimeoutError:
                print("Timeout!")
                browser.close()
            self.stdout.write(f"Loaded {len(professor_ids)} professor ids")
