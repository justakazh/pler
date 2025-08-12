#!/usr/bin/env python3
import argparse
import sys
import socket
import ipaddress
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class Pler:
    def __init__(self, args, targets):
        self.args = args
        self.targets = targets
        self.cloudflare_ips = []
        self.result = []

        # Colors
        self.GREEN = "\033[32m"
        self.RESET = "\033[0m"

        # Fetch Cloudflare ranges
        self.fetch_cloudflare_ranges()

        # Banner
        self.banner()

        # Start checking
        self.start()

    def start(self):
        if not self.targets:
            print(f"[!] No targets provided")
            return

        max_workers = max(1, int(getattr(self.args, 'threads', 3)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.run, domain) for domain in self.targets]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error: {e}")

        if self.args.output:
            self.save_output()

    def run(self, domain):
        ip_address = self.resolve_ip(domain)

        if not ip_address:
            self.parse_out_show(domain, ip_address, False)
            return

        if self.is_cloudflare(ip_address):
            self.parse_out_show(domain, ip_address, True)
        else:
            self.parse_out_show(domain, ip_address, False)

    def parse_out_show(self, domain, ip, is_cloudflare):
        show_unknown = self.args.show_unknown
        show_cloudflare = self.args.show_cloudflare

        # Case 1: Known IP, not Cloudflare
        if ip and not is_cloudflare and not show_unknown and not show_cloudflare:
            self.parse_out_type(domain, ip)

        # Case 2: Unknown IP
        if show_unknown and not ip and not is_cloudflare:
            self.parse_out_type(domain, ip)

        # Case 3: Cloudflare IP
        if show_cloudflare and is_cloudflare:
            self.parse_out_type(domain, ip)

    def parse_out_type(self, domain, ip):
        out_ip = ip if ip else "Unknown"

        if self.args.filter_type == "ip":
            if out_ip not in self.result:
                print(f"{out_ip}")
                self.result.append(out_ip)
        elif self.args.filter_type == "domain":
            if domain not in self.result:
                print(f"{domain}")
                self.result.append(domain)
        elif self.args.filter_type == "domain_ip":
            print(f"{domain} -> {out_ip}")
            self.result.append(f"{domain}:{out_ip}")

    def save_output(self):
        with open(self.args.output, "a", encoding="utf-8") as f:
            f.write("\n".join(self.result) + "\n")
        if not self.args.silent:
            print(f"\n[{self.GREEN}*{self.RESET}] Output saved to {self.GREEN}{self.args.output}{self.RESET}")

    def resolve_ip(self, domain):
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return False

    def is_cloudflare(self, ip_address):
        ip_obj = ipaddress.ip_address(ip_address)
        for cf_range in self.cloudflare_ips:
            if ip_obj in ipaddress.ip_network(cf_range):
                return True
        return False

    def banner(self):
        if not self.args.silent:
            print(f"""
 _____ __    _____ _____ 
|  {self.GREEN}_{self.RESET}  |  |  |   __| {self.GREEN}__{self.RESET}  |
|   __|  |__|   __|    -|
|__|  |_____|_____|__|__|
Probe and Cloudflare Filter
https://github.com/justakazh/pler
""")

    def fetch_cloudflare_ranges(self):
        url = "https://api.cloudflare.com/client/v4/ips?networks=jdcloud"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            ipv4 = result.get("ipv4_cidrs", [])
            ipv6 = result.get("ipv6_cidrs", [])
            jdcloud = result.get("jdcloud_cidrs", [])
            self.cloudflare_ips = ipv4 + ipv6 + jdcloud
        except requests.RequestException as e:
            print(f"[!] Failed to fetch Cloudflare IP ranges: {e}")
            self.cloudflare_ips = []


def main():
    parser = argparse.ArgumentParser(description="Pler is a tool to check if an IP is a Cloudflare IP")
    parser.add_argument("-d", "--domain", help="Target domain to check")
    parser.add_argument("-l", "--list", help="List of domains to check")
    parser.add_argument("-t", "--threads", help="Threads to use", type=int, default=3)
    parser.add_argument("-ft", "--filter-type", choices=["ip", "domain", "domain_ip"], default="domain_ip",
                        help="Filter type. Cloudflare results are hidden unless specified")
    parser.add_argument("-su", "--show-unknown", action="store_true", default=False, help="Show unknown IPs")
    parser.add_argument("-sc", "--show-cloudflare", action="store_true", default=False, help="Show Cloudflare IPs")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-s", "--silent", action="store_true", default=False, help="Silent mode")
    args = parser.parse_args()

    targets = []

    if args.domain:
        targets.append(args.domain)
    elif args.list:
        try:
            with open(args.list, "r", encoding="utf-8") as f:
                targets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] File not found: {args.list}")
            return
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read()
        targets = [line.strip() for line in input_data.splitlines() if line.strip()]

    Pler(args, targets)


if __name__ == "__main__":
    main()
