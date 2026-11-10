import os
from dataclasses import dataclass
from typing import Iterable

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


@dataclass(frozen=True)
class TourRecord:
    external_id: str
    visit_date: str
    visitor_code: str


def submit_tours(records: Iterable[TourRecord]) -> list[dict[str, str]]:
    url = os.environ["ERP_URL"]
    username = os.environ["ERP_USERNAME"]
    password = os.environ["ERP_PASSWORD"]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    results: list[dict[str, str]] = []

    try:
        driver.get(url)
        wait.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, "[name='username']"))
        ).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "[name='password']").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "[data-form='tour']")))

        for record in records:
            try:
                date_input = wait.until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "[name='visit_date']"))
                )
                date_input.clear()
                date_input.send_keys(record.visit_date)
                driver.find_element(By.CSS_SELECTOR, "[name='visitor_code']").send_keys(
                    record.visitor_code
                )
                driver.find_element(By.CSS_SELECTOR, "[data-action='submit-tour']").click()
                wait.until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, "[role='status']"))
                )
                results.append({"external_id": record.external_id, "status": "submitted"})
            except Exception as exc:
                results.append(
                    {
                        "external_id": record.external_id,
                        "status": "failed",
                        "error": type(exc).__name__,
                    }
                )
        return results
    finally:
        driver.quit()

