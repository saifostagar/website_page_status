import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


def get_contents(url):
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
    
def remove_image_links(links):
    # List of common image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']

    # Filter out links that end with image file extensions
    filtered_links = [link for link in links if not any(link.lower().endswith(ext) for ext in image_extensions)]

    return filtered_links


def process_sitemap(sitemap_link):
    contents = get_contents(sitemap_link)
    if contents:
        soup = BeautifulSoup(contents, 'html.parser')
        if sitemap_link.endswith(".xml"):
            links = [loc.text for loc in soup.find_all('loc')]
            print("yo0000 its xml")
        else:
            links = [a['href'] for a in soup.find_all('a', href=True)]
            print("its html blah")
        filtered_links = remove_image_links(links)
        for link in links:
            print(link)
        return filtered_links
    else:
        print("Unable to extract xml content from xml site :D")


def get_all_links(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract all links from the page
        links = []
        # Extract links from 'a' tags
        links += [a.get('href') for a in soup.find_all('a', href=True) if a.get('href')]
        # Extract links from 'img' tags
        links += [img.get('src') for img in soup.find_all('img', src=True) if img.get('src')]
        # Extract links from 'link' tags
        links += [link.get('href') for link in soup.find_all('link', href=True) if link.get('href')]
        # Extract links from 'iframe' tags
        links += [iframe.get('src') for iframe in soup.find_all('iframe', src=True) if iframe.get('src')]
        return links
    except requests.RequestException as e:
        print(f"Error getting links from {url}: {str(e)}")
        return []
    
def check_links(parent_link, links, headers=None):
    results = []

    for link in links:
        try:
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            status = response.status_code
            if response.status_code >=201:
                results.append((link, parent_link, status))
            
        except requests.RequestException as e:
            status = str(e)
            print(f"Error checking link: {link} - {status}")
            results.append((link, parent_link, status))


    return results



def check_broken_link(extracted_links):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    results=[]
    #itarate all link and find all link present there
    for link in extracted_links:
        # Get all links from the home page
        all_links = get_all_links(link, headers=headers)

        link_results = check_links(link, all_links, headers=headers)
        results=results+link_results
    return results

        


def missing_alt_check(extracted_links):
    print("missing")
    





def main(input_file_path):
    input_df = pd.read_excel(input_file_path)

    for index, site_row in input_df.iterrows():
        site_name = site_row['sitemap URL']
        # Replace invalid characters in site_name with underscores
        site_name_cleaned = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in site_name)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        linkcheck_op_file_name = f"link_output_{timestamp}_{site_name_cleaned}.xlsx"
        missing_alt_op_file_name = f"alt_output_{timestamp}_{site_name_cleaned}.xlsx"

        check_broken_link_flag = site_row['checkBrokenLink'] == 'Yes'
        find_missing_alt_flag = site_row['FindMissingAlt'] == 'Yes'

        if check_broken_link_flag or check_broken_link_flag:
            #extract links from given link/sitemap
            extracted_links = process_sitemap(site_row['sitemap URL'])
        

        if check_broken_link_flag:
            broken_links=check_broken_link(extracted_links)
            
            output_df = pd.DataFrame(broken_links, columns=['Link', 'Parent Page', 'Status'])
            
            output_df.to_excel(linkcheck_op_file_name, index=False)
            print(f"Broken links saved to {linkcheck_op_file_name}")
        else:
            print(f"No Broken Link checks performed for site {site_name} as checkBrokenLink is not marked as 'Yes'")
        

        if find_missing_alt_flag:
            missing_alt_images=missing_alt_check(extracted_links)
            
            output_df = pd.DataFrame(missing_alt_images, columns=['Link of Image', 'Parent Page', 'Status'])
            
            output_df.to_excel(missing_alt_op_file_name, index=False)
            print(f"Missing Alt Images List saved to {missing_alt_op_file_name}")
        else:
            print(f"No Missing alt Images checks performed for site {site_name} as FindMissingAlt is not marked as 'Yes'")


if __name__ == "__main__":
    input_file_path = "URLsBook.xlsx"
    main(input_file_path)