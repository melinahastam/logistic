"""Generic Selenium worker with placeholder selectors and no production details."""

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


def submit_demo_tours(records: Iterable[TourRecord]) -> list[dict[str, str]]:
    url = os.environ["DEMO_ERP_URL"]
    username = os.environ["DEMO_ERP_USERNAME"]
    password = os.environ["DEMO_ERP_PASSWORD"]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    results: list[dict[str, str]] = []

    try:
        driver.get(url)
        wait.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, "[data-demo='username']"))
        ).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "[data-demo='password']").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "[data-demo='login']").click()
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "[data-demo='tour-form']")))

        for record in records:
            try:
                date_input = wait.until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "[data-demo='visit-date']"))
                )
                date_input.clear()
                date_input.send_keys(record.visit_date)
                driver.find_element(By.CSS_SELECTOR, "[data-demo='visitor-code']").send_keys(
                    record.visitor_code
                )
                driver.find_element(By.CSS_SELECTOR, "[data-demo='submit-tour']").click()
                wait.until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, "[data-demo='success']"))
                )
                results.append({"external_id": record.external_id, "status": "submitted"})
            except Exception as exc:  # Real adapters map known Selenium exceptions separately.
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

