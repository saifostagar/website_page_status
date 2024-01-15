import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all links from the page
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    
    return links

def is_internal_link(base_url, link):
    # Check if the link is internal to the base URL
    return urljoin(base_url, link).startswith(base_url)

def check_links(base_url, links):
    results = []

    for link in links:
        full_url = urljoin(base_url, link)
        try:
            response = requests.head(full_url)
            response.raise_for_status()
            status = response.status_code
        except requests.RequestException as e:
            status = str(e)

        link_type = 'Internal' if is_internal_link(base_url, link) else 'External'

        results.append({'Link': full_url, 'Status': status, 'Type': link_type})

    return results

def generate_output_file_name(base_url):
    website_name = urlparse(base_url).hostname
    version = 1

    while True:
        output_file = f"{website_name}_link_status_output_v{version}.xlsx"
        if not os.path.exists(output_file):
            return output_file
        version += 1

def main():
    # Get input URL from the user
    input_url = input("Enter the URL of the home page: ")

    # Ensure the URL has the proper scheme (http or https)
    if not input_url.startswith(('http://', 'https://')):
        input_url = 'http://' + input_url

    # Get the output file name with version
    output_file = generate_output_file_name(input_url)

    # Get all links from the home page
    all_links = get_all_links(input_url)

    # Check for link status
    link_results = check_links(input_url, all_links)

    # Create a DataFrame
    df = pd.DataFrame(link_results)

    # Save to Excel file
    df.to_excel(output_file, index=False)

    print(f"Results saved to '{output_file}'.")

if __name__ == "__main__":
    main()
