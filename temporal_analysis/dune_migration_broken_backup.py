import time
import json
from urllib.error import HTTPError, URLError

def fetch_page(method, url, payload=None, retries=6):
    for attempt in range(retries):
        try:
            data = None
            headers = {
                "Accept": "application/geo+json",
                "User-Agent": "TERRATIME4D/1.0"
            }

            if method.upper() == "POST":
                data = json.dumps(payload or {}).encode("utf-8")
                headers["Content-Type"] = "application/json"

            request = Request(
                url,
                data=data,
                headers=headers,
                method=method.upper()
            )

            with urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))

        except (HTTPError, URLError, TimeoutError) as error:
            wait = min(10 * (2 ** attempt), 120)
            print(
                f"Request failed ({error}). "
                f"Retry {attempt + 1}/{retries} in {wait}s..."
            )

            if attempt == retries - 1:
                raise

            time.sleep(wait)