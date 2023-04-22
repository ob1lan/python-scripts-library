import dns.resolver
from tqdm import tqdm
import asyncio
import aiohttp
import time

with open(r"domains.txt", 'r') as file:
    count = 0
    for line in file:
        if line != "\n":
            count += 1
file.close()


async def get(domain, session):
    with open("excluded.txt", 'r') as exclusions:
        excluded = exclusions.read()
    exclusions.close()

    if domain.strip() not in excluded:
        try:
            url = ("http://" + domain).strip()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
            async with session.get(url=url, timeout=5, headers=headers) as response:
                # resp = await response.read()
                # print("Successfully got url {} with resp {} and length {}.".format(url, response.status, len(resp)))
                if response.status == 404:
                    text = await response.text()
                    if "NoSuchBucket" in text:
                        print("Might be an Abandoned Amazon S3 Bucket:", url)
                        answer: dns.resolver.Answer = dns.resolver.resolve(domain.strip(), 'CNAME')
                        for rdata in answer:
                            print(" ->", rdata)
                        f = open("findings.txt", "a")
                        f.write(url + "\n")
                        f.close()
        except aiohttp.client_exceptions.ClientConnectorError:
            pass
        except asyncio.exceptions.TimeoutError:
            pass
        except aiohttp.client_exceptions.ClientOSError:
            pass
        except Exception as e:
            print("Unable to get url {} due to {}.".format(domain.strip(), e.__class__))
            pass
    else:
        print("Excluded:", domain.strip())


async def main(domains):
    async with aiohttp.ClientSession() as session:
        # ret = await asyncio.gather(*[get(domain, session) for domain in domains])
        ret = [get(domain, session) for domain in domains]
        responses = [await f for f in tqdm(asyncio.as_completed(ret), total=len(ret), desc="Progress", unit=" domains")]


with open(r"domains.txt", 'r') as file:
    domains = file
    start = time.time()
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception as e:
        pass
    asyncio.run(main(domains))
    end = time.time()

print("It took {} seconds to query {} domains.".format(end - start, count))
file.close()
