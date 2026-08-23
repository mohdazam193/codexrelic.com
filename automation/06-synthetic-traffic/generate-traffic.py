import sys
import time
import random
import argparse
import urllib.request
import urllib.error

def generate_traffic(domain, duration_seconds=60):
    endpoints = [
        "/",
        "/api/movies",
        "/api/blogs",
        "/resume.html",
        "/movies.html",
        "/blog.html",
        "/admin/login.html",
        "/nonexistent-page-404", # to generate 404s
    ]

    base_url = f"https://{domain}"
    print(f"Starting synthetic traffic to {base_url} for {duration_seconds} seconds...")
    
    start_time = time.time()
    request_count = 0

    while time.time() - start_time < duration_seconds:
        endpoint = random.choice(endpoints)
        url = base_url + endpoint
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Synthetic-Traffic-Bot/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                print(f"[SUCCESS] {status} - GET {url}")
        except urllib.error.HTTPError as e:
            print(f"[HTTP ERROR] {e.code} - GET {url}")
        except urllib.error.URLError as e:
            print(f"[URL ERROR] Failed to reach {url}: {e.reason}")
        except Exception as e:
            print(f"[ERROR] {e} on GET {url}")

        request_count += 1
        
        # Random sleep to simulate realistic bursts of traffic (0.1 to 1.5 seconds)
        time.sleep(random.uniform(0.1, 1.5))

    print(f"\nFinished! Sent {request_count} requests in {duration_seconds} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic traffic for CodexRelic observability testing.')
    parser.add_argument('--domain', type=str, default='uat.codexrelic.com', help='Target domain (e.g. uat.codexrelic.com)')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds to run traffic')
    args = parser.parse_args()

    generate_traffic(args.domain, args.duration)
