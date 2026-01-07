import nmap
import sys
import argparse
from vuln_checker import check_vulnerabilities

def scan_target(ip_address):
    """
    Scans a target IP address for open TCP ports and service versions.

    Args:
        ip_address (str): The target IP address to scan.

    Returns:
        dict: A dictionary of open ports and their service information,
              or None if the scan fails or the host is down.
    """
    nm = nmap.PortScanner()
    try:
        # -sV: Probe open ports to determine service/version info
        # -T4: Aggressive timing template for faster scans
        nm.scan(ip_address, arguments='-sV -T4')

        scan_results = {}

        if ip_address not in nm.all_hosts():
            print(f"[-] Host {ip_address} seems to be down.")
            return None

        host = nm[ip_address]
        if 'tcp' not in host:
            print(f"[*] No open TCP ports found on {ip_address}.")
            return {}

        for port in host['tcp'].keys():
            port_info = host['tcp'][port]
            if port_info['state'] == 'open':
                scan_results[port] = {
                    'service': port_info.get('name', 'unknown'),
                    'product': port_info.get('product', ''),
                    'version': port_info.get('version', '')
                }
        return scan_results
    except nmap.PortScannerError as e:
        print(f"[!] Nmap scan error: {e}. Make sure nmap is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A simple network vulnerability scanner.")
    parser.add_argument("target", help="The target IP address to scan.")
    parser.add_argument("--api-key", help="Your NVD API key for a higher request rate.")
    args = parser.parse_args()

    target = args.target
    api_key = args.api_key

    scan_results = scan_target(target)

    if scan_results:
        print(f"\n[+] Scan Results for {target}:")
        for port, info in scan_results.items():
            print(f"  [+] Port {port}/tcp is open")
            print(f"    - Service: {info.get('service', 'N/A')}")
            print(f"    - Product: {info.get('product', 'N/A')}")
            print(f"    - Version: {info.get('version', 'N/A')}")

            if info.get('product') and info.get('version'):
                print("    [*] Checking for vulnerabilities...")
                vulnerabilities = check_vulnerabilities(info, api_key)
                if vulnerabilities:
                    print("    [!] Found vulnerabilities:")
                    for vuln in vulnerabilities:
                        print(f"      - CVE: {vuln['cve_id']} (Severity: {vuln['severity']})")
                        print(f"        Description: {vuln['description']}\\n")
                else:
                    print("    [+] No known vulnerabilities found for this service version.")
            else:
                print("    [*] Could not determine product/version, skipping vulnerability check.")
            print("-" * 40)
    elif scan_results == {}:
        print(f"[*] No open TCP ports with service information were found on {target}.")
    else:
        # Error messages are printed inside scan_target
        print(f"[-] Scan of {target} failed.")
