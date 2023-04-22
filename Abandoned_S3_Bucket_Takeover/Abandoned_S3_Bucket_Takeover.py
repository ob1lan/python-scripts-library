import requests
import dns.resolver
from tqdm import tqdm

with open(r"domains.txt", 'r') as file:
    count = 0
    for line in file:
        if line != "\n":
            count += 1
print('Total Domains', count)
file.close()

with open(r"domains.txt", 'r') as file:
    for domain in tqdm(file, total=count, desc="Progress", unit=" domains"):
        excluded = open("excluded.txt")
        if domain.strip() not in excluded:
            url = ("http://" + domain).strip()
            try:
                session = requests.Session()
                session.max_redirects = 4
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
                session.headers = headers
                r = session.get(url, timeout=5)
                if r.status_code == 404:
                    if "NoSuchBucket" in r.text:
                        print("Might be an Abandoned Amazon S3 Bucket:", url)
                        answer: dns.resolver.Answer = dns.resolver.resolve(domain.strip(), 'CNAME')
                        for rdata in answer:
                            print(" ->", rdata)
                        f = open("findings.txt", "a")
                        f.write(url + "\n")
                        f.close()
            except requests.ConnectionError:
                pass
            except requests.exceptions.TooManyRedirects:
                f = open("excluded.txt", "a")
                f.write(url + "\n")
                f.close()
                pass
            except requests.exceptions.ReadTimeout:
                f = open("excluded.txt", "a")
                f.write(url + "\n")
                f.close()
                pass
        else:
            print("Excluded:", domain.strip())
file.close()
