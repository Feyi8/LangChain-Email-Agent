"""
PhD Application Email Assistant
=====================================
A 5-agent agentic workflow that researches Professor Michael Zhang's
academic profile and crafts a personalized PhD interest email.

Agents:
  1. Scholar Scraper   - Extracts research data (Google Scholar + SMU fallback)
  2. Topic Matcher     - Finds overlap between your interests and his research
  3. Email Composer    - Writes a personalized, compelling email
  4. Tone Reviewer     - Ensures professional yet warm tone
  5. Email Sender      - Sends with HITL approval

Install dependencies:
  pip install langchain-openai openai python-dotenv requests beautifulsoup4 lxml selenium

Author: Feyi Osideinde
Course: Agentic AI - Sobey School of Business, Saint Mary's University
"""

import os
import ssl
import smtplib
import time
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDER_EMAIL   = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

RECEIVER_EMAIL = "add_your_email"
SCHOLAR_URL    = "add_your_weblink"
SMU_URL        = "add_your_weblink"

YOUR_NAME      = "[Insert_name]"               
YOUR_PROGRAM   = "[Insert_program]"  
YOUR_INTERESTS = "[Insert_interests]"
YOUR_CONTACT   = "[Insert_contact]"   
YOUR_LINKEDIN  = "[Insert_linkedIn]"           


# =============================================================================
# TERMINAL STYLING
# =============================================================================

PINK   = "\033[95m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def banner():
    print(f"""
{PINK}{BOLD}
  +----------------------------------------------------------+
  |        PhD Application Email Assistant                   |
  |        Your Academic Matchmaker & Email Stylist          |
  |        Powered by LangChain + GPT-4o-mini                |
  +----------------------------------------------------------+
{RESET}""")


def step(number: int, total: int, label: str):
    bar = "+" * number + "-" * (total - number)
    print(f"\n{CYAN}{BOLD}  Step {number}/{total}  [{bar}]{RESET}")
    print(f"  {BOLD}{label}{RESET}")
    print(f"  {'-' * 54}")


def success(msg: str):
    print(f"  {GREEN}  [OK]  {msg}{RESET}")


def info(msg: str):
    print(f"  {YELLOW}  >>   {msg}{RESET}")


def warn(msg: str):
    print(f"  {YELLOW}  [!]  {msg}{RESET}")


def divider():
    print(f"\n{PINK}  {'=' * 56}{RESET}\n")


# =============================================================================
# SCRAPING HELPERS
# =============================================================================

def scrape_with_selenium(url: str) -> dict:
    """
    Use Selenium (headless Edge) to scrape Google Scholar.
    Returns dict with interests, papers, stats.
    """
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Edge(options=edge_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gsc_prf_in"))
        )
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "lxml")

        interests = [t.get_text(strip=True) for t in soup.select("#gsc_prf_int a")]
        papers    = [t.get_text(strip=True) for t in soup.select(".gsc_a_at")][:10]
        stats     = [t.get_text(strip=True) for t in soup.select(".gsc_rsb_std")][:4]

        citation_summary = ""
        if len(stats) >= 3:
            citation_summary = f"Total Citations: {stats[0]} | h-index: {stats[2]}"

        return {
            "source":   "Google Scholar",
            "interests": interests,
            "papers":    papers,
            "citations": citation_summary
        }
    except Exception as e:
        return {"source": "Google Scholar", "error": str(e), "interests": [], "papers": []}
    finally:
        driver.quit()


