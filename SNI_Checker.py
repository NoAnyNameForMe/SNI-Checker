import os
import re
import ssl
import socket 
from ping3 import ping
from prettytable import PrettyTable
from tqdm import tqdm

def extract_domains(file_path):
    domains = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            match = re.match(r'^([\d.]+)\t(.+)$', line)
            if match:
                domains_str = match.group(2)
                domains_list = re.split(r',\s*', domains_str)
                domains.extend(domains_list)

    # Remove "(more...)" from domain names and exclude domains starting with "*"
    domains = [re.sub(r'\(.*\)', '', domain).strip() for domain in domains if not domain.startswith('*')]

    return domains

def check_tls_version(domain):
    try:
        with ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            tls_version = s.version()
            return tls_version if tls_version else "TLS version not available"
    except Exception as e:
        return None

def ping_domains(domains):
    table = PrettyTable()
    table.field_names = ['Domain', 'Ping Result (ms)', 'TLS Version']

    success_domains_table = PrettyTable()
    success_domains_table.field_names = ['Domain', 'Ping Result (ms)', 'TLS Version']

    success_domains = set()
    success_count = 0
    failed_count = 0

    with tqdm(total=len(domains), desc='Pinging Domains', unit='Domain') as pbar:
        for domain in domains:
            ping_result = ping(domain)
            if ping_result is not None:
                ping_result *= 1000  # Multiply by 1000 if not None
                tls_version = check_tls_version(domain)
                table.add_row([domain, int(ping_result), tls_version])
                success_domains_table.add_row([domain, int(ping_result), tls_version])
                success_domains.add(domain)
                success_count = len(success_domains)
            else:
                table.add_row([domain, "Failed", "N/A"])
                failed_count += 1

            pbar.set_description(f"Pinging: {domain}")
            pbar.set_postfix({'Success': success_count, 'Failed': failed_count})
            pbar.update(1)

    print(table)
    print("\nSuccessful Domains:")
    print(success_domains_table)

    # Get the directory path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Save result to a text file
    output_file = os.path.join(script_dir, "ping_result.txt")
    with open(output_file, "w") as file:
        file.write(str(table))
        file.write("\n\nSuccessful Domains:\n")
        file.write(str(success_domains_table))

# Prompt for file location and run the script
file_location = input("Enter the file location: ")
domains = extract_domains(file_location)
ping_domains(domains)
