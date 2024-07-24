import argparse
import requests
from colorama import init, Fore, Style
import ipaddress

# Initialize colorama
init(autoreset=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Send HTTP requests with various headers.")
    parser.add_argument('--url', required=True, help="Path to the file containing URLs.")
    parser.add_argument('--ips', required=True, help="Path to the file containing IPs or domains.")
    parser.add_argument('-o', '--output', help="Path to the output file.")
    return parser.parse_args()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def expand_ip_range(ip_range):
    network = ipaddress.ip_network(ip_range, strict=False)
    return [str(ip) for ip in network.hosts()]

def send_requests(urls, ips, output=None):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    headers_to_test = ['X-Forwarded-For', 'X-Forwarded-Host']
    results = []

    for url in urls:
        for method in methods:
            for header in headers_to_test:
                for ip in ips:
                    headers = {header: ip}
                    response = requests.request(method, url, headers=headers)
                    status_code = response.status_code
                    title = response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No Title'
                    
                    if status_code == 200:
                        color = Fore.GREEN
                    elif status_code in range(300, 400) or status_code == 404 or status_code in range(500, 600):
                        color = Fore.YELLOW
                    else:
                        color = Fore.RED
                    
                    result_line = f"{color}{status_code} {url} {method} {header}: {ip} - {title}"
                    results.append(result_line)
                    print(result_line)
    
    if output:
        with open(output, 'w') as outfile:
            for line in results:
                # Remove color codes for file output
                clean_line = line.replace(Fore.GREEN, '').replace(Fore.YELLOW, '').replace(Fore.RED, '').replace(Style.RESET_ALL, '')
                outfile.write(clean_line + "\n")

def main():
    args = parse_args()
    urls = read_file(args.url)
    raw_ips = read_file(args.ips)
    
    ips = []
    for ip in raw_ips:
        if '/' in ip:
            ips.extend(expand_ip_range(ip))
        else:
            ips.append(ip)

    send_requests(urls, ips, args.output)

if __name__ == "__main__":
    main()
