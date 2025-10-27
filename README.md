
# MantisBT Issue Exporter

This script extracts history and route card data from the Mantis Bug Tracker web application using `BeautifulSoup4`. It processes issues by their unique IDs and downloads any associated attachments for each issue into a designated local folder.

> **Note that this script will only work for specific history and route card templates created in MantisBT. If any of the custom sections change in the original template the script will have to be altered.**


## Features

- Extracts data from MantisBT on a per issue basis.
- Creates a Microsoft Word and PDF report with this scraped data.
- Downloads any associated attachements for a issue to a local directory.
- Add hyperlinks to the created report which points to the local downloaded files.
- Saves each issue report in a folder with the name of the category.


## Installation

To run the script [Python](https://www.python.org/) is needed with the depenpecies listed below. At the time of creation `Python 3.13.2` was used. The [uv](https://docs.astral.sh/uv/) package manager was used with this project which will make the installation of the requirements easier.

- Python
- beautifulsoup4
- docx2pdf
- python-docx
- python-dotenv
- requests

Make sure uv is [installed](https://docs.astral.sh/uv/getting-started/installation/):
- `pip install uv`

Once in the root directory of the cloned repo run the following to install the neccessary requirements:
- `uv sync`


## Usage

Before running the script, make sure the required configuration files are in place.

### 1. Environment Configuration (`.env`)

Create a `.env` file in the project root to define connection details for your MantisBT instance.

This file:
- Specifies the MantisBT URLs to be scraped.
- Can optionally store login credentials to skip manual input in debug mode.

Example `.env`

```properties
# .env

# Optional: enables debug mode to use stored credentials instead of prompting
# APP_ENV="debug"

# Required: base URL of your MantisBT instance
BASE_URL=[insert base url]

# Derived URLs (do not modify unless necessary)
USERNAME_URL=${BASE_URL}/login_password_page.php
PASSWORD_URL=${BASE_URL}/login.php

# Optional: credentials (used only in debug mode)
APP_USERNAME="[insert username]"
APP_PASSWORD="[insert password]"
```

### 2. Issue List Configuration (`issue_list.toml`)

Create an `issue_list.toml` file to specify which issue IDs should be scraped.

This file:
- Lists all active issue IDs to process.
- Supports commenting out IDs to exclude them temporarily.

Example `issue_list.toml`

```toml
# issue_list.toml

active_issues = [
    # 11423,  # skipped
    # 11424,  # skipped
    11425,
    # 11426,  # skipped
    # 11427,  # skipped
    11428,
]
```

Once both files are configured, you can run the script with: `uv run main.py`

This will download the data and related attachements into the following folder structure, note that the reports and attachements directories are automatically created of not present. The `hrc_report_template.docx` will be used to populate and create the issue reports.

```bash
root/
├── reports/
│   ├── category_issue_folder_1/
│   │   ├── attachements/
│   │   │   ├── attachement_01.pdf
│   │   │   └── attachement_02.pdf
│   │   ├── issue_report.docx
│   │   ├── issue_report.pdf
│   │   └── issue_report.html
│   ├── category_issue_folder_2/
│   ├── ...
│   └── category_issue_folder_n
├── .env
├── .gitignore
├── .python-version
├── hrc_report_template.docx
├── issue_list.toml
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

> Note that if multiple issues need to be scraped, the PDF conversion can slow down the process significantly. If only the Microsoft Word report is needed the PDF conversion can be disabled by commenting out the following line in the `main.py` file:

`convert(os.path.join(report_path, document_file_name))`

## Support

For support, email [Francois du Plessis](mailto:francoisdl@reutech.co.za).


## License

[MIT](https://choosealicense.com/licenses/mit/)
