import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import os

# Function to fetch and parse the XML content
def get_xml_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    elif response.status_code == 403:
        print("Access to the XML content is forbidden (403). Check if the website allows access.")
    else:
        raise Exception(f"Failed to fetch XML content. Status code: {response.status_code}")

# Function to extract links from XML content
def extract_links(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')
    links = [loc.text for loc in soup.find_all('loc')]
    return links

# Function to save links to an Excel file
def save_to_excel(links, excel_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Links"

    for index, link in enumerate(links, start=1):
        ws.cell(row=index, column=1, value=link)

    wb.save(excel_file)
    print(f"Links saved to {excel_file}")

# Function to generate a unique output file name
def generate_output_filename(site_name, version):
    base_filename = f"{site_name}_links_version_{version}.xlsx"
    return base_filename

# Accept XML page link as input
xml_url = input("Enter the URL of the XML page: ")

# Extract site name from the URL
site_name = os.path.splitext(os.path.basename(xml_url))[0]

# Generate the initial output Excel file name
excel_version = 1
excel_file = generate_output_filename(site_name, excel_version)

# Check if the file already exists, increment version if necessary
while os.path.exists(excel_file):
    excel_version += 1
    excel_file = generate_output_filename(site_name, excel_version)

# Fetch and parse XML content
xml_content = get_xml_content(xml_url)

# If XML content is fetched successfully, proceed to extract and save links
if xml_content:
    links = extract_links(xml_content)
    save_to_excel(links, excel_file)
