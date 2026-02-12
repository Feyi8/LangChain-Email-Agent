# PhD Application Email Assistant

An intelligent 5-agent agentic workflow that researches Professor Michael Zhang's academic profile and crafts a personalized PhD interest email — with Human-in-the-Loop approval before sending.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.2.7-green.svg)
![License](https://img.shields.io/badge/license-MIT-pink.svg)

---

## What It Does

```
Scrapes Google Scholar  →  Matches Topics  →  Writes Email
→  Reviews Tone  →  YOUR Approval  →  Sends!
```

Five agents collaborate autonomously to produce one perfectly crafted,
personalized PhD interest email — and nothing gets sent without your say-so.

---

## The 5 Agents

| # | Agent | Role |
|---|-------|------|
| 1 | **Scholar Scraper** | Scrapes research interests, papers & citation stats from Google Scholar using BeautifulSoup4 |
| 2 | **Topic Matcher** | Identifies research overlaps between student interests and professor's work |
| 3 | **Email Composer** | Writes a compelling, personalized PhD interest email (max 250 words) |
| 4 | **Tone Reviewer** | Polishes tone — confident, warm, specific, not generic |
| 5 | **Email Sender** | Sends via Gmail SMTP after explicit HITL approval |

---

## Human-In-The-Loop (HITL)

Before any email is sent, the system **pauses and asks you**:

```
  Is this email good to go?
     [Y] Yes, send it!
     [N] No, cancel.
```

Nothing is sent without your explicit approval. This is a core safety feature.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install langchain-openai openai python-dotenv requests beautifulsoup4 lxml
```

### 2. Set Up Environment Variables

```bash
cp .env_phd.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key
SENDER_EMAIL=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

### 3. Update Your Details

In `phd_email_assistant.py`, update these 3 lines:
```python
YOUR_NAME      = "Your Full Name"           # ← Your name
YOUR_PROGRAM   = "Master of Business Analytics"  # ← Your program
YOUR_INTERESTS = "AI in Business/Finance and Supply Chain & Operations AI"
```

### 4. Run!

```bash
python phd_email_assistant.py
```

---

## Gmail App Password Setup

**Important:** You need a Gmail App Password, NOT your regular password.

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. **Security** → Enable **2-Step Verification** (required!)
3. **Security** → **App Passwords**
4. Select **Mail** + **Windows Computer** → **Generate**
5. Copy the 16-character password into your `.env` file

---

## Sample Output

```
  ╔══════════════════════════════════════════════════════════╗
  ║             PhD Application Email Assistant              ║
  ║         Your Academic Matchmaker & Email Stylist         ║
  ║              Powered by LangChain + GPT-4o-mini          ║
  ╚══════════════════════════════════════════════════════════╝

  ✦  Student:   Jane Smith
  ✦  Program:   Master of Business Analytics
  ✦  Interests: AI in Business/Finance and Supply Chain & Operations AI
  ✦  Sending to: Yilin.Huang@smu.ca

  Step 1/5  █░░░░
    Scholar Scraper — Researching Professor Zhang
  ──────────────────────────────────────────────────────
    Profile scraped successfully!

  Step 2/5  ██░░░
    Topic Matcher — Finding Research Overlaps
  ──────────────────────────────────────────────────────
    Research overlaps identified!

    • AI-driven pricing models → aligns with professor's revenue management research
    • Supply chain optimization → connects to his Operations AI publications
    • Business analytics applications → core theme across his cited work

  Step 3/5  ███░░
     Email Composer — Crafting Your Email
  ──────────────────────────────────────────────────────
    First draft composed!

  Step 4/5  ████░
    Tone Reviewer — Polishing Your Email
  ──────────────────────────────────────────────────────
    Email polished and ready!

  Step 5/5  █████
    Email Sender — Your Approval Required!

  ════════════════════════════════════════════════════════

    HUMAN-IN-THE-LOOP APPROVAL

    EMAIL PREVIEW

    SUBJECT: PhD Interest — AI in Business Analytics & Supply Chain

    Dear Professor Zhang,

    I am writing to express my strong interest in pursuing...
    [Full email shown here]

  ════════════════════════════════════════════════════════

    Is this email good to go?
     [Y] Yes, send it! 
     [N] No, cancel.

    Your choice (Y/N): Y

    Email sent successfully! Good luck with your PhD! 
```

---

##  Architecture

```
phd_email_assistant.py
│
├── AGENT 1: scrape_scholar_profile()
│     └── BeautifulSoup4 scrapes Google Scholar
│         Extracts: interests, papers, citations
│
├── AGENT 2: match_research_topics()
│     └── GPT-4o-mini identifies overlaps
│         Between student interests + professor's work
│
├── AGENT 3: compose_phd_email()
│     └── GPT-4o-mini writes personalized email
│         References specific papers and interests
│
├── AGENT 4: review_email_tone()
│     └── GPT-4o-mini polishes tone
│         Confident, warm, specific, under 250 words
│
└── AGENT 5: HITL + send_email()
      └── Shows preview → asks approval → sends via Gmail SMTP
```

---

##  Project Structure

```
project/
├── phd_email_assistant.py    # Main application
├── .env                       # Your API keys (DON'T commit!)
├── .env_phd.example           # Template
├── .gitignore                 # Protects your keys
└── README.md                  # This file
```

---

##  Security

- API keys stored in `.env` (never committed to Git)
- `.gitignore` excludes all sensitive files
- HITL ensures no accidental emails sent
- Email sent to TA test address only

---

##  Cost

Each run makes ~3 GPT-4o-mini calls:
- Topic matching: ~300 tokens
- Email composing: ~400 tokens
- Tone review: ~400 tokens
- **Total per run: ~$0.001** (0.1 cents) 

---

## Built With

- [LangChain](https://python.langchain.com/) - Agent framework
- [OpenAI GPT-4o-mini](https://openai.com/) - Language model
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [smtplib](https://docs.python.org/3/library/smtplib.html) - Email sending
- [Google Scholar](https://scholar.google.com/) - Academic data source

---

**Built for Agentic AI Coursework — Sobey School of Business, Saint Mary's University**
