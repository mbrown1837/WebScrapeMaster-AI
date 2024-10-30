# WebScrapeMaster-AI For Colab Only

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
!git clone https://github.com/mbrown1837/WebScrapeMaster-AI.git
```

Navigate to the project directory:
```bash
cd WebScrapeMaster-AI
```

Install required dependencies:
```bash
pip install -r requirements.txt
```

Install Playwright browsers:
```bash
!playwright install chromium
```

## Configuration

1. Create `config.txt`:
```text
model=meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
together_api_key=your-together-api-key
```

2. Create `fields.txt`:
```text
names
email
phone number
designation
```

3. Create `urls.txt`:
```text
https://example.com/page1
https://example.com/page2
```

## Usage

Run the script:
```bash
!python scrapemaster_colab.py
```

## Output Structure
```text
scraping_results/
├── domain1/
│   ├── domain1_results.json
│   ├── domain1_results.csv
│   └── domain1_results.xlsx
└── domain2/
    ├── domain2_results.json
    ├── domain2_results.csv
    └── domain2_results.xlsx
```

## Technical Details

### Model Information
- Model: meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
- Context Length: 131,072 tokens
- Max Output Tokens: 4,096

### Key Components

**Configuration Management**
- Loads settings from config.txt
- Manages API keys and model settings
- Handles URL and field configurations

**Web Scraping Engine**
- Uses Playwright for JavaScript rendering
- Implements smart waiting mechanisms
- Rotates user agents automatically

**Content Processing**
- Converts HTML to clean markdown
- Chunks content for optimal processing
- Handles large pages efficiently

**AI Processing**
- Structured prompt engineering
- JSON response parsing
- Error handling and validation

**Output Management**
- Multi-format export capability
- Domain-based organization
- Detailed logging system

## Troubleshooting

**API Issues:**
- Verify Together API key in config.txt
- Check API status
- Validate model name

**Scraping Problems:**
- Verify URL accessibility
- Check JavaScript rendering
- Adjust waiting times

**Content Processing:**
- Adjust chunk size if needed
- Monitor memory usage
- Check output formatting

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

## Support
For issues and feature requests, please use the GitHub Issues section.

## Requirements
- Python 3.7+
- beautifulsoup4
- pandas
- pydantic
- html2text
- playwright
- requests
- fake-useragent
- openpyxl

## Note
This tool is optimized for the Together AI platform and the Meta-Llama-3.1-70B-Instruct-Turbo model. Ensure you have the necessary API access and credentials before use.
```

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/2461148/e9ad20a7-2813-4dc7-a50c-b3f4c02bb793/input.txt
