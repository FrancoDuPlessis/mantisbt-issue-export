import os
import re
import requests
from bs4 import BeautifulSoup


# Define URLs for the login pages
username_url = "http://mantis.rrs.co.za/login_password_page.php"
password_url = "http://mantis.rrs.co.za/login.php"

# Credentials   
username = "Francoisdl"
password = "gTf{<=$DT9cJ7FgS"

folder_path = "downloads"
base_url = "http://mantis.rrs.co.za/"

# Create the folder if it doesn't exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


def main():

    # Create a session to persist cookies
    session = requests.Session()

    # Step 1: Submit username to the first page
    username_payload = {
        "return": "index.php",
        "username": username
    }
    response_username = session.post(username_url, data=username_payload)
    
    # Check if the request was successful
    if response_username.status_code == 200:
        print("Username submitted successfully")
    else:
        print(f"Failed to submit username: {response_username.status_code}")
        exit()
    
    # Step 2: Submit password to the second page
    password_payload = {
        "return": "login.php",
        "username": username,
        "password": password
    }
    response_password = session.post(password_url, data=password_payload)

    # Check if the login was successful
    if response_password.status_code == 200:
        print("Password submitted successfully")
        if "Assigned to Me (Unresolved)" in response_password.text:
            print("Login successful!")
        else:
            print("Login may have failed. Check response content.")
    else:
        print(f"Failed to submit password: {response_password.status_code}")

    # Access a protected issue page
    protected_issue_page = "http://mantis.rrs.co.za/view.php?id=13513"
    response_issue_page = session.get(protected_issue_page)
    if response_issue_page.status_code == 200:
        print("Successfully accessed protected page")
    else:
        print(f"Failed to access protected page: {response_issue_page.status_code}")
    

    # Scrape contents from issue page with BeautifulSoup
    soup = BeautifulSoup(response_issue_page.text, "html.parser")

    # Get the issue number
    issue_no = soup.title.text.split(':')[0]
    issue_path = os.path.join(folder_path, issue_no)
    # Create a issue directory in the downloads folder
    if not os.path.exists(issue_path):
        os.makedirs(issue_path)

    # Write the context of the page to a HTML file
    with open(f"{issue_path}/{issue_no}_report.html", "wt") as file:
        file.write(soup.prettify())

    # Remove the PDf icon links from the soup as to not download the file multiple times.
    pdf_icons = soup.find_all("i", class_="fa fa-file-pdf-o")
    for i, i_tag in enumerate(pdf_icons):
        parent_tag = i_tag.parent
        parent_tag.decompose()
    
    pdf_links = soup.find_all("a", href=lambda x: x and "file_download.php" in x)

    if not pdf_links:
        print("No PDF links found on the page.")
    else:
        print(f"Found {len(pdf_links)} potential PDF links.")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

        # Track downloaded files to avoid duplicate filenames
        downloaded_files = set()

        for index, link in enumerate(pdf_links, 1):
            # Extract the href value
            relative_url = link["href"]

            # Construct the full URL
            file_url = file_url = relative_url if relative_url.startswith('http') else os.path.join(base_url, relative_url.lstrip('/'))

            # Extract filename from <a> tag text or use default
            filename = link.text.strip() if link.text.strip() else f'downloaded_file_{index}.pdf'

            # Sanitize filename: remove invalid characters and ensure .pdf extension
            filename = re.sub(r'[^\w\.-]', '_', filename)  # Replace invalid chars with _
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'

            # Ensure unique filename to avoid overwriting
            base_name, ext = os.path.splitext(filename)
            counter = 1
            unique_filename = filename
            while unique_filename in downloaded_files:
                unique_filename = f"{base_name}_{counter}{ext}"
                counter += 1
            file_path = os.path.join(issue_path, unique_filename)
            downloaded_files.add(unique_filename)

            print(f"Attempting to download file {index}/{len(pdf_links)}: {unique_filename} from {file_url}")

            try:
                # Use the authenticated session to download the file
                file_response = session.get(file_url, headers=headers, allow_redirects=True)
                
                # Check if the request was successful
                if file_response.status_code == 200:
                    content_type = file_response.headers.get('content-type', '').lower()
                    print(f"  Content-Type: {content_type}")

                    if 'application/pdf' in content_type:
                        with open(file_path, 'wb') as f:
                            f.write(file_response.content)
                            print(f"  Saved as {file_path}")
                else:
                    print(f"Unexpected content type: {content_type}. The response may not be a PDF.")
            except:
                pass

    # Close the session
    session.close()


if __name__ == "__main__":
    main()