def scrape_smu_profile(url: str) -> dict:
    """
    Fallback: scrape receiver's SMU faculty page using requests + BS4.
    Professor confirmed this is also an acceptable source.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Extract all paragraph text from the page
        paragraphs = soup.find_all(["p", "li", "h2", "h3"])
        content    = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        return {
            "source":  "SMU Faculty Page",
            "content": content[:3000]   # cap to avoid token waste
        }
    except Exception as e:
        return {"source": "SMU Faculty Page", "error": str(e), "content": ""}


# =============================================================================
# AGENT 1 - SCHOLAR SCRAPER (with SMU fallback)
# =============================================================================

@tool
def scrape_scholar_profile(url: str) -> str:
    """
    Scrape receiver's academic profile.
    Primary: Google Scholar (Selenium).
    Fallback: SMU faculty page (requests + BS4) if Scholar data is empty.

    Args:
        url: Google Scholar profile URL

    Returns:
        Structured string with academic profile data
    """
    # --- Try Google Scholar first ---
    scholar_data = scrape_with_selenium(url)

    interests = scholar_data.get("interests", [])
    papers    = scholar_data.get("papers", [])
    citations = scholar_data.get("citations", "")

    # --- If Scholar returned empty data, fall back to SMU page ---
    smu_content = ""
    if not interests and not papers:
        warn("Google Scholar returned no data - using SMU faculty page as fallback...")
        smu_data    = scrape_smu_profile(SMU_URL)
        smu_content = smu_data.get("content", "")

    # --- Compile result ---
    lines = ["PROFESSOR: Michael Zhang", "INSTITUTION: Saint Mary's University", ""]

    if interests:
        lines.append("RESEARCH INTERESTS:")
        for i in interests:
            lines.append(f"  - {i}")
        lines.append("")

    if papers:
        lines.append("TOP PUBLICATIONS:")
        for n, p in enumerate(papers):
            lines.append(f"  {n+1}. {p}")
        lines.append("")

    if citations:
        lines.append(f"CITATION STATS:\n  {citations}")
        lines.append("")

    if smu_content:
        lines.append("PROFILE (from SMU website):")
        lines.append(smu_content[:1500])

    result = "\n".join(lines).strip()
    return result


# =============================================================================
# AGENT 2 - TOPIC MATCHER
# =============================================================================

@tool
def match_research_topics(professor_profile: str, student_interests: str) -> str:
    """
    Identify overlapping research themes between student and professor.

    Args:
        professor_profile: Scraped academic data
        student_interests: Student's stated research interests

    Returns:
        List of matched topics with talking points
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY)

    messages = [
        SystemMessage(content=(
            "You are an academic advisor. Identify specific research overlaps "
            "between a student and professor. Be concise and precise. "
            "Output 3-5 bullet points only. Reference actual papers or topics "
            "from the professor profile provided."
        )),
        HumanMessage(content=(
            f"PROFESSOR PROFILE:\n{professor_profile}\n\n"
            f"STUDENT INTERESTS:\n{student_interests}\n\n"
            "List the strongest research overlaps as concise bullet points. "
            "Reference specific papers or research areas from the profile above."
        ))
    ]

    response = llm.invoke(messages)
    return response.content


# =============================================================================
# AGENT 3 - EMAIL COMPOSER
# =============================================================================

@tool
def compose_phd_email(
    professor_profile: str,
    matched_topics: str,
    student_name: str,
    student_program: str,
    student_interests: str,
    student_contact: str,
    student_linkedin: str
) -> str:
    """
    Write a personalized PhD interest email to Professor Michael Zhang.

    Args:
        professor_profile: Scraped academic data
        matched_topics: Overlapping research themes
        student_name: Full name of the student
        student_program: Current academic program
        student_interests: Student's research interests

    Returns:
        A complete, polished email draft
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6, api_key=OPENAI_API_KEY)

    messages = [
        SystemMessage(content=(
            "You are an expert academic writing assistant. "
            "Write a compelling, sincere PhD interest email. "
            "It should be professional, specific, and warm - not generic. "
            "Maximum 250 words. Reference SPECIFIC papers or research areas "
            "from the professor profile - do NOT use placeholders like "
            "[insert paper title]. Use only what is in the profile provided."
        )),
        HumanMessage(content=(
            f"Write a PhD interest email with these details:\n\n"
            f"FROM: {student_name} ({student_program})\n"
            f"TO: Professor Michael Zhang, Saint Mary's University\n\n"
            f"PROFESSOR'S RESEARCH:\n{professor_profile}\n\n"
            f"MATCHED TOPICS:\n{matched_topics}\n\n"
            f"STUDENT INTERESTS:\n{student_interests}\n\n"
            f"STUDENT CONTACT: {student_contact}\n"
            f"STUDENT LINKEDIN: {student_linkedin}\n\n"
            "Write the full email including subject line. "
            "End the email with the student's name, contact info, and LinkedIn "
            "(only include LinkedIn if it is not blank). "
            "Do NOT use any placeholder text like [Your Contact Information]. "
            "Format as:\nSUBJECT: ...\n\n[email body]"
        ))
    ]

    response = llm.invoke(messages)
    return response.content


# =============================================================================
# AGENT 4 - TONE REVIEWER
# =============================================================================

@tool
def review_email_tone(email_draft: str) -> str:
    """
    Review and refine the email tone - professional, warm, not generic.

    Args:
        email_draft: The composed email draft

    Returns:
        Polished final email with tone improvements applied
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY)

    messages = [
        SystemMessage(content=(
            "You are a professional writing editor specialising in academic emails. "
            "Review and improve the email tone. Ensure it is:\n"
            "  - Confident but not arrogant\n"
            "  - Warm but not overly casual\n"
            "  - Specific, not generic\n"
            "  - Under 250 words\n"
            "  - Free of any placeholder text like [insert ...]\n"
            "Return the COMPLETE improved email only. No commentary."
        )),
        HumanMessage(content=f"Review and improve this PhD email:\n\n{email_draft}")
    ]

    response = llm.invoke(messages)
    return response.content


