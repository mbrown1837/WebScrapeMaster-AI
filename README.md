# WebScrapeMaster-AI

A powerful web scraping tool that leverages AI (Together API) to extract structured information from websites using Large Language Models (LLMs). This tool is specifically optimized for the Meta-Llama-3.1-70B-Instruct-Turbo model.

## Features
- AI-Powered Extraction: Uses Together AI's LLM for intelligent data parsing
- Dynamic Web Scraping: Handles JavaScript-rendered content using Playwright
- Smart Content Processing: Chunks large content for optimal processing
- Multiple Output Formats: Exports to JSON, CSV, and Excel
- User-Agent Rotation: Improves scraping reliability
- Domain-Based Organization: Automatically organizes results by domain
- Clean Content Conversion: HTML to Markdown transformation
- Configurable Fields: Customize extraction fields

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/WebScrapeMaster-AI.git

Navigate to the project directory:
```bash
cd WebScrapeMaster-AI

Install required dependencies:
```bash
pip install -r requirements.txt

Install Playwright browsers:
```bash
playwright install chromium
