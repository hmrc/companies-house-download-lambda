# companies-house-download-lambda

This repository contains an AWS Lambda function that downloads Companies House bulk data files and stores the extracted data in S3.

## What it does

The Lambda function:
- retrieves the latest download link from the Companies House bulk download pages
- supports the `basic` company data snapshot and the `psc` persons with significant control snapshot
- streams the ZIP archive from `download.companieshouse.gov.uk`
- extracts the single file contained in the archive
- writes the extracted output to an S3 bucket specified by the `BUCKET_NAME` environment variable

The function entry point is `companies_house_download.handler` and the code is implemented in `src/companies_house_download.py`.

## Supported download types

- `basic`: downloads the latest basic company data ZIP and stores the extracted CSV file
- `psc`: downloads the latest persons with significant control snapshot ZIP and stores the extracted JSON file

## Runtime

This project is packaged as a container-based AWS Lambda using Python 3.9.

### License

This code is open source software licensed under the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0.html).
