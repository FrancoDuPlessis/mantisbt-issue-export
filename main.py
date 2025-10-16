import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple
import getpass
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
BASE_URL = os.getenv("BASE_URL") or logger.error("BASE_URL not set in .env file") or exit(1)
USERNAME_URL = os.getenv("USERNAME_URL") or logger.error("USERNAME_URL not set in .env file") or exit(1)
PASSWORD_URL = os.getenv("PASSWORD_URL") or logger.error("PASSWORD_URL not set in .env file") or exit(1)
DOWNLOADS_DIR = Path("downloads")
ISSUE_FILE = Path("issue_list.txt")

icon_class_list = [
    "fa fa-envelope-o",
    "fa fa-file-image-o",
    "fa fa-file-o",
    "fa fa-file-pdf-o",
    "fa fa-file-text-o",
    "fa fa-file-word-o",
]

class MantisScraper:
    """A class to scrape issues and download files from a MantisBT instance."""
    
    def __init__(self, base_url: str, username_url: str, password_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username_url = username_url
        self.password_url = password_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        logger.info("Session closed.\n")

    def get_issue_list(self, file_path: Path) -> List[str]:
        """Read issue numbers from a file."""
        try:
            if not file_path.is_file():
                raise FileNotFoundError(f"Issue list file {file_path} does not exist.")
            with file_path.open("r") as f:
                issues = [issue.strip() for issue in f.readlines() if issue.strip()]
            logger.info(f"Loaded {len(issues)} issues from {file_path}\n")
            return issues
        except Exception as e:
            logger.error(f"Failed to read issue list: {e}\n")
            raise

    def login(self) -> None:
        """Log in to the MantisBT instance."""
        try:
            # Step 1: Submit username
            username_payload = {"return": "index.php", "username": self.username}
            response = self.session.post(self.username_url, data=username_payload, timeout=10)
            response.raise_for_status()
            if f"Enter password for '{self.username}'" not in response.text:
                raise ValueError("Username submission failed.")

            # Step 2: Submit password
            password_payload = {"return": "login.php", "username": self.username, "password": self.password}
            response = self.session.post(self.password_url, data=password_payload, timeout=10)
            response.raise_for_status()
            if "Assigned to Me (Unresolved)" not in response.text:
                raise ValueError("Login unsuccessful.")
            logger.info("Login successful.\n")
        except requests.RequestException as e:
            logger.error(f"Login failed: {e}\n")
            raise

    def access_issue_page(self, issue: str) -> Optional[requests.Response]:
        """Access a protected issue page."""
        try:
            issue_url = f"{self.base_url}/view.php?id={issue}"
            response = self.session.get(issue_url, timeout=10)
            response.raise_for_status()
            if "View Issue Details" not in response.text:
                logger.error(f"Failed to access issue page {issue}")
                return None
            print("")
            logger.info(f"Successfully accessed issue page {issue}")
            return response
        except requests.RequestException as e:
            logger.error(f"Error accessing issue {issue}: {e}\n")
            return None

    def scrape_page(self, response: requests.Response, issue: str) -> Tuple[BeautifulSoup, str, Path]:
        """Scrape issue page content and save as HTML."""
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            issue_no = soup.title.text.split(':')[0]
            issue_path = DOWNLOADS_DIR / issue_no
            issue_path.mkdir(parents=True, exist_ok=True)

            # Save HTML report
            with (issue_path / f"{issue_no}_report.html").open("w", encoding="utf-8") as f:
                f.write(soup.prettify())
            logger.info(f"Saved HTML report for issue {issue_no}")

            # Remove file icons to avoid duplicate downloads
            for icon_class in icon_class_list:
                for icon in soup.find_all("i", class_=f"{icon_class}"):
                    icon.parent.decompose()

            return soup, issue_no, issue_path
        except Exception as e:
            logger.error(f"Error scraping issue {issue}: {e}")
            raise

    def download_multiple_type_files(self, issue_path: Path, file_links: List[BeautifulSoup]) -> None:
        """Download files from provided links."""
        if not file_links:
            logger.warning("No file links found.")
            return

        logger.info(f"Found {len(file_links)} file links.")
        downloaded_files = set()

        for index, link in enumerate(file_links, 1):
            try:
                relative_url = link["href"]
                file_url = relative_url if relative_url.startswith('http') else f"{self.base_url}/{relative_url.lstrip('/')}"

                file_basename, _file_extension = os.path.splitext(link.text)
                file_extension = _file_extension.lstrip('.')
                
                # This regex sanitizes the file name text:
                    # input:    My new:file/name.pdf
                    # output:   My_new_file_name.pdf
                filename = re.sub(r'[^\w\.-]', '_', f"{file_basename.strip()}.{file_extension}" or f"file_{index}.{file_extension}")

                # Ensure unique filename
                base_name, ext = os.path.splitext(filename)
                counter = 1
                unique_filename = filename
                while unique_filename in downloaded_files:
                    unique_filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                file_path = issue_path / unique_filename
                downloaded_files.add(unique_filename)

                logger.info(f"Downloading {unique_filename} from {file_url}")
                response = self.session.get(file_url, timeout=10, allow_redirects=True)
                response.raise_for_status()

                with file_path.open("wb") as f:
                    f.write(response.content)
                logger.info(f"Saved {unique_filename}")
            except requests.RequestException as e:
                logger.error(f"Failed to download {file_url}: {e}")

def main():
    """Main function to orchestrate the scraping process."""
    try:
        # Prompt for credentials
        username = input("Enter your Mantis username: ")
        password = getpass.getpass(prompt=f"Enter password for {username}: ")

        # Ensure downloads directory exists
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

        with MantisScraper(BASE_URL, USERNAME_URL, PASSWORD_URL, username, password) as scraper:
            scraper.login()
            issues = scraper.get_issue_list(ISSUE_FILE)
            for issue in issues:
                response = scraper.access_issue_page(issue)
                if response:
                    soup, issue_no, issue_path = scraper.scrape_page(response, issue)
                    file_links = soup.find_all("a", href=lambda x: x and "file_download.php" in x)
                    scraper.download_multiple_type_files(issue_path, file_links)
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()