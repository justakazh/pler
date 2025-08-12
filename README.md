# Pler - Domain Probe and Cloudflare Filter Tool
<img width="1104" height="503" alt="image" src="https://github.com/user-attachments/assets/13220e61-dc9b-4523-988e-5b0151db6f1d" />


**Pler** is a simple yet powerful Python script to check whether a domain is using Cloudflare.  
It is useful for **bug bounty hunters**, **pentesters**, or **OSINT** purposes, as it can filter results according to your needs.

---

## ✨ Features
- **Multi-threading** → fast domain checks.
- **IPv4 & IPv6 support**.
- **Result filtering** → only IP, only domain, or domain + IP.
- **Cloudflare detection** → quickly identify domains behind Cloudflare.
- **Unknown mode** → show domains that cannot be resolved.
- **Save output to file** for later use.
- **Silent Mode** 

---

## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/justakazh/pler.git
cd pler
pip install -r requirements.txt
```

Or install directly from **PyPI** (if published):

```bash
pip install python-pler
```

---

## ⚙️ Usage

```bash
python3 pler.py [options]
```

### Options
| Argument | Description |
|----------|-------------|
| `-d`, `--domain` `<domain>` | Target domain to check. |
| `-l`, `--list` `<file>` | File containing list of domains (one per line). |
| `-t`, `--threads` `<int>` | Number of threads (default: 3). |
| `-ft`, `--filter-type` `{ip,domain,domain_ip}` | Output filter type. |
| `-su`, `--show-unknown` | Show domains with unknown IP. |
| `-sc`, `--show-cloudflare` | Show domains that use Cloudflare. |
| `-o`, `--output` `<file>` | Save results to a file. |
| `-s`, `--silent` | Disable banner & non-essential output. |

---

## 🖥️ Examples

**Check a single domain**
```bash
pler -d example.com
```

**Check from a file**
```bash
pler -l subdomains.txt
```

**Check via STDIN**
```bash
echo "example.com" | pler
cat subdomains.txt | pler
```

**Show only IP addresses**
```bash
cat subdomains.txt | pler -ft ip
```

**Show only domains**
```bash
cat subdomains.txt | pler -ft domain
```

**Show only domains using Cloudflare**
```bash
cat subdomains.txt | pler -sc
```

**Show only unknown IPs**
```bash
cat subdomains.txt | pler -su
```

**Save results to file**
```bash
cat subdomains.txt | pler -ft domain_ip -o result.txt
```

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
