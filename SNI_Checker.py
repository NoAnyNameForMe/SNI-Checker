import os
import re
import ssl
import socket
import subprocess
from typing import List, Optional
from ping3 import ping
from prettytable import PrettyTable
from tqdm import tqdm
import speedtest
import time
import traceback


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

    # Get the directory path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Save result to a text file
    output_file = os.path.join(script_dir, "Domains Result.txt")
    with open(output_file, "w") as file:
        file.write(str(table))
        if success_domains:
            file.write("\n\nSuccessful Domains (TLSv1.3):\n")
            file.write(str(success_domains_table))

    if input("Do you want to perform a speed test on the successful domains with TLSv1.3? (y/n)").lower() == "y":
        # Perform speed test on successful domains
        speed_test_domains(list(success_domains))

    return list(success_domains)

def speed_test_domains(domains: List[str]) -> None:
    """
    Performs a speed test on a list of domains.

    Arguments:
        domains: The list of domains to test.
    """
    table = PrettyTable()
    table.field_names = ['Domain', 'Ping Result (ms)', 'TLS Version', 'Download Speed (Mbps)', 'Upload Speed (Mbps)']

    total_download = 0
    total_upload = 0

    with tqdm(total=len(domains), desc='Speed Testing Domains', unit='Domain') as pbar:
        for domain in domains:
            pbar.set_description(f"Testing: {domain}")
            ping_time = ping(domain)
            if ping_time is not None:
                ping_time *= 1000  # Multiply by 1000 if not None
                tls_version = check_tls_version(domain)
                if tls_version == 'TLSv1.3':
                    try:
                        st = speedtest.Speedtest()
                        st.get_best_server()
                        st.download()
                        st.upload()
                        download_speed = st.results.download / 1000000  # Download speed in Mbps
                        upload_speed = st.results.upload / 1000000  # Upload speed in Mbps
                        table.add_row([domain, int(ping_time), tls_version, round(download_speed, 2), round(upload_speed, 2)])
                        total_download += st.results.bytes_received  # Accumulate actual download size
                        total_upload += st.results.bytes_sent  # Accumulate actual upload size
                    except Exception as e:
                        table.add_row([domain, int(ping_time), tls_version, "Error", "Error"])
                        traceback.print_exc()  # Print the exception traceback
            pbar.update(1)
            time.sleep(5)  # Add a 5-second delay between each domain to avoid overloading the server

    total_download_mb = total_download / (1024 * 1024)  # Convert to MB
    total_upload_mb = total_upload / (1024 * 1024)  # Convert to MB

    print(table)
    print(f"Total Download Data Transfer: {round(total_download_mb, 2)} MB")  # Display the total download data transfer in MB
    print(f"Total Upload Data Transfer: {round(total_upload_mb, 2)} MB")  # Display the total upload data transfer in MB

    # Get the directory path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Save result to a text file
    output_file = os.path.join(script_dir, "Speed Test Result.txt")
    with open(output_file, "w") as file:
        file.write(str(table))
        file.write(f"Total Download Data Transfer: {round(total_download_mb, 2)} MB\n")  # Save the total download data transfer in MB
        file.write(f"Total Upload Data Transfer: {round(total_upload_mb, 2)} MB\n")  # Save the total upload data transfer in MB

if __name__ == '__main__':
    file_path = input("Enter the path of the file to scan: ")
    domains = extract_domains(file_path)
    ping_domains(domains)
