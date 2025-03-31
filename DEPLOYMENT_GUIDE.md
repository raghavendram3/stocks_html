# StockTrackPro - GitHub Pages Deployment Guide

This guide explains how to deploy your StockTrackPro static site to GitHub Pages.

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., `stocktrackpro`)
4. Choose whether to make it public or private
5. Click "Create repository"

## Step 2: Upload Your Code

### Option A: Using Git Command Line

```bash
# Initialize Git in your project directory
git init

# Add all files to Git
git add .

# Commit changes
git commit -m "Initial commit"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Option B: Upload via GitHub Web Interface

1. On your repository page, click "uploading an existing file"
2. Drag and drop all the files from your project directory
3. Click "Commit changes"

## Step 3: Configure GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings"
3. Scroll down to the "GitHub Pages" section
4. For Source, select "GitHub Actions"

## Step 4: Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. You might see the "Generate Static Site" workflow already detected
3. If not, click "set up a workflow yourself" and copy the contents of `.github/workflows/static-site-generator.yml` into the editor
4. Click "Start commit" and then "Commit new file"

## Step 5: Run the Workflow

1. Go to the "Actions" tab
2. Click on the "Generate Static Site" workflow
3. Click "Run workflow" on the right side
4. Select the branch (main) and click "Run workflow"

## Step 6: Access Your Static Site

After the workflow completes successfully:

1. Go back to "Settings" > "Pages"
2. You'll see a message like "Your site is published at https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/"
3. Click the link to visit your static site

## Troubleshooting

### Workflow Failures

If your GitHub Actions workflow fails:

1. Go to the "Actions" tab
2. Click on the failed run
3. Check the logs for error messages
4. Common issues include:
   - Missing dependencies
   - Selenium/Chrome driver issues
   - Permission problems

### Custom Domain (Optional)

To use a custom domain:

1. Go to "Settings" > "Pages"
2. Under "Custom domain", enter your domain name
3. Update your DNS settings with your domain provider
4. Add a CNAME file to your repository that contains your custom domain
5. Make sure your GitHub Actions workflow doesn't delete this file when deploying

## Updating Your Site

Your site will automatically update:

1. Daily at midnight UTC (as configured in the workflow)
2. Whenever you push changes to the main branch
3. Manually when you run the workflow from the Actions tab

## Important Notes

1. The static site contains pre-generated data for specific stocks only
2. Interactive features won't work on the static site
3. To add more stocks to the pre-generated list, edit the `DEFAULT_STOCKS` list in `static_site_generator.py`