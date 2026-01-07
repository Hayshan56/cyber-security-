# Web-Based Network Vulnerability Scanner (Asynchronous)

This is a web-based network vulnerability scanner that uses a Flask web server, a Celery task queue for asynchronous scanning, and a Redis message broker.

## Features

- **Asynchronous Scanning:** Scans are run in the background, allowing for a non-blocking user interface.
- **Web Dashboard:** A simple, user-friendly web interface for running scans and viewing results.
- **Port Scanning:** Uses `nmap` to discover open TCP ports.
- **Service & Version Detection:** Identifies the software and version running on open ports.
- **Vulnerability Lookup:** Queries the NVD for CVEs related to the discovered services.
- **Reporting:** Displays a clear report of open ports, services, and associated vulnerabilities.

## Prerequisites

- **Python 3:** The script is written for Python 3.
- **nmap:** The `nmap` command-line tool must be installed and in your system's PATH.
- **Redis:** A Redis server must be running on `localhost:6379`. You can install it with `sudo apt-get install redis-server` on Debian/Ubuntu or download from [redis.io](https://redis.io/download).

## Installation

1.  **Clone the repository.**
2.  **Set up a virtual environment.**
3.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## NVD API Key (Recommended)

To significantly improve the scanner's speed, it is highly recommended to obtain a free API key from the [NVD](https://nvd.nist.gov/developers/request-an-api-key) and enter it in the web form.

## Usage

You will need to run three separate processes in three different terminals.

1.  **Start the Redis server** (if not already running):
    ```bash
    redis-server
    ```

2.  **Start the Celery worker:**
    Navigate to the project directory and run:
    ```bash
    celery -A celery_worker.celery worker --loglevel=info
    ```

3.  **Run the Flask web server:**
    ```bash
    python app.py
    ```

4.  **Open your web browser** and navigate to `http://127.0.0.1:5000`.

5.  Enter the target IP and optional NVD API key and start the scan.

## Production Deployment

For a production environment, do not use the built-in Flask development server (`app.run(debug=True)`). Instead, use a production-grade WSGI server like Gunicorn or uWSGI.

Example with Gunicorn:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

## Disclaimer

This tool is for educational purposes and authorized security testing only.
