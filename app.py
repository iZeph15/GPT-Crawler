import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
import ebooklib
from ebooklib import epub
import PyPDF2
from io import BytesIO

# Function to convert Excel file to JSON
def convert_excel_to_json(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        return df.to_json(orient='records')
    except Exception as e:
        return {'error': str(e)}

# Initialize a headless Chrome browser session
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser

# Function to scrape a single URL
def scrape_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example of extracting data: getting texts, images, and links
        texts = soup.get_text()
        images = [img['src'] for img in soup.find_all('img') if img.get('src')]
        links = [a['href'] for a in soup.find_all('a') if a.get('href')]

        return {
            'url': url,
            'text': texts,
            'images': images,
            'links': links
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

# Function to crawl a single URL with Selenium
def selenium_scrape_url(url, browser):
    try:
        browser.get(url)
        # If the page has JavaScript that dynamically generates links, you might need to wait
        # Here we wait up to 10 seconds for the page to load (customize as needed)
        browser.implicitly_wait(10)

        # Extracting all links from the page
        links_elements = browser.find_elements(By.TAG_NAME, 'a')
        links = [link.get_attribute('href') for link in links_elements if link.get_attribute('href')]

        # De-duplicate links
        unique_links = list(set(links))
        return unique_links
    except Exception as e:
        return {'url': url, 'error': str(e)}

def merge_pdfs(uploaded_files):
    merged_pdf = BytesIO()
    pdf_writer = PyPDF2.PdfWriter()  # Updated to use PdfWriter

    for uploaded_file in uploaded_files:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    pdf_writer.write(merged_pdf)
    merged_pdf.seek(0)  # Reset pointer to the beginning of the file
    return merged_pdf

# Function to scrape a single URL
def selenium_scrape_url(url, browser, max_pages=20):
    try:
        crawled_links = set()
        current_page = 0

        while current_page < max_pages:
            browser.get(url)
            browser.implicitly_wait(10)

            # Extracting all links from the page
            links_elements = browser.find_elements(By.TAG_NAME, 'a')
            links = [link.get_attribute('href') for link in links_elements if link.get_attribute('href')]
            crawled_links.update(links)

            # Find the 'next page' link and update the URL, break if not found
            next_page_element = browser.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(@rel, 'next')]")
            if next_page_element:
                url = next_page_element.get_attribute('href')
                current_page += 1
            else:
                break

        return list(crawled_links)
    except Exception as e:
        return {'url': url, 'error': str(e)}
    
# Function to scrape multiple pages of a URL with Selenium
def selenium_scrape_multiple_pages(url, browser, max_pages=20):
    try:
        crawled_links = set()
        current_page = 0

        while current_page < max_pages:
            browser.get(url)
            browser.implicitly_wait(10)

            # Extracting all links from the page
            links_elements = browser.find_elements(By.TAG_NAME, 'a')
            links = [link.get_attribute('href') for link in links_elements if link.get_attribute('href')]
            crawled_links.update(links)

            # Find the 'next page' link and update the URL, break if not found
            next_page_element = browser.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(@rel, 'next')]")
            if next_page_element:
                url = next_page_element.get_attribute('href')
                current_page += 1
            else:
                break

        return list(crawled_links)
    except Exception as e:
        return {'url': url, 'error': str(e)}
    
def convert_csv_to_json(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, delimiter='|')
        return df.to_dict(orient='records')  # Changed to to_dict
    except Exception as e:
        return {'error': str(e)}

def extract_data_from_html(uploaded_file):
    try:
        soup = BeautifulSoup(uploaded_file, 'html.parser')
        texts = soup.get_text()
        images = [img['src'] for img in soup.find_all('img') if img.get('src')]
        links = [a['href'] for a in soup.find_all('a') if a.get('href')]

        return {
            'text': texts,
            'images': images,
            'links': links
        }
    except Exception as e:
        return {'error': str(e)}

# Function to crawl a single URL and retrieve all clickable links
def crawl_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        
        crawled_links = []
        for link in links:
            href = link.get('href')
            if href:
                # Create an absolute URL from a relative URL
                absolute_url = urljoin(url, href)
                crawled_links.append(absolute_url)
        return crawled_links
    except Exception as e:
        return {'url': url, 'error': str(e)}
    
def convert_epub_to_json(uploaded_file):
    try:
        book = epub.read_epub(uploaded_file)
        contents = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                text = soup.get_text()
                contents.append({'title': item.get_name(), 'content': text.strip()})

        return json.dumps(contents, indent=4)
    except Exception as e:
        return {'error': str(e)}

# Streamlit UI for Homepage Selection
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ("Home", "Web Scraper", "Web Crawler", "Excel to JSON Converter", "CSV to JSON Converter", "HTML to JSON Converter", "EPUB to JSON Converter", "PDF Merger"))

