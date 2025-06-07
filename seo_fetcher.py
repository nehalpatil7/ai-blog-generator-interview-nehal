import json
import os
from pytrends.request import TrendReq as UTrendReq
import pandas as pd
pd.set_option("future.no_silent_downcasting", True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEO_DATA_FILE = os.path.join(BASE_DIR, "mock_seo_data.json")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en-IN;q=0.9,en;q=0.8,mr;q=0.7,es;q=0.6",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://trends.google.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-arch": '"arm"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-form-factors": '"Desktop"',
    "sec-ch-ua-full-version": '"137.0.7151.55"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="137.0.7151.55", "Chromium";v="137.0.7151.55", "Not/A)Brand";v="24.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"macOS"',
    "sec-ch-ua-platform-version": '"15.3.1"',
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "x-browser-channel": "stable",
    "x-browser-copyright": "Copyright 2025 Google LLC. All rights reserved.",
    "x-browser-validation": "jWhhuGepE5WyX9SzRfjQzPC9+KI=",
    "x-browser-year": "2025",
    "x-client-data": "CLG1yQEIjLbJAQiltskBCKmdygEIu+HKAQiVocsBCJGjywEIhqDNAQie7c4BCN3uzgEIkvHOAQij8s4B",
    'cookie': 'S=billing-ui-v3=iBOwcyOwaD_6wHnaHsKV3axGqtMUeX3e:billing-ui-v3-efe=iBOwcyOwaD_6wHnaHsKV3axGqtMUeX3e; SID=g.a000xQhamFWlfZUnidf7T9lFzTWBVQDO-44PcT9rP0zx7SJDcNLsDQsOYO7wzlhppEQcX3SK4AACgYKAT4SARASFQHGX2Mi9sXTKpkGB9D1vFiXFgab7RoVAUF8yKq9pQogHgvcWJT_eFjhMjOa0076; __Secure-1PSID=g.a000xQhamFWlfZUnidf7T9lFzTWBVQDO-44PcT9rP0zx7SJDcNLs5v7U9EDBreQT7EEMjnniywACgYKAXISARASFQHGX2Miw93earxaKLI67VWkIXPb8RoVAUF8yKr8NB7xhXV8qUA_D5AB2JIg0076; __Secure-3PSID=g.a000xQhamFWlfZUnidf7T9lFzTWBVQDO-44PcT9rP0zx7SJDcNLsKFKL3bktvT2iKZVZ1UsWGQACgYKAZMSARASFQHGX2MiMMkMGd7uVjz3rP7I9mpg3BoVAUF8yKr77Ss9r7iZ_JO2WjLxey7H0076; HSID=A5B09nLcvj6yJddsI; SSID=A2I7QlUYPcfO942vI; APISID=7nkV896wVmbgdwVb/AcgSwSgeh6cikCT23; SAPISID=qQ5wjPt5BA-y9N57/AXoYdpn7Qwc9-077e; __Secure-1PAPISID=qQ5wjPt5BA-y9N57/AXoYdpn7Qwc9-077e; __Secure-3PAPISID=qQ5wjPt5BA-y9N57/AXoYdpn7Qwc9-077e; SEARCH_SAMESITE=CgQIjJ4B; AEC=AVh_V2hPuPMRRBZndfUJO568-xzw6pcLOzZc5ikNezBKGW5xAcVobwLNJY4; NID=524=by78HlkXDTM4meMHNQO5wDP3RIQ6_FLwFBNzw7jJc51ZzGq0bZ5ak033-SOrRz1Zp6kz9cIMps410t9pQe4IHC_wkCgT7bgjnD50dX9DyxJZQR4dM7x568rHO-LhgTidrJxKN6TlfLKLbUMrpM5bNtcn68KYmpF0rguE17H_EO8Gk2NLzVTTFk9tbuwynamR1Whqi7MKoP0X9OZrU2kd8mazAt_SNrpAm20VbVyka2p1FiBV2PUG1RXTRjrSvJl0XfIpUxB6vwHHSO8FET5N2u_rOE3OT88yFCOadv3LwNVHCR7CMDnFJWEqj4dUupvzBxgFPyEhhgATm8h3Wi5g20jOMk1kge-19ELuwkZeHUZz439BB3mHML-5cnat5ta1Ieg0tAqpRK2StMgnsVo-J-8yiADZSBRnGhoyK3KD4fsKZcPMx0TCTW5VOOQdAHvqWnY_AmHcDn8PhniZ8WEhtmqLiFxmV18OndjkXcd3Boz74VXUqMmhEfnkmRBvHtFTav4AWZ8OJ8daLPY4gwVdZIHgTw-T_gFP3xvsKWLSrzeE2ZhiFhPCUtGztfeD8atyw_-t2RDBtMtSfc4WXuURhz75nmO5kXfiQCqHfo9mm6w8y9zXoqyNm2YZUdr1zJWMNpTf6X2Pegp20sxb59c-VquZMqvu5XPmV6Ng4dh8ke-mhkVivAhqYw6Wf7Z2ZEBEAgCVSyQXoZlwNAnZiQsj3dCXBw67XLZubojawbCOlFZjZhwXDPStwMYKyrmalxkbt4q9okRSdgISwvmPDxIhjjiKhtZ86H_ME3erSgsOP_93jHKIm0bynofoXcJm616DmvcM; OTZ=8111312_76_80_104160_76_446820; __Secure-1PSIDTS=sidts-CjIB5H03PzH2Ms5Z2qhxEwpK8fk38cZkzvyLF2RRR-6hwzzUrq59lOszomnT1b8HcCyJABAA; __Secure-3PSIDTS=sidts-CjIB5H03PzH2Ms5Z2qhxEwpK8fk38cZkzvyLF2RRR-6hwzzUrq59lOszomnT1b8HcCyJABAA; SIDCC=AKEyXzUM66LTtZw2sZR5Q-FzMHcQ5Y-GnfXVrLcXVAu8JUxPNOKw72FmHUW6VCIdymZvHN30_Ns; __Secure-1PSIDCC=AKEyXzXPCwlBuuQ2rHw1eTsUlmoQQNQhcx10o5s0oKSDLOFyYHPmqr15J8eY9yK9j9vNtwE3WaA; __Secure-3PSIDCC=AKEyXzXEYbkrHOMbCVtBu6P78016XvmNlpXaRZYqDCabCWmp4Gi8guJIKi3_QjzBOUofVMt7dbo',
}

