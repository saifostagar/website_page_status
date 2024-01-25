import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import time

def get_links_from_excel(file_path):
    df = pd.read_excel(file_path, header=None)
    return df.iloc[:, 0].dropna().tolist()

def get_status(url, parent_link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        soup = BeautifulSoup(response.text, 'html.parser')
        parent_title = soup.title.text.strip() if soup.title else 'N/A'

        return status_code, parent_title
    except Exception as e:
        return str(e), parent_link

def main(input_excel_path, output_excel_path):
    links = get_links_from_excel(input_excel_path)

    results = []
    for link in tqdm(links, desc="Checking links"):
        parent_link = 'N/A'
        absolute_link = link
        status, parent_title = get_status(absolute_link, parent_link)
        results.append([absolute_link, status, parent_title])
        time.sleep(1)  # Add a delay of 1 second between requests

    result_df = pd.DataFrame(results, columns=['Link', 'Status', 'Parent'])
    result_df.to_excel(output_excel_path, index=False)
    print(f"Results saved to {output_excel_path}")

if __name__ == "__main__":
    input_excel_path = "page-sitemap_links_version_1.xlsx"  # Replace with your input Excel file path
    output_excel_path = "output_results.xlsx"  # Replace with your desired output Excel file path

    main(input_excel_path, output_excel_path)
