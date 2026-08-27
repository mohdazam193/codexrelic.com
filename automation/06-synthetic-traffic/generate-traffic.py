import sys
import time
import random
import argparse
import urllib.request
import urllib.error
import concurrent.futures

def generate_traffic(domain, duration_seconds=60, num_users=1):
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
    print(f"Starting synthetic traffic to {base_url} for {duration_seconds} seconds with {num_users} users...")
    
    start_time = time.time()
    
    def simulate_user(user_id):
        request_count = 0
        while time.time() - start_time < duration_seconds:
            endpoint = random.choice(endpoints)
            url = base_url + endpoint
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': f'Synthetic-Traffic-Bot/{user_id}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.getcode()
                    print(f"[User-{user_id}] [SUCCESS] {status} - GET {url}")
            except urllib.error.HTTPError as e:
                print(f"[User-{user_id}] [HTTP ERROR] {e.code} - GET {url}")
            except urllib.error.URLError as e:
                pass
            except Exception as e:
                pass

            request_count += 1
            
            # Random sleep to simulate realistic bursts of traffic
            time.sleep(random.uniform(0.1, 1.5))
        return request_count

    total_requests = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(simulate_user, i) for i in range(num_users)]
        for future in concurrent.futures.as_completed(futures):
            total_requests += future.result()

    print(f"\nFinished! Sent {total_requests} requests in {duration_seconds} seconds across {num_users} users.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic traffic for CodexRelic observability testing.')
    parser.add_argument('--domain', type=str, default='uat.codexrelic.com', help='Target domain (e.g. uat.codexrelic.com)')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds to run traffic')
    parser.add_argument('--users', type=int, default=1, help='Number of concurrent users')
    args = parser.parse_args()

    generate_traffic(args.domain, args.duration, args.users)
