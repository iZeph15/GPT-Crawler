import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin

# Function to scrape a single URL
def scrape_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting data
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

# Streamlit UI for Homepage Selection
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ("Home", "Web Scraper", "Web Crawler"))

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
            crawled_links = crawl_url(crawl_url_input)
            # Generating a timestamped filename for the crawled links
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            links_filename_json = f'crawled_links_{timestamp}.json'
            links_filename_txt = f'crawled_links_{timestamp}.txt'
            
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