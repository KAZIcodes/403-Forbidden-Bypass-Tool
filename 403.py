import argparse
import requests
from colorama import init, Fore, Style
import ipaddress
import os
import time

# Initialize colorama
init(autoreset=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Send HTTP requests with various headers.")
    parser.add_argument('--urls', help="Path to the file containing URLs.")
    parser.add_argument('-url', help="Single URL to test.")
    parser.add_argument('--ips', required=True, help="Path to the file containing IPs or domains.")
    parser.add_argument('--headers', help="Path to the file containing headers to test.")
    parser.add_argument('--verb_tamper', action='store_true', help="Perform verb tampering with multiple HTTP methods.")
    parser.add_argument('-o', '--output', help="Path to the output file.")
    parser.add_argument('-t', '--time_delay', type=float, default=0, help="Time delay between each request in seconds.")
    return parser.parse_args()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def expand_ip_range(ip_range):
    network = ipaddress.ip_network(ip_range, strict=False)
    return [str(ip) for ip in network.hosts()]

def send_requests(urls, ips, headers_to_test, verb_tamper, time_delay, output=None):
    methods = ['GET', 'POST', 'PUT', 'DELETE'] if verb_tamper else ['GET']
    results = []

    for url in urls:
        for method in methods:
            for header in headers_to_test:
                for ip in ips:
                    headers = {header: ip}
                    response = requests.request(method, url, headers=headers)
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
                    
                    time.sleep(time_delay)
    
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
        if '/' in ip:
            ips.extend(expand_ip_range(ip))
        else:
            ips.append(ip)
    
    headers_file = args.headers if args.headers else 'default_headers.txt'
    if not os.path.isfile(headers_file):
        print(f"Error: Headers file '{headers_file}' not found.")
        return
    
    headers_to_test = read_file(headers_file)
    send_requests(urls, ips, headers_to_test, args.verb_tamper, args.time_delay, args.output)

if __name__ == "__main__":
    main()
