import requests
import time

BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def check_vulnerabilities(service_info, api_key=None):
    """
    Queries the NVD API for vulnerabilities related to a specific service.

    Args:
        service_info (dict): A dictionary containing 'product' and 'version'.
        api_key (str, optional): An NVD API key for higher rate limits. Defaults to None.

    Returns:
        list: A list of found vulnerabilities (CVEs), or an empty list if none are found
              or an error occurs.
    """
    product = service_info.get('product')
    version = service_info.get('version')

    if not product or not version:
        return []

    search_query = f"{product} {version}"

    params = {
        'keywordSearch': search_query,
        'noRejected': ''
    }

    headers = {
        'User-Agent': 'NVD-Vulnerability-Scanner/1.0'
    }
    if api_key:
        headers['apiKey'] = api_key

    try:
        # With an API key, the NVD allows 50 requests in a rolling 30-second window.
        # Without a key, it's 5 requests in 30 seconds.
        delay = 0.6 if api_key else 6.0
        time.sleep(delay)

        response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        vulnerabilities = []
        if 'vulnerabilities' in data:
            for item in data['vulnerabilities']:
                cve = item['cve']
                cve_id = cve['id']
                description = "No description available."
                if cve.get('descriptions'):
                    for desc in cve['descriptions']:
                        if desc['lang'] == 'en':
                            description = desc['value']
                            break

                severity = "N/A"
                if 'metrics' in cve and 'cvssMetricV31' in cve['metrics']:
                    severity = f"{cve['metrics']['cvssMetricV31'][0]['cvssData']['baseScore']} ({cve['metrics']['cvssMetricV31'][0]['cvssData']['baseSeverity']})"

                vulnerabilities.append({
                    'cve_id': cve_id,
                    'description': description,
                    'severity': severity
                })

        return vulnerabilities

    except requests.exceptions.RequestException as e:
        print(f"[!] Error querying NVD API: {e}")
        return []
    except Exception as e:
        print(f"[!] An unexpected error occurred during vulnerability check: {e}")
        return []
