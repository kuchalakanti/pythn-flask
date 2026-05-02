import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

VM_IP    = os.environ.get("VM_IP", "127.0.0.1")
VM_PORT  = os.environ.get("VM_PORT", "5000")
BASE_URL = f"http://{VM_IP}:{VM_PORT}"

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # ✅ Hardcoded path — paste output of 'which chromedriver' here
    service = Service(executable_path="/usr/bin/chromedriver")
    driver  = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

@pytest.fixture
def driver():
    d = get_driver()
    yield d
    d.quit()

def test_add_employee_and_verify_in_list(driver):
    """
    Test Case 1:
    1. Open app using VM IP
    2. Enter employee name
    3. Click Add Employee
    4. Verify employee appears in list
    """
    print(f"\n Opening: {BASE_URL}")
    driver.get(BASE_URL)
    assert "Employee Directory" in driver.title, f"Wrong title: {driver.title}"

    employee_name = "John Jenkins"
    name_input = driver.find_element(By.ID, "employeeName")
    name_input.clear()
    name_input.send_keys(employee_name)

    add_button = driver.find_element(By.XPATH, "//button[text()='Add Employee']")
    add_button.click()

    time.sleep(2)

    employee_list = driver.find_element(By.ID, "employeeList")
    list_items    = employee_list.find_elements(By.TAG_NAME, "li")
    names_in_list = [item.text for item in list_items]

    print(f"\n Employees in list: {names_in_list}")
    assert employee_name in names_in_list, \
        f"'{employee_name}' NOT found! List has: {names_in_list}"

    print(f"\n✅ PASS: '{employee_name}' found in list!")

def test_employee_list_loads_on_page_open(driver):
    """
    Test Case 2:
    Verify employee list is visible on page load
    """
    print(f"\n Opening: {BASE_URL}")
    driver.get(BASE_URL)

    employee_list = driver.find_element(By.ID, "employeeList")
    assert employee_list.is_displayed(), "❌ Employee list not visible!"

    print("\n✅ PASS: Employee list visible on page load!")
