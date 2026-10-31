"""Optional reachability audit. Does not determine rights or delete entries."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import json
from pathlib import Path
import socket
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def check(url):
    request = urllib.request.Request(url, headers={"User-Agent": "PublicDomainTreasuresLinkAudit/1.0", "Accept": "text/html,application/json;q=0.9,*/*;q=0.5"})
    result = {"url": url, "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            # Inspect a small prefix for obvious challenge pages, not asset content.
            prefix = response.read(8192).lower()
            blocked = any(s in prefix for s in [b"verify you are human", b"just a moment...", b"captcha", b"checking your browser"])
            result.update(status=response.status, final_url=response.url,
                          classification="possible_bot_protection" if blocked else ("redirected" if response.url != url else "reachable"))
    except urllib.error.HTTPError as exc:
        classification = {401: "authentication_required", 403: "access_denied_or_bot_protection", 404: "possibly_broken", 410: "possibly_broken", 429: "rate_limited"}.get(exc.code, "server_or_http_error")
        result.update(status=exc.code, final_url=exc.url, classification=classification)
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        result.update(status=None, classification="network_error_or_timeout", detail=str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/link-audit.json")
    args = parser.parse_args()
    entries = json.loads((ROOT / "data/treasures.json").read_text(encoding="utf-8"))
    urls = sorted({e[k] for e in entries for k in ("item_url", "rights_url")})
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, urls))
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {}
    for r in results:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
    print(json.dumps({"unique_urls": len(urls), "responses": counts}, indent=2))
    print("A response, redirect or block is not a copyright determination. Review possible failures manually.")


if __name__ == "__main__":
    main()
