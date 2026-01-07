from celery import Celery
from scanner import scan_target
from vuln_checker import check_vulnerabilities

# Configure Celery
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task
def run_full_scan(target, api_key=None):
    """
    A Celery task that runs a full network scan and vulnerability check.
    """
    scan_results = scan_target(target)

    if scan_results:
        for port, info in scan_results.items():
            if info.get('product') and info.get('version'):
                vulnerabilities = check_vulnerabilities(info, api_key)
                scan_results[port]['vulnerabilities'] = vulnerabilities
            else:
                scan_results[port]['vulnerabilities'] = []

    return scan_results
