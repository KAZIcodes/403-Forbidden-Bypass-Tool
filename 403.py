import argparse
import requests
from colorama import init, Fore, Style
import ipaddress
import os
import time
import json

# Initialize colorama
init(autoreset=True)

# Suppress InsecureRequestWarning from urllib3
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

PROGRESS_FILE = 'progress.json'

def parse_args():
    parser = argparse.ArgumentParser(description="Send HTTP requests with various headers.")
    parser.add_argument('--urls', help="Path to the file containing URLs.")
    parser.add_argument('-url', help="Single URL to test.")
    parser.add_argument('--ips', required=True, help="Path to the file containing IPs or domains.")
    parser.add_argument('--headers', help="Path to the file containing default headers to test.")
    parser.add_argument('--verb_tamper', action='store_true', help="Perform verb tampering with multiple HTTP methods.")
    parser.add_argument('--proxy', help="Proxy URL to use for the requests.")
    parser.add_argument('-H', action='append', help="Custom headers to include or replace in the request (e.g., -H 'User-Agent: mamad').")
    parser.add_argument('-o', '--output', help="Path to the output file.")
    parser.add_argument('-t', '--time_delay', type=float, default=0, help="Time delay between each request in seconds.")
    parser.add_argument('--resume', action='store_true', help="Resume from the last saved state.")
    return parser.parse_args()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def expand_ip_range(ip_range):
    network = ipaddress.ip_network(ip_range, strict=False)
    return [str(ip) for ip in network.hosts()]

def save_progress(url_index, method_index, header_index, ip_index):
    with open(PROGRESS_FILE, 'w') as file:
        json.dump({
            'url_index': url_index,
            'method_index': method_index,
            'header_index': header_index,
            'ip_index': ip_index
        }, file)

def load_progress():
    if os.path.isfile(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as file:
            return json.load(file)
    return None

def send_requests(urls, ips, headers_to_test, custom_headers, verb_tamper, time_delay, proxy, output=None, resume=False):
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] if verb_tamper else ['GET']
    results = []

    # Set up proxy if provided
    proxies = {
        "http": proxy,
        "https": proxy
    } if proxy else None

    start_point = {
        'url_index': 0,
        'method_index': 0,
        'header_index': 0,
        'ip_index': 0
    }

    if resume:
        progress = load_progress()
        if progress:
            start_point = progress

    for url_index, url in enumerate(urls[start_point['url_index']:], start=start_point['url_index']):
        for method_index, method in enumerate(methods[start_point['method_index']:], start=start_point['method_index']):
            for header_index, header in enumerate(headers_to_test[start_point['header_index']:], start=start_point['header_index']):
                for ip_index, ip in enumerate(ips[start_point['ip_index']:], start=start_point['ip_index']):
                    headers = {header: ip}
                    # Include or replace custom headers
                    if custom_headers:
                        for custom_header in custom_headers:
                            key, value = custom_header.split(':', 1)
                            headers[key.strip()] = value.strip()
                    
                    try:
                        response = requests.request(method, url, headers=headers, verify=False, proxies=proxies)
                        status_code = response.status_code
                        response_size = len(response.content)
                        title = response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No Title'
                        
                        if status_code == 200:
                            color = Fore.GREEN
                        elif status_code in range(300, 400) or status_code == 404 or status_code in range(500, 600):
                            color = Fore.YELLOW
                        else:
                            color = Fore.RED
                        
                        result_line = f"{color}{status_code} {url} {method} {header}: {ip} - {title} (Size: {response_size} bytes)"
                        results.append(result_line)
                        print(result_line)
                        
                    except requests.RequestException as e:
                        print(f"Request to {url} failed: {e}")

                    time.sleep(time_delay)

                    save_progress(url_index, method_index, header_index, ip_index)
    
    if output:
        with open(output, 'w') as outfile:
            for line in results:
                # Remove color codes for file output
                clean_line = line.replace(Fore.GREEN, '').replace(Fore.YELLOW, '').replace(Fore.RED, '').replace(Style.RESET_ALL, '')
                outfile.write(clean_line + "\n")


def main():
    args = parse_args()
    
    if not args.urls and not args.url:
        print("Error: Either --urls or -url must be specified.")
        return
    
    if args.urls:
        urls = read_file(args.urls)
    else:
        urls = [args.url]
    
    raw_ips = read_file(args.ips)
    
    ips = []
    for ip in raw_ips:
        if '/' in ip and '://' not in ip:
            ips.extend(expand_ip_range(ip))
        else:
            ips.append(ip)
    
    headers_file = args.headers if args.headers else 'default_headers.txt'
    if not os.path.isfile(headers_file):
        print(f"Error: Headers file '{headers_file}' not found.")
        return
    
    headers_to_test = read_file(headers_file)
    send_requests(urls, ips, headers_to_test, args.H, args.verb_tamper, args.time_delay, args.proxy, args.output, args.resume)

if __name__ == "__main__":
    main()
