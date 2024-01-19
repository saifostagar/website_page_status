import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def get_all_links(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract all links from the page
        links = [a.get('href') for a in soup.find_all(['a', 'img', 'link'], href=True)]
        return links
    except requests.RequestException as e:
        print(f"Error getting links from {url}: {str(e)}")
        return []

def is_internal_link(base_url, link):
    # Check if the link is internal to the base URL
    return urljoin(base_url, link).startswith(base_url)

def check_links(base_url, links, headers=None):
    results = []

    for link in links:
        full_url = urljoin(base_url, link)
        try:
            response = requests.get(full_url, headers=headers)
            response.raise_for_status()
            status = response.status_code
        except requests.RequestException as e:
            status = str(e)
            print(f"Error checking link: {full_url} - {status}")

        link_type = 'Internal' if is_internal_link(base_url, link) else 'External'

        results.append({'Link': full_url, 'Status': status, 'Type': link_type})

    return results

def generate_output_file_name(base_url, script_dir):
    website_name = urlparse(base_url).hostname
    version = 1

    while True:
        output_folder = os.path.join(script_dir, 'Reports')
        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, f"{website_name}_link_status_output_v{version}.xlsx")
        if not os.path.exists(output_file):
            return output_file
        version += 1

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get input URL from the user
    input_url = input("Enter the URL of the home page: ")

    # Ensure the URL has the proper scheme (http or https)
    if not input_url.startswith(('http://', 'https://')):
        input_url = 'https://' + input_url

    # Set a user-agent header to make the request look like a regular browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Get the output file name with version
    output_file = generate_output_file_name(input_url, script_dir)

    # Get all links from the home page
    all_links = get_all_links(input_url, headers=headers)

    # Check for link status
    link_results = check_links(input_url, all_links, headers=headers)

    # Create a DataFrame
    df = pd.DataFrame(link_results)

    # Save to Excel file
    df.to_excel(output_file, index=False)

    print(f"Results saved to '{output_file}'.")

if __name__ == "__main__":
    main()
