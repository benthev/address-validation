from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import csv

# Set up the Selenium WebDriver (Ensure you have the correct driver for your browser)
driver = webdriver.Chrome()

input_file = "addresses.csv"
output_file = "addresses_valid.csv"
vars_to_save = ["identifier", "mailingaddress1", "mailingaddress2", "mailingcity",
                "mailingstate", "mailingzip", "status", "address", "is_address_valid"]

with open(input_file, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)  # Read CSV as a dictionary
    # Create a list to store updated rows
    updated_rows = []
    for row in reader:
        street_input = row.get("mailingaddress1")
        apt_input = row.get("mailingaddress2")
        city_input = row.get("mailingcity")
        state_input = row.get("mailingstate")
        zip_input = row.get("mailingzip")
        row = {k: v for k, v in row.items() if k in vars_to_save}

        if street_input:
            try:
                # Navigate to the USPS ZIP Code lookup page
                driver.get(
                    "https://tools.usps.com/zip-code-lookup.htm?byaddress")

                # Wait until the form fields are available
                wait = WebDriverWait(driver, 10)
                street_field = wait.until(
                    EC.presence_of_element_located((By.ID, "tAddress")))
                if apt_input:
                    apt_field = driver.find_element(By.ID, "tCity")
                city_field = driver.find_element(By.ID, "tApt")
                state_field = driver.find_element(By.ID, "tState")
                zip_field = driver.find_element(By.ID, "tZip-byaddress")
                submit_button = driver.find_element(By.ID, "zip-by-address")

                # Input data
                street_field.send_keys(street_input)
                if apt_input:
                    apt_field.send_keys(apt_input)
                city_field.send_keys(city_input)
                state_field.send_keys(state_input)
                zip_field.send_keys(zip_input)

                # Submit the form
                submit_button.click()

                # Parse the page source with BeautifulSoup
                wait = WebDriverWait(driver, 10)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                try:
                    result_box = wait.until(EC.presence_of_element_located(
                        (By.CLASS_NAME, "zipcode-result-address")))
                    result_text = result_box.text.strip()
                    row["status"] = "success"
                    row["address"] = result_text
                    row["is_address_valid"] = True
                except:
                    print('No zipcode result address')
                    print(street_input)
                    row["status"] = "error"
                    row["is_address_valid"] = False
                pass

                # Check for server error message
                # error_div = soup.find(
                #     "div", class_="server-error address-tAddress help-block")
                # row["status"] = "error"
                # row["message"] = error_div.text.strip()
                updated_rows.append(row)
            except:
                print('Error processing')
                print(street_input + " " + apt_input + " " +
                      city_input + " " + state_input + " " + zip_input)
                pass

                # # Save the result as a JSON file
                # with open("usps_zip_lookup_result.json", "w") as json_file:
                #     json.dump(result_data, json_file, indent=4)

                # print(json.dumps(result_data, indent=4))

# Write the updated rows to a new CSV file
with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
    fieldnames = vars_to_save
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()  # Write headers
    writer.writerows(updated_rows)  # Write updated data

print(f"Updated CSV saved as {output_file}")

driver.quit()
