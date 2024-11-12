# Insight Tracker

A streamlined tool for gathering and analyzing company and professional profile insights using AI-powered analysis.

## Overview

Insight Tracker is a Streamlit-based application that helps you:
- Research companies and their market presence
- Analyze professional profiles
- Track business insights
- Generate outreach content

## Prerequisites

- Python 3.8 or higher
- Virtual environment management tool (venv)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/insight_tracker.git
cd insight_tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```env
API_BASE_URL=your_api_base_url
API_KEY=your_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

```
insight_tracker/
├── src/
│   ├── insight_tracker/
│   │   ├── main.py           # Main application
│   │   ├── db.py            # Database operations
│   │   ├── utils/           # Utility functions
│   │   └── ui/             # User interface components
│   └── api/
│       ├── client/         # API client
│       ├── models/         # Data models
│       ├── exceptions/     # Custom exceptions
│       └── services/       # Business logic
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Usage

1. Start the application:
```bash
streamlit run src/insight_tracker/main.py
```

2. Access the web interface at `http://localhost:8501`

3. Enter your credentials to begin using the tool

## Features

### Company Research
- Company profile analysis
- Industry insights
- Employee information
- Market positioning

### Profile Analysis
- Professional background analysis
- Career trajectory
- Key achievements
- Contact information

### Data Management
- Save and track research history
- Export insights
- Manage user preferences

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black src/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, questions, or feedback:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Pydantic](https://pydantic-docs.helpmanual.io/)
