import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

def check_broken_link(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.head(url, headers=headers, allow_redirects=True)
        
        if response.status_code == 403:
            return True, 'Forbidden'
        else:
            return response.status_code >= 200, str(response.status_code)

    except requests.RequestException:
        return True, 'Error'

def check_alt_text(link, headers):
    try:
        response_link = requests.get(link, headers=headers)
        soup_link = BeautifulSoup(response_link.content, 'x')
        images = soup_link.find_all('img', alt=False)
        return [str(img) for img in images]

    except requests.RequestException:
        return ['Error']

def is_image_link(link):
    # Check if the link ends with a common image file extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
    return any(link.lower().endswith(ext) for ext in image_extensions)

def process_site(site_row):
    site_name = site_row['sitemap URL']
    site_url = site_row['sitemap URL']
    check_broken_link_flag = site_row['checkBrokenLink'] == 'Yes'
    find_missing_alt_flag = site_row['FindMissingAlt'] == 'Yes'

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(site_url, headers=headers)

        # Use 'lxml-xml' parser for XML content
        soup = BeautifulSoup(response.content, 'lxml')

        if 'xml' in response.headers['content-type']:
            # Extract links from XML content
            links = [link.text for link in soup.find_all('loc') if not is_image_link(link.text)]
        else:
            # Assume it's an HTML page and extract links accordingly
            links = [link['href'] for link in soup.find_all('a', href=True)]

        visited_links = set()
        broken_links = []

        for link in links:
            absolute_url = urljoin(site_url, link)

            # Check if the link has been visited to avoid redundant requests
            if absolute_url not in visited_links:
                visited_links.add(absolute_url)

                # Process each link
                print(f"Processing link: {absolute_url}")

                # Check for broken links if the flag is set
                if check_broken_link_flag and check_broken_link(absolute_url)[0]:
                    status = check_broken_link(absolute_url)[1]
                    broken_links.append((absolute_url, site_url, status))

                # Check for missing alt text on images if the flag is set
                if find_missing_alt_flag:
                    missing_alt_images = check_alt_text(absolute_url, headers)
                    for img_detail in missing_alt_images:
                        broken_links.append((img_detail, absolute_url, 'Missing Alt Text'))

    except requests.RequestException as e:
        print(f"Error processing site {site_name}: {e}")

    return broken_links

def main(input_file_path):
    input_df = pd.read_excel(input_file_path)

    for index, site_row in input_df.iterrows():
        site_name = site_row['sitemap URL']
        # Replace invalid characters in site_name with underscores
        site_name_cleaned = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in site_name)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file_name = f"output_{timestamp}_{site_name_cleaned}.xlsx"

        check_broken_link_flag = site_row['checkBrokenLink'] == 'Yes'
        find_missing_alt_flag = site_row['FindMissingAlt'] == 'Yes'

        if check_broken_link_flag or find_missing_alt_flag:
            broken_links = process_site(site_row)

            # Save broken links to an Excel file
            output_df = pd.DataFrame(broken_links, columns=['Link', 'Parent Page', 'Status'])
            output_df.to_excel(output_file_name, index=False)
            print(f"Broken links saved to {output_file_name}")
        else:
            print(f"No checks performed for site {site_name} as checkBrokenLink or FindMissingAlt is not marked as 'Yes'")
            
if __name__ == "__main__":
    input_file_path = "URLsBook.xlsx"
    main(input_file_path)
