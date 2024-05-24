import logging
import os
import re
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup
from smart_open import open
from stream_unzip import stream_unzip

logger = logging.getLogger()
logger.setLevel("INFO")

CH_BASE_URL = "https://download.companieshouse.gov.uk"
BUCKET = os.environ["BUCKET_NAME"]
BASE_DIR = "companies_house"

# for each each download option we provide a tuple of (path, regex) to find the file
DOWNLOAD_OPTIONS = {
    "basic": (
        f"{CH_BASE_URL}/en_output.html",
        r"^BasicCompanyDataAsOneFile-20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].zip$",
        "csv",
    ),
    "psc": (
        f"{CH_BASE_URL}/en_pscdata.html",
        r"^persons-with-significant-control-snapshot-20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].zip$",
        "json",
    ),
}


def find_link(page_url: str, link_re: str):
    r = httpx.get(page_url)
    soup = BeautifulSoup(r.content, "html.parser")
    links = soup.find_all("a", attrs={"href": re.compile(link_re)})
    link_count = len(links)
    if link_count != 1:
        raise ValueError(f"expected to find exactly one link, but found {link_count}")
    return links[0].get("href")


def zipped_chunks(url: str):
    # Iterable that yields the bytes of a zip file
    with httpx.stream("GET", url) as r:
        yield from r.iter_bytes(chunk_size=65536)


def unzip_url(url: str, path: str):
    chunks = zipped_chunks(url)
    file_count = 0
    for file_name, file_size, unzipped_chunks in stream_unzip(chunks):
        file_count += 1
        if file_count > 1:
            raise ValueError("found more than one file in the archive")
        file_name = str(file_name, "utf-8")
        logger.info(f"unzipping {file_name}: {file_size}")

        target_path = f"s3://{BUCKET}/{path}/{file_name}"
        logger.info(f"writing {path}")

        with open(path, "wb") as fout:
            for chunk in unzipped_chunks:
                fout.write(chunk)


def handler(event: Dict[Any, Any], _):
    logger.info("event:")
    logger.info(event)

    try:
        download_type = event["download_type"]
    except:
        raise ValueError('required parameter "download_type" not found')

    try:
        url, link_re, ext = DOWNLOAD_OPTIONS[download_type]
    except:
        raise ValueError(
            f"\"{download_type}\" is not a valid option for \"download_type\", should be one of [{', '.join(DOWNLOAD_OPTIONS.keys())}]"
        )

    logger.info(f"looking for link at {url}")
    download_href = find_link(url, link_re)
    download_uri = f"{CH_BASE_URL}/{download_href}"
    logger.info(f"downloading data from {download_uri}")
    unzip_url(
        download_uri, f"s3://{BUCKET}/{BASE_DIR}/companies_house_{download_type}.{ext}"
    )

    return {
        "statusCode": 200,
        "body": f"Successfully extracted companies house {download_type} data",
    }
