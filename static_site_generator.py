import os
import time
import subprocess
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import json
import re

# Configuration
STREAMLIT_PORT = 5000
OUTPUT_DIR = "build"
BASE_URL = f"http://localhost:{STREAMLIT_PORT}"
PAGES = [
    {"url": "/", "file_name": "index.html"},
    {"url": "/Stock_Analysis", "file_name": "stock_analysis.html"},
    {"url": "/Predictive_Analytics", "file_name": "predictive_analytics.html"}
]
ASSETS_DIRS = ["static", "media", "assets"]
DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

def create_output_directory():
    """Create or clean the output directory"""
    output_path = Path(OUTPUT_DIR)
    
    # Remove existing directory if it exists
    if output_path.exists() and output_path.is_dir():
        shutil.rmtree(output_path)
    
    # Create a fresh directory
    output_path.mkdir(parents=True)
    
    # Create directories for assets
    for asset_dir in ASSETS_DIRS:
        (output_path / asset_dir).mkdir(exist_ok=True)

def start_streamlit_server():
    """Start the Streamlit server as a subprocess"""
    process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", str(STREAMLIT_PORT), 
         "--server.address", "localhost", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(5)
    return process

def stop_streamlit_server(process):
    """Stop the Streamlit server subprocess"""
    process.terminate()
    process.wait()

def initialize_webdriver():
    """Initialize and configure Chrome webdriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_window_size(1280, 1024)
    return driver

def process_html(html_content, page_url):
    """Process HTML content to make it static-friendly"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all script tags that load from streamlit
    for script in soup.find_all('script'):
        src = script.get('src', '')
        # Remove the dynamic streamlit scripts that depend on websockets
        if 'streamlit' in src and ('client' in src or 'main' in src):
            script.decompose()
    
    # Find and fix the base URL for assets
    for link in soup.find_all(['link', 'img', 'script']):
        for attr in ['href', 'src']:
            if link.has_attr(attr) and not link[attr].startswith(('http', 'https', '//')):
                # Fix relative URLs
                link[attr] = link[attr].replace('/_stcore/static/', '/static/')
                link[attr] = link[attr].replace('./_streamlit/static/', '/static/')
    
    # Add custom JavaScript to handle interactivity loss
    static_js = soup.new_tag('script')
    static_js.string = """
    document.addEventListener('DOMContentLoaded', function() {
      // Message for users about the static nature of the page
      const infoDiv = document.createElement('div');
      infoDiv.innerHTML = '<div style="padding: 10px; background-color: #f0f8ff; border-radius: 5px; margin: 10px 0; text-align: center;">⚠️ This is a static snapshot of StockTrackPro. For full interactivity, please visit the live application.</div>';
      document.body.insertBefore(infoDiv, document.body.firstChild);
      
      // Add snapshot date
      const dateDiv = document.createElement('div');
      dateDiv.innerHTML = '<div style="text-align: center; padding: 20px;">Data snapshot from: ' + new Date().toLocaleDateString() + '</div>';
      document.body.appendChild(dateDiv);
    });
    """
    soup.head.append(static_js)
    
    return str(soup)

def generate_stock_pages(driver, default_stocks):
    """Generate static pages for each default stock"""
    for stock in default_stocks:
        # Generate stock analysis page
        stock_url = f"{BASE_URL}/Stock_Analysis?ticker={stock}"
        driver.get(stock_url)
        
        try:
            # Wait for the main content to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Stock Analysis')]"))
            )
            time.sleep(5)  # Additional wait for all data to load
            
            # Process and save the page
            html_content = process_html(driver.page_source, stock_url)
            output_path = Path(OUTPUT_DIR) / f"stock_{stock.lower()}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Generated stock analysis page for {stock}")
            
            # Generate predictive analytics page
            predict_url = f"{BASE_URL}/Predictive_Analytics?ticker={stock}"
            driver.get(predict_url)
            
            # Wait for the main content to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Predictive Analytics')]"))
            )
            time.sleep(5)  # Additional wait for data to load
            
            html_content = process_html(driver.page_source, predict_url)
            output_path = Path(OUTPUT_DIR) / f"predict_{stock.lower()}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Generated predictive analytics page for {stock}")
            
        except Exception as e:
            print(f"Error generating pages for {stock}: {e}")

def download_streamlit_assets(driver):
    """Download static assets needed for the Streamlit app"""
    # Get all static asset URLs from network requests
    all_requests = driver.execute_script("return window.performance.getEntries();")
    
    asset_urls = []
    for request in all_requests:
        url = request.get('name', '')
        if '/_stcore/static/' in url or './_streamlit/static/' in url:
            asset_urls.append(url)
    
    # Download each asset
    for url in asset_urls:
        try:
            # Extract the path part of the URL
            path_parts = url.split('static/')[1].split('?')[0]
            output_path = Path(OUTPUT_DIR) / 'static' / path_parts
            
            # Create directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            response = requests.get(url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded asset: {path_parts}")
        except Exception as e:
            print(f"Error downloading asset {url}: {e}")

def create_static_pages():
    """Create static pages from the Streamlit app"""
    create_output_directory()
    streamlit_process = start_streamlit_server()
    
    try:
        driver = initialize_webdriver()
        
        # Process each defined page
        for page in PAGES:
            url = f"{BASE_URL}{page['url']}"
            print(f"Processing {url}...")
            
            driver.get(url)
            
            # Wait for the content to be loaded
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give charts and data more time to load
            time.sleep(5)
            
            # Process and save the HTML
            html_content = process_html(driver.page_source, url)
            output_path = Path(OUTPUT_DIR) / page["file_name"]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"Created {page['file_name']}")
        
        # Generate pages for default stocks
        generate_stock_pages(driver, DEFAULT_STOCKS)
        
        # Download necessary assets
        download_streamlit_assets(driver)
        
        # Create GitHub Pages config file
        create_github_pages_config()
        
        # Copy 404 page from static assets if it exists
        custom_404_path = Path("static_assets/404.html")
        if custom_404_path.exists():
            shutil.copy(custom_404_path, Path(OUTPUT_DIR) / "404.html")
            print("Added custom 404 page")
        
        driver.quit()
        
    finally:
        stop_streamlit_server(streamlit_process)

def create_github_pages_config():
    """Create a _config.yml file for GitHub Pages"""
    config_content = """
# GitHub Pages configuration
title: StockTrackPro
description: Your comprehensive stock analysis platform
theme: jekyll-theme-cayman
"""
    
    with open(Path(OUTPUT_DIR) / "_config.yml", "w") as f:
        f.write(config_content.strip())
    
    # Create a README for the build directory
    readme_content = """
# StockTrackPro - Static Site

This is a statically generated version of the StockTrackPro application. The static site was generated on {date}.

## Pages

- [Home](index.html)
- [Stock Analysis](stock_analysis.html)
- [Predictive Analytics](predictive_analytics.html)

### Pre-generated Stock Pages

{stock_links}

Data provided by Yahoo Finance.
""".format(
        date=time.strftime("%Y-%m-%d"),
        stock_links="\n".join([f"- [{stock}](stock_{stock.lower()}.html)" for stock in DEFAULT_STOCKS])
    )
    
    with open(Path(OUTPUT_DIR) / "README.md", "w") as f:
        f.write(readme_content.strip())

if __name__ == "__main__":
    print("Starting static site generation...")
    create_static_pages()
    print(f"Static site generation complete. Files are in the '{OUTPUT_DIR}' directory.")