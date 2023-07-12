import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

NPM_REGISTRY_URL = 'https://registry.npmjs.org/-/v1/search'


def is_external(url, base_url):
    return not url.startswith(base_url)


def find_scripts(url):
    parsed_url = urlparse(url)
    base_url = "{0.scheme}://{0.netloc}".format(parsed_url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script', src=True)

    # Convert relative URLs to absolute URLs and check if they are external
    external_scripts = [urljoin(base_url, script['src']) for script in scripts if is_external(script['src'], base_url)]

    return external_scripts


def find_npm_packages(script_url):
    response = requests.get(script_url)

    # Match 'require' calls that don't start with './'
    require_packages = set(re.findall(r'require\(["\'](?!./)(.*?)["\']\)', response.text))

    # Match '_requiredBy' arrays
    required_by_packages = set(re.findall(r'"_requiredBy":\["/(.*?)"', response.text))

    # Match '_resolved' URLs
    resolved_packages = set(
        re.findall(r'"_resolved":"http://npm.stepstone.com/repository/npm/(.*?)/-/.*?"', response.text))

    # Combine all packages
    packages = require_packages | required_by_packages | resolved_packages

    return packages


def check_org_registered(package):
    response = requests.get(NPM_REGISTRY_URL, params={'text': package})

    if response.status_code != 200:
        print(f'Error checking package {package}: {response.status_code}')
        return False

    package_info = response.json()
    for result in package_info['objects']:
        if result['package']['name'] == package:
            return True

    return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)

    url = sys.argv[1]  # Get the URL from command line arguments
    external_scripts = find_scripts(url)

    for script in external_scripts:
        print(f'Checking script: {script}')
        packages = find_npm_packages(script)
        for package in packages:
            print(f'Found package: {package}')
            if check_org_registered(package):
                print(f'Organization for {package} is registered')
            else:
                print('\033[91m' + f'WARNING:' + '\033[0m' + f'In script: {script}, organization for {package} may not be registered')


if __name__ == "__main__":
    main()
