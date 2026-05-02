import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Get VM IP from environment variable — Jenkins will pass this
VM_IP   = os.environ.get("VM_IP", "127.0.0.1")
VM_PORT = os.environ.get("VM_PORT", "5000")
BASE_URL = f"http://{VM_IP}:{VM_PORT}"

@pytest.fixture
def driver():
    """Setup Chrome in headless mode (required for CI/CD — no GUI on Jenkins server)"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")           # No GUI needed
    chrome_options.add_argument("--no-sandbox")         # Required in CI
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

def test_add_employee_and_verify_in_list(driver):
    """
    Test Case:
    1. Open application using VM IP
    2. Enter employee name
    3. Click Add Employee
    4. Verify employee appears in list
    """
    # Step 1: Open the application
    driver.get(BASE_URL)
    assert "Employee Directory" in driver.title, "Page title mismatch!"

    # Step 2: Enter employee name
    employee_name = "John Jenkins"
    name_input = driver.find_element(By.ID, "employeeName")
    name_input.clear()
    name_input.send_keys(employee_name)

    # Step 3: Click Add Employee button
    add_button = driver.find_element(By.XPATH, "//button[text()='Add Employee']")
    add_button.click()

    # Wait for the list to update
    time.sleep(2)

    # Step 4: Verify employee appears in the list
    employee_list = driver.find_element(By.ID, "employeeList")
    list_items = employee_list.find_elements(By.TAG_NAME, "li")
    names_in_list = [item.text for item in list_items]

    assert employee_name in names_in_list, \
        f"'{employee_name}' not found in employee list! Found: {names_in_list}"

    print(f"\n✅ PASS: Employee '{employee_name}' successfully added and verified in list!")

def test_employee_list_loads_on_page_open(driver):
    """
    Test Case:
    Verify that the employee list section is visible when page loads
    """
    driver.get(BASE_URL)

    employee_list = driver.find_element(By.ID, "employeeList")
    assert employee_list.is_displayed(), "Employee list is not visible on page!"

    print("\n✅ PASS: Employee list section is visible on page load!")
