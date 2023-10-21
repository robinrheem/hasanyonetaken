import threading
import time
from datetime import datetime
import re
import csv
from django.core.management.base import BaseCommand
from professor.models import Professor, Review
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class Command(BaseCommand):
    help = "Scrape detail information of each professor"

    def extract_thumbs(self, detail):
        for i, info in enumerate(detail):
            if info == "Helpful":
                return int(detail[i + 1]), int(detail[i + 2])
        return 0, 0

    def extract_tags(self, detail):
        return [tag for tag in detail if tag.isupper() and tag not in ["QUALITY", "DIFFICULTY", detail[4]]]

    def extract_info(self, detail, key):
        for info in detail:
            if "For Credit:" in info  and key == "credit":
                info_value = info.split(":")[1].strip()
                if info_value in ["Yes", "No", "N/A"]:
                    return info_value
            if "Attendance:" in info and key == "attendance":
                info_value = info.split(":")[1].strip()
                if info_value in ["Mandatory", "Not Mandatory", "N/A"]:
                    return info_value
            if "Would Take Again:" in info and key == 'take_again':
                info_value = info.split(":")[1].strip()
                if info_value in ["Yes", "No", "N/A"]:
                    return info_value
            if "Grade:" in info and key == "grade":
                return info.split(":")[1].strip()
            if "Textbook:" in info and key == "textbook":
                info_value = info.split(":")[1].strip()
                if info_value in ["Yes", "No", "N/A"]:
                    return info_value

    def extract_comment(self, rating_element):
        rating_detail = rating_element.inner_text().split("\n")

        self.stdout.write(f"{len(rating_detail)}")
        self.stdout.write(f"{rating_detail}")
        rating = rating_detail[1]
        difficulty = rating_detail[3]
        course = rating_detail[4]
        created_at_raw = rating_detail[5]
        cleaned_date_str = re.sub(r'(st|nd|rd|th)', '', created_at_raw)
        created_at = datetime.strptime(cleaned_date_str, '%b %d, %Y')
        for_credit = self.extract_info(rating_detail, "credit")
        attendance = self.extract_info(rating_detail, "attendance")
        take_again = self.extract_info(rating_detail, "take_again")
        grade = self.extract_info(rating_detail, "grade")
        has_textbook = self.extract_info(rating_detail, "textbook")
        helpful, not_helpful = self.extract_thumbs(rating_detail)
        tags = self.extract_tags(rating_detail)
        review_index = 6
        if for_credit:
            review_index += 1
        if attendance:
            review_index += 1
        if take_again:
            review_index += 1
        if grade:
            review_index += 1
        if attendance:
            review_index += 1
        review = rating_detail[review_index]
        self.stdout.write(f"Course: {course}")
        self.stdout.write(f"Rating: {rating}")
        self.stdout.write(f"Created: {created_at}")
        self.stdout.write(f"Difficulty: {difficulty}")
        self.stdout.write(f"Review: {review}")
        self.stdout.write(f"Tags: {tags}")
        self.stdout.write(f"For Credit: {for_credit}")
        self.stdout.write(f"Attendance: {attendance}")
        self.stdout.write(f"Take again: {take_again}")
        self.stdout.write(f"Grade: {grade}")
        self.stdout.write(f"Textbook: {has_textbook}")
        self.stdout.write(f"Helpful: {helpful}")
        self.stdout.write(f"Not Helpful: {not_helpful}")
        return Review(
            rating=rating,
            difficulty=difficulty,
            course=course,
            comment=review,
            tags=tags,
            helpful=helpful,
            not_helpful=not_helpful,
            take_again=take_again,
            for_credit=for_credit,
            has_textbook=has_textbook,
            attendance_mandatory=attendance,
            grade=grade,
            created_at=created_at
        )

    def extract_detail(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=360*1000)
            professor = None
            parsed_reviews = []
            try:
                self.stdout.write("Close cookie popup")
                page.locator('"Close"').click()
                name = page.locator('xpath=//*[contains(@class, "NameTitle__Name")]').inner_text()
                self.stdout.write(f"{name}")
                title = page.locator('xpath=//*[contains(@class, "NameTitle__Title")]').inner_text()
                department, college = re.search(r"Professor in the (.+?) department at (.+)$", title).groups()
                self.stdout.write(f"Department: {department}, College: {college}")

                professor = Professor(full_name=name, rmp_url=url, university=college, department=department)

                self.stdout.write("Clicking 'Load More Ratings' button")
                page.locator('"Load More Ratings"').click()
                self.stdout.write("Waiting for load ...")
                retry = 0
                while True:
                    loaded_reviews = page.locator('xpath=//*[contains(@class, "Rating__StyledRating")]').all()
                    self.stdout.write(f"Loaded {len(loaded_reviews)} reviews")
                    time.sleep(2)
                    if not page.locator('"Load More Ratings"').is_visible():
                        self.stdout.write("Cannot locate 'Load More Ratings' button")
                        self.stdout.write(f"Retrying ... {retry}")
                        retry += 1
                        if retry > 5:
                            break
                        time.sleep(1)
                        continue
                    page.locator('"Load More Ratings"').click()
                reviews = page.locator('xpath=//*[contains(@class, "Rating__StyledRating")]').all()
                self.stdout.write(f"Scraping {len(reviews)} reviews")
                for review in reviews:
                    parsed_reviews.append(self.extract_comment(review))
                self.stdout.write(f"Scraping done")
                browser.close()
            except PlaywrightTimeoutError:
                print("Timeout!")
                browser.close()
            return professor, parsed_reviews

    def handle(self, *args, **options):
        def save_data(professor, reviews):
            professor.save()
            for review in reviews:
                review.professor = professor
                review.save()

        with open("professor_ids.csv") as f:
            reader = csv.reader(f)
            for url in reader:
                professor, reviews = self.extract_detail(url[0])
                threading.Thread(target=save_data, args=(professor,reviews,)).start()
                time.sleep(2)
