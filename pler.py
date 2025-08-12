import argparse
import sys
import socket
import ipaddress
import requests
import threading
threading.Lock()


class Pler:
    def __init__(self, args, targets):
        self.args = args
        self.targets = targets
        self.cloudflare_ips = []
        self.result = []
        self.no_ip_result = []


        # ANSI color codes
        RESET   = "\033[0m"
        BOLD    = "\033[1m"

        # Foreground colors
        self.RED     = "\033[31m"
        self.GREEN   = "\033[32m"
        self.YELLOW  = "\033[33m"
        self.BLUE    = "\033[34m"
        self.MAGENTA = "\033[35m"
        self.CYAN    = "\033[36m"
        self.WHITE   = "\033[37m"
        self.GRAY    = "\033[90m"
        self.RESET   = "\033[0m"

        # Background colors (opsional)
        self.BG_RED     = "\033[41m"
        self.BG_GREEN   = "\033[42m"
        self.BG_YELLOW  = "\033[43m"
        self.BG_BLUE    = "\033[44m"
        self.BG_MAGENTA = "\033[45m"
        self.BG_CYAN    = "\033[46m"
        self.BG_WHITE   = "\033[47m"

        #fetch cloudflare ranges
        self.fetch_cloudflare_ranges()

        #start checking
        self.start()

    
    def start(self):
        threads = []
        max_threads = getattr(self.args, 'threads', 3) 
        for domain in self.targets:
            while threading.active_count() - 1 >= max_threads:
                pass
            t = threading.Thread(target=self.run, args=(domain,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        if self.args.output:
            self.save_output()

    def run(self, domain):
        ip_address = self.resolve_ip(domain)

        if not ip_address:
            self.parse_out(domain, ip_address, False)
            self.result.append({"domain": domain, "ip": "Unknown", "is_cloudflare": False})
            return

        if self.is_cloudflare(ip_address):
            self.parse_out(domain, ip_address, True)
            self.result.append({"domain": domain, "ip": ip_address, "is_cloudflare": True})
        else:
            self.parse_out(domain, ip_address, False)
            self.result.append({"domain": domain, "ip": ip_address, "is_cloudflare": False})
        

    def parse_out(self, domain, ip, is_cloudflare):
        if self.args.filter_type == "ip":
            if self.args.show_cloudflare:
                if is_cloudflare:
                    print(f"{ip}")
            else:
                if is_cloudflare:
                    return

        elif self.args.filter_type == "domain":
            print(f"{domain}")
        elif self.args.filter_type == "domain_ip":
            print(f"{domain} {ip}")
        else:
            return
        



    def save_output(self):
        print(f"Output saved to {self.args.output}")



    def resolve_ip(self, domain):
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except:
            return False

    def is_cloudflare(self, ip_address):
        ip_obj = ipaddress.ip_address(ip_address)
        for cf_range in self.cloudflare_ips:
            if ip_obj in ipaddress.ip_network(cf_range):
                return True
        return False

    def save_output(self):
        pass

    def fetch_cloudflare_ranges(self):
        url = "https://api.cloudflare.com/client/v4/ips?networks=jdcloud"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})
        ipv4 = result.get("ipv4_cidrs", [])
        ipv6 = result.get("ipv6_cidrs", [])
        # jdcloud_cidrs kemungkinan gak ada, jadi cek dulu
        jdcloud = result.get("jdcloud_cidrs", [])  
        self.cloudflare_ips = ipv4 + ipv6 + jdcloud




def main():
    parser = argparse.ArgumentParser(description="Pler is a tool to check if a IP is a Cloudflare IP")
    parser.add_argument("-d", "--domain", help="Target domain to check")
    parser.add_argument("-l", "--list", help="List of domain to check")
    parser.add_argument("-t", "--threads", help="Threads to use", type=int, default=3)
    parser.add_argument("-ft", "--filter-type", help="Filter type. result with detected a cloudflare will not displayed", choices=["ip", "domain", "domain_ip"], default="domain_ip")
    parser.add_argument("-su", "--show-unknown", help="Show unknown IP", action="store_true")
    parser.add_argument("-sc", "--show-cloudflare", help="Show Cloudflare IP", action="store_true")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-s", "--silent", help="Silent mode", action="store_true")
    args = parser.parse_args()


    targets = []

    # check input
    if args.domain:
        targets.append(args.domain)
    elif args.list:
        with open(args.list, "r") as f:
            targets = f.read().splitlines()
    elif not sys.stdin.isatty():
        # read from stdin
        input_data = sys.stdin.read()
        targets = input_data.splitlines()
    else:
        print("Error: -d or -l is required or stdin is not a tty")
        sys.exit(1)
        


    pler = Pler(args, targets)


if __name__ == "__main__":
    main()
