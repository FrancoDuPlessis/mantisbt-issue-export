
# MantisBT Issue Exporter

This script extracts data from the Mantis Bug Tracker web application using `BeautifulSoup4`. It processes issues by their unique IDs and downloads any associated attachments for each issue into a designated local folder.


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

Before the script can be run a list of MantisBT issue ids which need to be scraped must be saved in the `issue_list.toml` file. The reason for using a `*.toml` file is that issue numbers can be commented out in this file.

```toml
active_issues = [
    # 11423,
    # 11424,
    11425,
    # 11426,
    # 11427,
    11428,
]
```

When this is done the script can be run with: `uv run main.py`

This will download the data and related attachements into the following folder structure:

[insert data]


## Support

For support, email [Francois du Plessis](mailto:francoisdl@reutech.co.za).


## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [insert data]