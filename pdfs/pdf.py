import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

def scrape_pdfs_from_url(url, download_folder="downloaded_pdfs"):
    """
    Scrape all PDF files from a given URL and save them to a folder.
    
    Args:
        url (str): The URL to scrape for PDFs
        download_folder (str): Folder to save downloaded PDFs
    """
    
    # Create download directory if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Fetch the webpage content
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links that point to PDF files
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                # Convert relative URL to absolute URL
                full_url = urljoin(url, href)
                pdf_links.append(full_url)
        
        print(f"Found {len(pdf_links)} PDF(s)")
        
        # Download each PDF
        downloaded_files = []
        for i, pdf_url in enumerate(pdf_links):
            try:
                # Get the PDF filename from the URL
                parsed_url = urlparse(pdf_url)
                pdf_filename = os.path.basename(parsed_url.path)
                
                # If the PDF doesn't have a proper name, generate one
                if not pdf_filename or not pdf_filename.endswith('.pdf'):
                    pdf_filename = f"document_{i+1}.pdf"
                
                # Full path to save the PDF
                save_path = os.path.join(download_folder, pdf_filename)
                
                # Download the PDF
                print(f"Downloading ({i+1}/{len(pdf_links)}): {pdf_filename}")
                pdf_response = requests.get(pdf_url, headers=headers, timeout=15)
                pdf_response.raise_for_status()
                
                # Save the PDF
                with open(save_path, 'wb') as f:
                    f.write(pdf_response.content)
                
                downloaded_files.append(save_path)
                print(f"Saved: {save_path}")
                
                # Be polite - add a small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Failed to download {pdf_url}: {str(e)}")
        
        print(f"\nDownload complete! {len(downloaded_files)} PDF(s) saved to '{download_folder}' folder.")
        return downloaded_files
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

# Example usage - REPLACE THIS URL WITH YOUR TARGET URL
if __name__ == "__main__":
    target_url = "https://www.biat.com.tn/recherches-et-analyses/notes-de-recherche"  # <-- REPLACE WITH YOUR URL
    scrape_pdfs_from_url(target_url)