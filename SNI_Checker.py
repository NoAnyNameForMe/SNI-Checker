import os
import re
import ssl
import socket
from typing import List, Optional
from ping3 import ping
from prettytable import PrettyTable
from tqdm import tqdm
import logging

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


def check_tls_version(domain: str, timeout: float = 3.0) -> Optional[str]:
    """
    Checks the TLS version of a domain.

    Arguments:
        domain: The domain to check.
        timeout: The maximum amount of time to wait for a TLS response, in seconds.

    Returns:
        The TLS version of the domain if available, otherwise None.
    """
    try:
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with ssl.create_default_context().wrap_socket(sock, server_hostname=domain) as s:
                tls_version = s.version()
                return tls_version if tls_version else "TLS version not available"
    except ssl.SSLError as e:
        logging.error(f"SSL error occurred while checking domain {domain}: {e}")
        return None
    except socket.error as e:
        logging.error(f"Socket error occurred while checking domain {domain}: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while checking domain {domain}: {e}")
        return None


def ping_domains(domains: List[str], max_domains: Optional[int] = None, total_domains: int = 0, max_success: Optional[int] = None, timeout: float = 3.0, tls_timeout: float = 3.0) -> List[str]:
    """
    Pings a list of domains and checks their TLS version.

    Arguments:
        domains: The list of domains to ping.
        max_domains: The maximum number of domains to check.
        total_domains: The total number of domains.
        max_success: The maximum number of successful domains to find.
        timeout: The maximum amount of time to wait for a ping response, in seconds.
        tls_timeout: The maximum amount of time to wait for a TLS response, in seconds.

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

    with tqdm(total=total_domains, desc='Pinging Domains', unit='Domain') as pbar:
        for index, domain in enumerate(domains):
            if max_domains is not None and index >= max_domains:
                break  # Exit the loop if the maximum number of domains has been reached

            try:
                ping_time = ping(domain, timeout=timeout)
                if ping_time is not None and ping_time <= timeout:
                    ping_time *= 1000
                    tls_version = check_tls_version(domain, timeout=tls_timeout)
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
                        if max_success is not None and success_count >= max_success:
                            break  # Exit the loop if the maximum number of successful domains has been found
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logging.error(f"An error occurred while checking domain {domain}: {e}")
                failed_count += 1

            pbar.set_description(f"Pinging: {domain} ({index+1}/{total_domains})")
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

    # Save only the successful domains (TLSv1.3) per line to a separate file
    only_domains_file = os.path.join(script_dir, "Only Domains Result.txt")
    with open(only_domains_file, "w") as file:
        for domain in success_domains:
            file.write(domain + "\n")

    return list(success_domains)

if __name__ == '__main__':
    file_path = input("Enter the path of the file to scan: ")
    domains = extract_domains(file_path)

    # Prompt the user for the number of domains to check
    max_domains_input = input("Enter the number of domains to check (enter 'all' to check all domains): ")
    if max_domains_input.lower() == 'all':
        max_domains = None  # Set to None to check all domains
    else:
        max_domains = int(max_domains_input)

    # Prompt the user for the maximum number of successful domains to find
    max_success_input = input("Enter the maximum number of successful domains to find (enter 'all' to find all successful domains): ")
    if max_success_input.lower() == 'all':
        max_success = None  # Set to None to find all successful domains
    else:
        max_success = int(max_success_input)

    # Adjust the total value of tqdm progress bar
    total_domains = len(domains) if max_domains is None else min(len(domains), max_domains)

    success_domains = ping_domains(domains, max_domains, total_domains, max_success)
    print("Successful Domains Found:")
    print(success_domains)
