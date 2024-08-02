# 403 Forbidden Bypass Tool

## Description

This script is designed for penetration testing and bug bounty hunting, specifically to bypass 403 Forbidden endpoints discovered during the reconnaissance phase. It achieves this by leveraging the following methodology:

The script adds specific headers, such as **X-Forwarded-For** or **X-Forwarded-Host**, or other headers listed in the **default_headers.txt** file, to the HTTP requests. It then tests these requests with different user provided IP address or domain values that are related to the target company. These IPs or domains are typically gathered during the reconnaissance phase and may include the company's CIDR ranges for example.

The objective is to trick the upstream server into perceiving these IPs or domains as the origin of the request, potentially bypassing security restrictions and gaining access to restricted resources. This method exploits the possibility that the upstream server trusts certain IP ranges or domains specified in the headers and permits access accordingly.

Long story short, this script is good when you have some endpoints with 403 response and want to bypass them with above methodology.

This script allows you to:

- Send HTTP requests with your provided bypass headers instead of **default_headers.txt**
- Provide CIDR ranges in the IPs or domains file, and it will automatically expand and test all IPs within those ranges
- Include additional custom headers provided via the command line
- Perform verb tampering with 'GET', 'POST', 'PUT', 'PATCH' and 'DELETE’ HTTP methods for each request
- Use a proxy for the requests
- Specify a delay between each request (specially good for when fuzzing a service behind a CDN or WAF)
- Save the results to an output file

## Options

- `--urls`: Path to the file containing line separated URLs
- `-url`: Single URL to test
- `--ips`: Path to the file containing line separated IPs or domains to test
- `--headers`: Path to the file containing line separated bypass headers to test
- `--verb_tamper`: Perform verb(HTTP method) tampering by specifying this switch
- `-H`: Custom headers to include or replace in the request (e.g., `-H 'User-Agent: random'`)
- `--proxy`: Proxy URL to use for the requests.
- `-t`, `--time_delay`: Time delay between each request in seconds
- `--resume`: Resume from the last saved state
- `-o`, `--output`: Path to the output file

Note that if —headers is not specified then default_headers.txt will be used and if —verb_tamper is not specified then the requests are only made with ’GET’ method and if -H or —proxy or -t options are not specified the requests will be made with no proxy and no time delay and no additional headers.

## Dependencies

- Python 3.x
- `requests` library
- `colorama` library

## Installation

Clone the repository and install the required Python libraries using pip:

```
git clone https://github.com/KAZIcodes/403-Forbidden-Bypass-Tool.git
pip install requests colorama
```

## Usage Examples

```
python3 403.py --urls urls.txt --ips ips.txt --headers headers.txt --verb_tamper -o results.txt -t 10

python3 403.py -url https://example.com --ips ips.txt -H 'User-Agent: CustomAgent' --proxy http://proxyserver:8080 -o results.txt
```