# Override the _get_data method to add headers
class TrendReq(UTrendReq):
    def _get_data(self, url, method="GET", trim_chars=0, **kwargs):
        return super()._get_data(
            url, method=method, trim_chars=trim_chars, headers=headers, **kwargs
        )

# Now instantiate pytrends using the custom TrendReq
pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10, 25),
)

def get_seo_data(keyword: str) -> dict:
    """
    Fetches SEO data, combining real Google Trends data with mock data for metrics
    not provided by Google Trends (search volume, keyword difficulty, avg cpc).

    Args:
        keyword (str): The target keyword for which to fetch SEO data.

    Returns:
        dict: A dictionary containing combined SEO metrics and trends data.
              Includes: search_volume, keyword_difficulty, avg_cpc (from mock),
              relative_interest_score, related_queries (from pytrends), and notes.
              Includes an 'error_trends' key if trends data fetching fails.
    """
    # 1. Initialize data with default values and load mock data as fallback/supplement
    combined_seo_data = {
        "search_volume": None,
        "keyword_difficulty": None,
        "avg_cpc": None,
        "notes": "No specific notes from mock data.",
        "trends": {
            "relative_interest_score": "N/A",
            "related_queries": [],
            "error_trends": None,
        },
        "error_seo_fetcher": None,
    }

    mock_data_loaded = False
    try:
        with open(SEO_DATA_FILE, "r", encoding="utf-8") as f:
            all_mock_seo_data = json.load(f)
        normalized_keyword = keyword.lower()
        # Get specific keyword data or fallback to 'default' if keyword is not in mock data
        mock_keyword_data = all_mock_seo_data.get(
            normalized_keyword, all_mock_seo_data.get("default", {})
        )

        # Merge mock data into the combined data
        combined_seo_data["search_volume"] = mock_keyword_data.get("search_volume", 0)
        combined_seo_data["keyword_difficulty"] = mock_keyword_data.get(
            "keyword_difficulty", 0
        )
        combined_seo_data["avg_cpc"] = mock_keyword_data.get("avg_cpc", 0.0)
        combined_seo_data["notes"] = mock_keyword_data.get(
            "notes", "No specific notes from mock data."
        )
        mock_data_loaded = True

    except (FileNotFoundError, json.JSONDecodeError) as e:
        combined_seo_data["error_seo_fetcher"] = (
            f"Warning: Could not load or parse mock SEO data file: {e}. Using trends data only."
        )
        print(combined_seo_data["error_seo_fetcher"])
    except Exception as e:
        combined_seo_data["error_seo_fetcher"] = (
            f"An unexpected error occurred loading mock data: {e}"
        )
        print(combined_seo_data["error_seo_fetcher"])

    # 2. Fetch Google Trends data
    try:
        pytrends.build_payload([keyword], cat=0, timeframe="today 12-m", geo="")

        interest_over_time_df = pytrends.interest_over_time()
        if not interest_over_time_df.empty and keyword in interest_over_time_df.columns:
            # Get the average relative interest over the period (0-100)
            combined_seo_data["trends"]["relative_interest_score"] = (
                interest_over_time_df[keyword].mean().round(2)
            )
        else:
            combined_seo_data["trends"]["relative_interest_score"] = "No data"

        # Get Related Queries
        related_queries_dict = pytrends.related_queries()
        if (
            keyword in related_queries_dict
            and related_queries_dict[keyword] is not None
        ):
            # Extract 'top' queries
            top_queries_df = related_queries_dict[keyword].get("top")
            if top_queries_df is not None and not top_queries_df.empty:
                combined_seo_data["trends"]["related_queries"] = top_queries_df.to_dict(
                    orient="records"
                )

    except Exception as e:
        trends_error_msg = f"Failed to fetch Google Trends data for '{keyword}': {e}"
        combined_seo_data["trends"]["error_trends"] = trends_error_msg
        print(trends_error_msg)

    return combined_seo_data


if __name__ == "__main__":
    print("--- Testing seo_fetcher.py with pytrends integration ---")

    keywords_to_test = [
        "wireless earbuds",
        # "best budget smartphone",
        # "sustainable living tips",
        # "quantum computing breakthroughs",
        # "xyz non-existent keyword 123",
    ]

    for kw in keywords_to_test:
        print(f"\n--- Fetching data for: '{kw}' ---")
        data = get_seo_data(kw)
        print(json.dumps(data, indent=2))

        if data.get("error_seo_fetcher"):
            print(f"  Note: General SEO fetcher error: {data['error_seo_fetcher']}")
        if data.get("trends", {}).get("error_trends"):
            print(
                f"  Note: Trends data for '{kw}' failed: {data['trends']['error_trends']}"
            )