# =============================================================================
# AGENT 5 - HITL + EMAIL SENDER
# =============================================================================

def human_in_the_loop(final_email: str) -> bool:
    """
    HITL: Show the email preview and request explicit approval before sending.
    """
    divider()
    print(f"{PINK}{BOLD}  HUMAN-IN-THE-LOOP APPROVAL{RESET}")
    print(f"{PINK}  {'-' * 54}{RESET}")
    print(f"\n{BOLD}  EMAIL PREVIEW{RESET}\n")

    for line in final_email.split("\n"):
        print(f"    {line}")

    divider()
    print(f"{YELLOW}{BOLD}  Does this email look good to send?{RESET}")
    print(f"  {CYAN}  [Y]{RESET} Yes, send it!")
    print(f"  {CYAN}  [N]{RESET} No, cancel.")
    print()

    while True:
        choice = input(f"  {BOLD}  Your choice (Y/N): {RESET}").strip().lower()
        if choice in {"y", "yes"}:
            return True
        elif choice in {"n", "no"}:
            return False
        else:
            print(f"  {YELLOW}  Please enter Y or N{RESET}")


def send_email(final_email: str) -> bool:
    """
    Send the approved email via Gmail SMTP.
    Uses ssl._create_unverified_context() as recommended by professor.
    """
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print(f"\n  {YELLOW}  [!] Email credentials not set in .env file.{RESET}")
        print(f"  {YELLOW}      Add SENDER_EMAIL and EMAIL_PASSWORD to send.{RESET}")
        return False

    lines      = final_email.strip().split("\n")
    subject    = "PhD Interest - Prospective Student"
    body_start = 0

    for i, line in enumerate(lines):
        if line.upper().startswith("SUBJECT:"):
            subject    = line.split(":", 1)[1].strip()
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL

    context = ssl._create_unverified_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except smtplib.SMTPException as e:
        print(f"  [!] SMTP Error: {e}")
        return False


# =============================================================================
# ORCHESTRATOR
# =============================================================================

def run_pipeline():
    banner()

    info(f"Student:    {YOUR_NAME}")
    info(f"Program:    {YOUR_PROGRAM}")
    info(f"Interests:  {YOUR_INTERESTS}")
    info(f"Sending to: {RECEIVER_EMAIL}")

    step(1, 5, "Scholar Scraper - Researching Professor Zhang")
    professor_profile = scrape_scholar_profile.invoke({"url": SCHOLAR_URL})
    success("Profile scraped successfully!")

    step(2, 5, "Topic Matcher - Finding Research Overlaps")
    matched_topics = match_research_topics.invoke({
        "professor_profile": professor_profile,
        "student_interests": YOUR_INTERESTS
    })
    success("Research overlaps identified!")
    print()
    for line in matched_topics.strip().split("\n"):
        print(f"    {YELLOW}{line}{RESET}")

    step(3, 5, "Email Composer - Crafting Your Email")
    email_draft = compose_phd_email.invoke({
        "professor_profile": professor_profile,
        "matched_topics":    matched_topics,
        "student_name":      YOUR_NAME,
        "student_program":   YOUR_PROGRAM,
        "student_interests": YOUR_INTERESTS,
        "student_contact":   YOUR_CONTACT,
        "student_linkedin":  YOUR_LINKEDIN
    })
    success("First draft composed!")

    step(4, 5, "Tone Reviewer - Polishing Your Email")
    final_email = review_email_tone.invoke({"email_draft": email_draft})
    success("Email polished and ready!")

    step(5, 5, "Email Sender - Your Approval Required!")
    approved = human_in_the_loop(final_email)

    if approved:
        sent = send_email(final_email)
        divider()
        if sent:
            print(f"  {GREEN}{BOLD}  [OK] Email sent successfully! Good luck with your PhD!{RESET}")
        else:
            print(f"  {YELLOW}  [!] Email not sent - check your .env credentials.{RESET}")
            print(f"  {YELLOW}      Your polished email is shown above for manual sending.{RESET}")
    else:
        divider()
        print(f"  {YELLOW}  [!] Email cancelled.{RESET}")
        print(f"  {YELLOW}      Your draft is shown above for reference.{RESET}")

    divider()
    print(f"  {PINK}{BOLD}  Thank you for using PhD Email Assistant!{RESET}\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_pipeline()
