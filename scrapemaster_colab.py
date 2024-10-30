import os
import json
import time
from datetime import datetime
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
import html2text
from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urlparse
from fake_useragent import UserAgent

# Constants
SYSTEM_MESSAGE = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
with no additional commentary, explanations, or extraneous information."""

TOGETHER_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
GROQ_MODEL = "llama-3.1-70b-versatile"
MAX_TOKENS_TOGETHER = 131072
MAX_TOKENS_GROQ = 128000
MAX_OUTPUT_TOKENS_GROQ = 8000
DEFAULT_CHUNK_SIZE = 30000

class Config:
    def __init__(self):
        self.load_config()
        self.load_urls()
        self.load_fields()
        self.ua = UserAgent()

    def load_config(self):
        try:
            with open('config.txt', 'r') as f:
                config = dict(line.strip().split('=', 1) for line in f if '=' in line)
                self.api_provider = config.get('api_provider', 'together').lower()
                self.model = GROQ_MODEL if self.api_provider == 'groq' else TOGETHER_MODEL
                self.together_api_key = config.get('together_api_key', '')
                self.groq_api_key = config.get('groq_api_key', '')
                self.chunk_size = int(config.get('chunk_size', DEFAULT_CHUNK_SIZE))
                self.max_tokens = MAX_TOKENS_GROQ if self.api_provider == 'groq' else MAX_TOKENS_TOGETHER
                self.max_output_tokens = MAX_OUTPUT_TOKENS_GROQ if self.api_provider == 'groq' else 4096
        except FileNotFoundError:
            print("Config file not found. Using default values.")
            self.api_provider = 'together'
            self.model = TOGETHER_MODEL
            self.together_api_key = ''
            self.groq_api_key = ''
            self.chunk_size = DEFAULT_CHUNK_SIZE
            self.max_tokens = MAX_TOKENS_TOGETHER
            self.max_output_tokens = 4096

    def load_urls(self):
        try:
            with open('urls.txt', 'r') as f:
                self.urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("URLs file not found.")
            self.urls = []

    def load_fields(self):
        try:
            with open('fields.txt', 'r') as f:
                self.fields = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Fields file not found.")
            self.fields = []

def get_domain_name(url: str) -> str:
    """Extract domain name from URL"""
    try:
        parsed_uri = urlparse(url)
        domain = parsed_uri.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return 'unknown_domain'

def fetch_page_content(url: str, config: Config) -> str:
    """Fetch webpage content using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=config.ua.random)
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(2)
            content = page.content()
            return content
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""
        finally:
            browser.close()

def clean_html(html_content: str) -> str:
    """Clean HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['script', 'style', 'iframe', 'meta']):
        element.decompose()
    return str(soup)

def html_to_markdown(html_content: str) -> str:
    """Convert HTML to markdown"""
    cleaned_html = clean_html(html_content)
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    return converter.handle(cleaned_html)

def chunk_content(content: str, config: Config) -> List[str]:
    """Split content into optimally sized chunks based on configuration"""
    sentences = content.replace('\n', ' ').split('.')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Approximate token count (words + buffer for tokenization)
        sentence_size = len(sentence.split()) * 1.3
        
        if current_size + sentence_size > config.chunk_size:
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def process_with_api(content: str, fields: List[str], config: Config) -> Dict:
    """Process content with selected API provider"""
    try:
        system_prompt = SYSTEM_MESSAGE
        user_prompt = f"""Extract the following fields from the content: {', '.join(fields)}
        Format the output EXACTLY as:
        {{
            "listings": [
                {{{', '.join(f'"{field}": "value"' for field in fields)}}}
            ]
        }}
        
        Content: {content}"""

        if config.api_provider == 'together':
            api_url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.together_api_key}",
                "Content-Type": "application/json"
            }
        else:  # groq
            api_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.groq_api_key}",
                "Content-Type": "application/json"
            }

        # Calculate approximate token count for prompt
        prompt_tokens = len(system_prompt.split()) + len(user_prompt.split())
        max_output = min(
            config.max_output_tokens,
            config.max_tokens - prompt_tokens
        )

        data = {
            "model": config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": max_output,
            "response_format": {"type": "json_object"}
        }

        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content'].strip()
            return parse_api_response(response_text)
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return {"listings": []}

    except Exception as e:
        print(f"Error processing with API: {str(e)}")
        return {"listings": []}

def parse_api_response(response_text: str) -> Dict:
    """Parse and validate API response"""
    try:
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```").strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].strip()
        else:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_text = response_text[start_idx:end_idx] if start_idx != -1 and end_idx > start_idx else response_text

        result = json.loads(json_text)
        
        if not isinstance(result, dict):
            result = {"listings": []}
        elif "listings" not in result:
            if isinstance(result, dict):
                result = {"listings": [result]}
            else:
                result = {"listings": []}
        
        return result

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return {"listings": []}

def save_results(data: Dict, domain: str, urls: List[str], output_folder: str):
    """Save results in multiple formats"""
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Add source URLs to each listing
        for listing in data.get('listings', []):
            listing['source_url'] = urls
        
        # Save JSON
        json_path = os.path.join(output_folder, f'{domain}_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Convert and save to CSV and Excel if data contains listings
        if data.get('listings'):
            df = pd.DataFrame(data['listings'])
            
            csv_path = os.path.join(output_folder, f'{domain}_results.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            excel_path = os.path.join(output_folder, f'{domain}_results.xlsx')
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
        print(f"Results saved for domain: {domain}")
            
    except Exception as e:
        print(f"Error saving results for {domain}: {str(e)}")

def main():
    """Main function to run the scraper"""
    try:
        config = Config()
        
        if not config.urls or not config.fields:
            print("No URLs or fields found. Please check your configuration files.")
            return
        
        base_output_folder = 'scraping_results'
        os.makedirs(base_output_folder, exist_ok=True)
        
        domain_results = {}
        for url in config.urls:
            domain = get_domain_name(url)
            print(f"\nProcessing {url} (Domain: {domain})...")
            
            output_folder = os.path.join(base_output_folder, domain)
            os.makedirs(output_folder, exist_ok=True)
            
            html_content = fetch_page_content(url, config)
            if not html_content:
                continue
            
            markdown_content = html_to_markdown(html_content)
            print(f"Content length: {len(markdown_content)} characters")
            
            chunks = chunk_content(markdown_content, config)
            print(f"Split into {len(chunks)} chunks")
            
            chunk_results = []
            for i, chunk in enumerate(chunks, 1):
                print(f"Processing chunk {i}/{len(chunks)}")
                result = process_with_api(chunk, config.fields, config)
                if result and result.get('listings'):
                    chunk_results.extend(result['listings'])
                time.sleep(1)  # Rate limiting
            
            if chunk_results:
                if domain not in domain_results:
                    domain_results[domain] = []
                domain_results[domain].extend(chunk_results)
        
        # Save results for each domain
        for domain, results in domain_results.items():
            combined_results = {'listings': results}
            output_folder = os.path.join(base_output_folder, domain)
            save_results(combined_results, domain, config.urls, output_folder)
            print(f"\nCompleted processing domain: {domain}")
            print(f"Total items extracted: {len(results)}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()