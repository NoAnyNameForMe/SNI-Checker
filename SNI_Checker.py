import os
import re
import ssl
import socket
from typing import List, Optional
from ping3 import ping
from prettytable import PrettyTable
from tqdm import tqdm


def extract_domains(file_path: str) -> List[str]:
    """
    Extracts domains from a file with IP addresses and domain names.

    Arguments:
        file_path: The path to the file containing IP addresses and domain names.

    Returns:
        A list of domain names extracted from the file.
    """
    domains = []
    with open(file_path) as file:
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


def check_tls_version(domain: str) -> Optional[str]:
    """
    Checks the TLS version of a domain.

    Arguments:
        domain: The domain to check.

    Returns:
        The TLS version of the domain if available, otherwise None.
    """
    try:
        with ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            tls_version = s.version()
            return tls_version if tls_version else "TLS version not available"
    except ssl.SSLError:
        return None
    except socket.error:
        return None


def ping_domains(domains: List[str]) -> List[str]:
    """
    Pings a list of domains and checks their TLS version.

    Arguments:
        domains: The list of domains to ping.

    Returns:
        A list of successful domains that responded to ping.
    """
    table = PrettyTable()
    table.field_names = ['Domain', 'Ping Result (ms)', 'TLS Version']

    success_domains_table = PrettyTable()
    success_domains_table.field_names = ['Domain', 'Ping Result (ms)', 'TLS Version']

    # Get the directory path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    success_domains = set()
    success_count = 0
    failed_count = 0

    with tqdm(total=len(domains), desc='Pinging Domains', unit='Domain') as pbar:
        for domain in domains:
            ping_time = ping(domain)
            if ping_time is not None:
                ping_time *= 1000  # Multiply by 1000 if not None
                tls_version = check_tls_version(domain)
                table.add_row([domain, int(ping_time), tls_version])
                if tls_version == 'TLSv1.3':
                    success_domains_table.add_row([domain, int(ping_time), tls_version])
                    success_domains.add(domain)
                    success_count = len(success_domains)
                    # Save the middle results to a text file
                    output_file = os.path.join(script_dir, "Temp Domains Result.txt")
                    with open(output_file, "w") as file:
                        file.write(str(table))
                        file.write("\n\nSuccessful Domains (TLSv1.3) until now:\n")
                        file.write(str(success_domains_table))
                else:
                    failed_count += 1
            else:
                table.add_row([domain, "Failed", "N/A"])
                failed_count += 1

            pbar.set_description(f"Pinging: {domain}")
            pbar.set_postfix({'Success': success_count, 'Failed': failed_count})
            pbar.update(1)

    print(table)
    print("\nSuccessful Domains (TLSv1.3):")
    print(success_domains_table)

    # Save result to a text file
    output_file = os.path.join(script_dir, "Temp Domains Result.txt")
    if os.path.exists(output_file):
        os.remove(output_file)
    output_file = os.path.join(script_dir, "Domains Result.txt")
    with open(output_file, "w") as file:
        file.write(str(table))
        if success_domains:
            file.write("\n\nSuccessful Domains (TLSv1.3):\n")
            file.write(str(success_domains_table))

    return list(success_domains)


if __name__ == '__main__':
    file_path = input("Enter the path of the file to scan: ")
    domains = extract_domains(file_path)
    ping_domains(domains)
