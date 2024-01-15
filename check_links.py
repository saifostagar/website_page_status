import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all links from the page
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    
    return links

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

        results.append({'Link': full_url, 'Status': status})

    return results

def main():
    # Get input URL from the user
    input_url = input("Enter the URL of the home page: ")

    # Ensure the URL has the proper scheme (http or https)
    if not input_url.startswith(('http://', 'https://')):
        input_url = 'http://' + input_url

    # Get all links from the home page
    all_links = get_all_links(input_url)

    # Check for link status
    link_results = check_links(input_url, all_links)

    # Create a DataFrame
    df = pd.DataFrame(link_results)

    # Save to Excel file
    df.to_excel('link_status_output.xlsx', index=False)

    print("Results saved to 'link_status_output.xlsx'.")

if __name__ == "__main__":
    main()