if choice == "Home":
    st.title("Welcome to the Web Assistant Tool")
    st.write("Choose 'Web Scraper' to extract text, images, and links from a website.")
    st.write("Choose 'Web Crawler' to list all clickable links from a website.")

elif choice == "Web Scraper":
    st.title('Web Scraper for Assistant Training')
    urls = st.text_area("Enter URLs (one per line)")

    if st.button('Scrape'):
        if urls:
            url_list = urls.split('\n')
            # Processing each URL
            all_data = []
            for url in url_list:
                result = scrape_url(url)
                all_data.append(result)

            # Generating a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f'scraped_data_{timestamp}.json'

            # Saving to JSON
            json_data = json.dumps(all_data)
            with open(filename, 'w') as outfile:
                outfile.write(json_data)
            
            st.success(f'Data scraped and saved to {filename}')

            # Download button
            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name=filename,
                mime='application/json'
            )
        else:
            st.error('Please enter at least one URL')

elif choice == "Web Crawler":
    st.title("Web Crawler")
    crawl_url_input = st.text_input("Enter URL to crawl")
    download_format = st.selectbox("Select download format", ["JSON", "TXT"])
    
    if st.button('Crawl'):
        if crawl_url_input:
            browser = init_browser()
            crawled_links = crawl_url(crawl_url_input)
            # Generating a timestamped filename for the crawled links
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            links_filename_json = f'crawled_links_{timestamp}.json'
            links_filename_txt = f'crawled_links_{timestamp}.txt'
            
            # Use the selenium_scrape_multiple_pages function to crawl
            crawled_links = selenium_scrape_multiple_pages(crawl_url_input, browser)
            browser.quit()
            
            # Saving crawled links to a file
            json_data = json.dumps(crawled_links)
            txt_data = '\n'.join(crawled_links)
            if download_format == "JSON":
                with open(links_filename_json, 'w') as links_file:
                    links_file.write(json_data)
                download_data = json_data
                download_name = links_filename_json
                mime_type = 'application/json'
            else:
                with open(links_filename_txt, 'w') as links_file:
                    links_file.write(txt_data)
                download_data = txt_data
                download_name = links_filename_txt
                mime_type = 'text/plain'
            
            st.success(f'Links crawled successfully and saved as {download_name}')
            
            # Displaying the crawled links appropriately
            if download_format == "JSON":
                st.json(crawled_links)
            else:
                st.text(txt_data)

            # Download button for crawled links
            st.download_button(
                label=f"Download Links File (.{download_format.lower()})",
                data=download_data,
                file_name=download_name,
                mime=mime_type
            )
        else:
            st.error('Please enter a URL')

elif choice == "Excel to JSON Converter":
    st.title("Excel to JSON Converter")
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        json_data = convert_excel_to_json(uploaded_file)
        if 'error' in json_data:
            st.error(json_data['error'])
        else:
            st.json(json_data)  # Display JSON data
            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name="converted_data.json",
                mime='application/json'
            )

elif choice == "CSV to JSON Converter":
    st.title("CSV to JSON Converter")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file is not None:
        data = convert_csv_to_json(uploaded_file)
        if 'error' in data:
            st.error(data['error'])
        else:
            json_data = json.dumps(data)
            st.json(json_data)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            download_filename = f"csv_converted_{timestamp}.json"
            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name=download_filename,
                mime='application/json'
            )

elif choice == "HTML to JSON Converter":
    st.title("HTML to JSON Converter")
    uploaded_file = st.file_uploader("Upload HTML file", type=['html'])

    if uploaded_file is not None:
        data = extract_data_from_html(uploaded_file)
        if 'error' in data:
            st.error(data['error'])
        else:
            json_data = json.dumps(data)
            st.json(json_data)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            download_filename = f"html_extracted_{timestamp}.json"
            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name=download_filename,
                mime='application/json'
            )


elif choice == "EPUB to JSON Converter":
    st.title("EPUB to JSON Converter")
    uploaded_file = st.file_uploader("Upload EPUB file", type=['epub'])

    if uploaded_file is not None:
        json_data = convert_epub_to_json(uploaded_file)
        if 'error' in json_data:
            st.error(json_data['error'])
        else:
            st.json(json_data)  # Display JSON data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            download_filename = f"epub_converted_{timestamp}.json"
            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name=download_filename,
                mime='application/json'
            )

# Streamlit UI for PDF Merger
elif choice == "PDF Merger":
    st.title("PDF Merger")
    uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)

    if st.button('Merge PDFs'):
        if uploaded_files:
            merged_pdf = merge_pdfs(uploaded_files)
            st.success('PDFs merged successfully.')
            st.download_button(
                label="Download Merged PDF",
                data=merged_pdf,
                file_name="merged_document.pdf",
                mime='application/pdf'
            )
        else:
            st.error('Please upload at least one PDF file.')