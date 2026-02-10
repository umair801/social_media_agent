# Social Media Agent - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [API Keys Setup](#api-keys-setup)
4. [Configuration](#configuration)
5. [Running the Agent](#running-the-agent)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

### Recommended
- Virtual environment (venv or conda)
- PostgreSQL (for production database)
- Redis (for background task processing)

### API Accounts Needed
- OpenAI API account (for GPT-4)
- Buffer account (or direct platform APIs)
- Google Cloud account (for Sheets integration)
- Social media platform developer accounts

## Installation

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone https://github.com/yourusername/social-media-agent.git
cd social-media-agent

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import crewai; print('CrewAI installed successfully')"
```

## API Keys Setup

### OpenAI API

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't see it again!)

**Cost Estimate**: ~$20-50/month for typical usage

### Buffer API (Recommended for Multi-Platform)

1. Sign up at [Buffer](https://buffer.com/)
2. Go to [Buffer Developer Apps](https://buffer.com/developers/apps)
3. Create a new app
4. Get your Access Token
5. Note your Profile IDs for each platform

**Alternative**: Use direct platform APIs (see below)

### Instagram API

1. Create a [Facebook Developer Account](https://developers.facebook.com/)
2. Create an app and add Instagram Graph API
3. Get access tokens and permissions
4. Note your Instagram Business Account ID

### LinkedIn API

1. Create a [LinkedIn Developer Account](https://www.linkedin.com/developers/)
2. Create an app
3. Request API access (may take 1-2 weeks)
4. Get OAuth tokens

### Twitter/X API

1. Apply for [Twitter Developer Account](https://developer.twitter.com/)
2. Create a project and app
3. Get API Key, API Secret, Access Token, and Access Secret
4. Note your Bearer Token

### Facebook API

1. Use Facebook Developer Account (same as Instagram)
2. Get Page Access Token
3. Note your Page ID

### Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API
4. Create credentials (Service Account)
5. Download JSON credentials file

## Configuration

### Step 1: Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Fill in your API keys:

```env
# Required
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4

# Choose one: Buffer OR direct platform APIs

# Option 1: Buffer (Recommended)
BUFFER_ACCESS_TOKEN=your_buffer_token
BUFFER_PROFILE_IDS=instagram_id,linkedin_id,twitter_id,facebook_id

# Option 2: Direct Platform APIs
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_ACCOUNT_ID=your_account_id
FACEBOOK_ACCESS_TOKEN=your_facebook_token
FACEBOOK_PAGE_ID=your_page_id
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_ORGANIZATION_ID=your_org_id
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Google Services
GOOGLE_SHEETS_CREDENTIALS=path/to/google-credentials.json
```

### Step 2: Brand Configuration

Edit `config/brand_profiles.yaml`:

```yaml
brand_name: "Your Company Name"
industry: "Your Industry"
brand_voice: "Your brand voice description"

target_audience:
  platforms:
    - LinkedIn
    - Instagram
    - Twitter
    - Facebook

# Customize other fields as needed
```

### Step 3: Verify Configuration

```bash
# Test configuration loading
python -c "import yaml; print(yaml.safe_load(open('config/brand_profiles.yaml')))"
```

## Running the Agent

### Quick Start - Generate Content

```python
from agents.orchestrator import SocialMediaOrchestrator

# Initialize
orchestrator = SocialMediaOrchestrator("config/brand_profiles.yaml")

# Generate 7 days of content
calendar = orchestrator.generate_content_calendar(days=7)

# Schedule posts
results = orchestrator.schedule_all_posts(calendar)

print(f"Scheduled {len(results['scheduled'])} posts!")
```

### Run Engagement Monitoring

```bash
# Test mode (sample comments)
python run_engagement_agent.py --test-mode

# Production mode (monitor platforms)
python run_engagement_agent.py --platforms instagram linkedin

# With custom interval (check every 5 minutes)
python run_engagement_agent.py --interval 300
```

### Generate Analytics Report

```python
from agents.analytics import AnalyticsAgent
from datetime import datetime, timedelta

analytics = AnalyticsAgent({'brand_name': 'Your Brand'})

report = analytics.generate_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    platforms=['instagram', 'linkedin']
)

# Export to JSON
analytics.export_report(report, format='json')
```

## Deployment

### Option 1: DigitalOcean Droplet ($6/month)

```bash
# Create droplet with Ubuntu 22.04
# SSH into droplet
ssh root@your_droplet_ip

# Install dependencies
apt update && apt upgrade -y
apt install python3.9 python3-pip git -y

# Clone repo
git clone https://github.com/yourusername/social-media-agent.git
cd social-media-agent

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add your keys

# Run with screen or tmux
screen -S social-agent
python run_engagement_agent.py
# Detach with Ctrl+A, D
```

### Option 2: Heroku (Free Tier Available)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login and create app
heroku login
heroku create your-social-agent

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set BUFFER_ACCESS_TOKEN=your_token
# ... set all required vars

# Deploy
git push heroku main

# Run worker
heroku ps:scale worker=1
```

### Option 3: AWS EC2

```bash
# Launch t2.micro instance (free tier eligible)
# Use Ubuntu 22.04 AMI

# SSH and setup (similar to DigitalOcean)
# Configure security groups for API access
```

### Using systemd for Auto-Restart (Linux)

Create `/etc/systemd/system/social-agent.service`:

```ini
[Unit]
Description=Social Media Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/social-media-agent
ExecStart=/path/to/venv/bin/python run_engagement_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable social-agent
sudo systemctl start social-agent
sudo systemctl status social-agent
```

## Troubleshooting

### Common Issues

#### "Module not found" Error

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### "OpenAI API Error: Rate Limit"

```python
# Reduce concurrent requests
# Add delays between API calls
import time
time.sleep(1)  # Wait 1 second between requests
```

#### "Buffer API Error: Invalid Profile ID"

```bash
# Get your profile IDs
curl https://api.bufferapp.com/1/profiles.json?access_token=YOUR_TOKEN

# Update BUFFER_PROFILE_IDS in .env
```

#### Posts Not Scheduling

```bash
# Check API credentials
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('BUFFER_ACCESS_TOKEN'))"

# Verify platform connection
python
>>> from tools.platform_apis import PlatformManager
>>> pm = PlatformManager()
>>> # Should not raise errors
```

#### High OpenAI Costs

```python
# Use GPT-3.5-turbo instead of GPT-4
# In .env:
OPENAI_MODEL=gpt-3.5-turbo

# Reduce temperature for more deterministic responses
# In agent initialization:
ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
```

### Getting Help

1. Check logs: `cat logs/engagement.log`
2. Enable debug mode: `LOG_LEVEL=DEBUG python run_engagement_agent.py`
3. Review API documentation for platform-specific issues
4. Open GitHub issue with error details

## Performance Optimization

### Reduce API Calls

```python
# Cache content templates
# Batch process posts
# Use rate limiting
```

### Database Optimization

```python
# Use PostgreSQL for production
# Index frequently queried fields
# Archive old posts
```

### Monitoring

```bash
# Setup Sentry for error tracking
pip install sentry-sdk

# Add to code:
import sentry_sdk
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
```

## Next Steps

1. Customize brand_profiles.yaml for your brand
2. Test content generation in dry-run mode
3. Review and approve generated content
4. Schedule first batch of posts
5. Monitor engagement and iterate
6. Scale to additional platforms

## Support

For issues or questions:
- Email: support@yourdomain.com
- GitHub: github.com/yourusername/social-media-agent/issues
- Documentation: Full docs in /docs folder
