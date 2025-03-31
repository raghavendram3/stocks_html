# StockTrackPro - Static Site Generation

This folder contains all files related to converting the StockTrackPro Streamlit application into a static website that can be hosted on GitHub Pages.

## Directory Structure

- `static_site_generator.py` - The main script that captures Streamlit HTML and converts it to static pages
- `test_static_generation.py` - A test script to verify the static site generation process locally
- `DEPLOYMENT_GUIDE.md` - Step-by-step instructions for deploying to GitHub Pages
- `STATIC_SITE_SOLUTION.md` - Detailed explanation of the static site approach
- `README_STATIC_SITE.md` - README file for the static site version
- `.github/workflows/` - GitHub Actions configuration for automated deployment
- `static_assets/` - Contains the custom 404 page and other static assets

## Implementation Overview

The static site generation approach:
1. Runs the Streamlit app in headless mode
2. Uses Selenium to navigate to each page
3. Captures the HTML output
4. Processes the HTML to work as a standalone static website
5. Generates stock-specific pages for popular tickers
6. Packages everything for GitHub Pages deployment

## Getting Started

For detailed instructions on deploying this static site, refer to the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) file.

## Testing Locally

To test the static site generation process locally:

```bash
python test_static_generation.py
```

This will create a `build` directory with the generated static site.

## Automatically Rebuilding the Site

The GitHub Actions workflow in `.github/workflows/static-site-generator.yml` is configured to:
- Run daily to keep the data current
- Run on pushes to the main branch
- Deploy the generated site to GitHub Pages

For more detailed technical information, see [STATIC_SITE_SOLUTION.md](STATIC_SITE_SOLUTION.md).