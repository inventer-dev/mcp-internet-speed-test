"""
Model Context Protocol for the internet speed test

This MCP implements an internet speed test service inspired by SpeedOf.Me methodology.

## How It Works

An internet speed test uses an incremental testing approach:

### Download Test
- Begins with downloading the smallest sample size (128 KB)
- Gradually increases file size until download takes more than 8 seconds
- Uses the last sample that took more than 8 seconds for final speed calculation

### Upload Test
- Similar incremental mechanism for uploads
- Starts with a smaller sample file and gradually increases
- Continues until upload takes more than 8 seconds

### Test Method
- Tests bandwidth in several passes with gradually increasing file sizes
- Can measure a wide range of connection speeds (from 10 Kbps to 100+ Mbps)
- Sample files sizes range from 128 KB to 512 MB

"""

import contextlib
import re
import time

import httpx
from mcp.server.fastmcp import Context, FastMCP, Icon
from mcp.server.session import ServerSession


async def safe_report_progress(context, progress: int, total: int, message: str) -> None:
    """Safely report progress, handling cases where context is unavailable."""
    if context is None:
        return
    with contextlib.suppress(ValueError, AttributeError):
        await context.report_progress(progress=progress, total=total, message=message)


async def safe_log_info(context, log_message: str) -> None:
    """Safely log info message, handling cases where context is unavailable."""
    if context is None:
        return
    with contextlib.suppress(ValueError, AttributeError):
        await context.info(log_message)

# Create a singleton instance of FastMCP
mcp = FastMCP("internet_speed_test", dependencies=["httpx"])

# Icons for tools (using data URIs for emoji-based icons)
_SVG_TPL = (
    "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'><text y='80' font-size='80'>{}</text></svg>"
)
ICON_DOWNLOAD = Icon(src=_SVG_TPL.format("⬇️"), mimeType="image/svg+xml")
ICON_UPLOAD = Icon(src=_SVG_TPL.format("⬆️"), mimeType="image/svg+xml")
ICON_LATENCY = Icon(src=_SVG_TPL.format("⏱️"), mimeType="image/svg+xml")
ICON_JITTER = Icon(src=_SVG_TPL.format("📊"), mimeType="image/svg+xml")
ICON_SERVER = Icon(src=_SVG_TPL.format("🖥️"), mimeType="image/svg+xml")
ICON_COMPLETE = Icon(src=_SVG_TPL.format("🚀"), mimeType="image/svg+xml")

# Default URLs for testing
GITHUB_USERNAME = "inventer-dev"  # Replace with your GitHub username
GITHUB_REPO = "speed-test-files"  # Replace with your repository name
GITHUB_BRANCH = "main"  # Replace with your branch name (main or master)

# Build base URL for GitHub raw content
GITHUB_RAW_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}"
)

DEFAULT_DOWNLOAD_URLS = {
    "128KB": f"{GITHUB_RAW_URL}/128KB.bin",
    "256KB": f"{GITHUB_RAW_URL}/256KB.bin",
    "512KB": f"{GITHUB_RAW_URL}/512KB.bin",
    "1MB": f"{GITHUB_RAW_URL}/1MB.bin",
    "2MB": f"{GITHUB_RAW_URL}/2MB.bin",
    "5MB": f"{GITHUB_RAW_URL}/5MB.bin",
    "10MB": f"{GITHUB_RAW_URL}/10MB.bin",
    "20MB": f"{GITHUB_RAW_URL}/20MB.bin",
    "40MB": f"{GITHUB_RAW_URL}/40MB.bin",
    "50MB": f"{GITHUB_RAW_URL}/50MB.bin",
    "100MB": f"{GITHUB_RAW_URL}/100MB.bin",
}

# Distributed upload endpoints for geographic diversity
UPLOAD_ENDPOINTS = [
    {
        "url": "https://httpi.dev/",
        "name": "Cloudflare Workers (Global)",
        "provider": "Cloudflare",
        "priority": 1,  # Highest priority due to global distribution
    },
    {
        "url": "https://httpbin.org/",
        "name": "HTTPBin (AWS)",
        "provider": "AWS",
        "priority": 2,
    },
]

# Primary endpoints for backward compatibility
DEFAULT_UPLOAD_URL = UPLOAD_ENDPOINTS[0]["url"] + "post"  # Use Cloudflare by default
DEFAULT_LATENCY_URL = UPLOAD_ENDPOINTS[0]["url"] + "get"  # Use Cloudflare by default

# File sizes in bytes for upload testing
UPLOAD_SIZES = {
    "128KB": 128 * 1024,
    "256KB": 256 * 1024,
    "512KB": 512 * 1024,
    "1MB": 1 * 1024 * 1024,
    "2MB": 2 * 1024 * 1024,
    "5MB": 5 * 1024 * 1024,
    "10MB": 10 * 1024 * 1024,
    "20MB": 20 * 1024 * 1024,
    "40MB": 40 * 1024 * 1024,
    "50MB": 50 * 1024 * 1024,
    "100MB": 100 * 1024 * 1024,
}

# Maximum time threshold for a test (in seconds)
DEFAULT_TEST_DURATION = 8.0
MIN_TEST_DURATION = 1.0
MAX_TEST_DURATION = 8.0
ADDITIONAL_TEST_DURATION = 4.0

# Size progression order
SIZE_PROGRESSION = [
    "128KB",
    "256KB",
    "512KB",
    "1MB",
    "2MB",
    "5MB",
    "10MB",
    "20MB",
    "40MB",
    "50MB",
    "100MB",
]

# Server location mapping based on Fastly POP codes
FASTLY_POP_LOCATIONS = {
    "MEX": "Mexico City, Mexico",
    "QRO": "Querétaro, Mexico",
    "DFW": "Dallas, Texas, USA",
    "LAX": "Los Angeles, California, USA",
    "NYC": "New York City, New York, USA",
    "MIA": "Miami, Florida, USA",
    "LHR": "London, United Kingdom",
    "FRA": "Frankfurt, Germany",
    "AMS": "Amsterdam, Netherlands",
    "CDG": "Paris, France",
    "NRT": "Tokyo, Japan",
    "SIN": "Singapore",
    "SYD": "Sydney, Australia",
    "GRU": "São Paulo, Brazil",
    "SCL": "Santiago, Chile",
    "BOG": "Bogotá, Colombia",
    "MAD": "Madrid, Spain",
    "MIL": "Milan, Italy",
    "STO": "Stockholm, Sweden",
    "CPH": "Copenhagen, Denmark",
    "ZUR": "Zurich, Switzerland",
    "VIE": "Vienna, Austria",
    "WAW": "Warsaw, Poland",
    "PRG": "Prague, Czech Republic",
    "BUD": "Budapest, Hungary",
    "ATH": "Athens, Greece",
    "IST": "Istanbul, Turkey",
    "DXB": "Dubai, UAE",
    "BOM": "Mumbai, India",
    "DEL": "New Delhi, India",
    "ICN": "Seoul, South Korea",
    "HKG": "Hong Kong",
    "TPE": "Taipei, Taiwan",
    "KUL": "Kuala Lumpur, Malaysia",
    "BKK": "Bangkok, Thailand",
    "CGK": "Jakarta, Indonesia",
    "MNL": "Manila, Philippines",
    "PER": "Perth, Australia",
    "AKL": "Auckland, New Zealand",
    "JNB": "Johannesburg, South Africa",
    "CPT": "Cape Town, South Africa",
    "CAI": "Cairo, Egypt",
    "LOS": "Lagos, Nigeria",
    "NBO": "Nairobi, Kenya",
    "YYZ": "Toronto, Canada",
    "YVR": "Vancouver, Canada",
    "GIG": "Rio de Janeiro, Brazil",
    "LIM": "Lima, Peru",
    "UIO": "Quito, Ecuador",
    "CCS": "Caracas, Venezuela",
    "PTY": "Panama City, Panama",
    "SJO": "San José, Costa Rica",
    "GUA": "Guatemala City, Guatemala",
    "SDQ": "Santo Domingo, Dominican Republic",
    "SJU": "San Juan, Puerto Rico",
}

# Cloudflare data center locations mapping
CLOUDFLARE_POP_LOCATIONS = {
    "DFW": "Dallas, Texas, USA",
    "LAX": "Los Angeles, California, USA",
    "SJC": "San Jose, California, USA",
    "SEA": "Seattle, Washington, USA",
    "ORD": "Chicago, Illinois, USA",
    "MCI": "Kansas City, Missouri, USA",
    "ATL": "Atlanta, Georgia, USA",
    "MIA": "Miami, Florida, USA",
    "EWR": "Newark, New Jersey, USA",
    "IAD": "Washington, D.C., USA",
    "YYZ": "Toronto, Canada",
    "YVR": "Vancouver, Canada",
    "LHR": "London, United Kingdom",
    "CDG": "Paris, France",
    "FRA": "Frankfurt, Germany",
    "AMS": "Amsterdam, Netherlands",
    "ARN": "Stockholm, Sweden",
    "CPH": "Copenhagen, Denmark",
    "OSL": "Oslo, Norway",
    "HEL": "Helsinki, Finland",
    "WAW": "Warsaw, Poland",
    "PRG": "Prague, Czech Republic",
    "VIE": "Vienna, Austria",
    "ZUR": "Zurich, Switzerland",
    "MIL": "Milan, Italy",
    "FCO": "Rome, Italy",
    "MAD": "Madrid, Spain",
    "BCN": "Barcelona, Spain",
    "LIS": "Lisbon, Portugal",
    "ATH": "Athens, Greece",
    "IST": "Istanbul, Turkey",
    "SVO": "Moscow, Russia",
    "LED": "St. Petersburg, Russia",
    "HKG": "Hong Kong",
    "NRT": "Tokyo, Japan",
    "KIX": "Osaka, Japan",
    "ICN": "Seoul, South Korea",
    "PVG": "Shanghai, China",
    "PEK": "Beijing, China",
    "SIN": "Singapore",
    "KUL": "Kuala Lumpur, Malaysia",
    "BKK": "Bangkok, Thailand",
    "CGK": "Jakarta, Indonesia",
    "MNL": "Manila, Philippines",
    "SYD": "Sydney, Australia",
    "MEL": "Melbourne, Australia",
    "PER": "Perth, Australia",
    "AKL": "Auckland, New Zealand",
    "BOM": "Mumbai, India",
    "DEL": "New Delhi, India",
    "BLR": "Bangalore, India",
    "MAA": "Chennai, India",
    "DXB": "Dubai, UAE",
    "DOH": "Doha, Qatar",
    "KWI": "Kuwait City, Kuwait",
    "JNB": "Johannesburg, South Africa",
    "CPT": "Cape Town, South Africa",
    "LAD": "Luanda, Angola",
    "CAI": "Cairo, Egypt",
    "LOS": "Lagos, Nigeria",
    "NBO": "Nairobi, Kenya",
    "GRU": "São Paulo, Brazil",
    "GIG": "Rio de Janeiro, Brazil",
    "FOR": "Fortaleza, Brazil",
    "SCL": "Santiago, Chile",
    "LIM": "Lima, Peru",
    "BOG": "Bogotá, Colombia",
    "UIO": "Quito, Ecuador",
    "PTY": "Panama City, Panama",
    "SJO": "San José, Costa Rica",
    "MEX": "Mexico City, Mexico",
    "QRO": "Querétaro, Mexico",
}

# AWS CloudFront edge location POP codes mapping
AWS_POP_LOCATIONS = {
    # North America
    "ATL": "Atlanta, Georgia, USA",
    "BOS": "Boston, Massachusetts, USA",
    "ORD": "Chicago, Illinois, USA",
    "CMH": "Columbus, Ohio, USA",
    "DFW": "Dallas, Texas, USA",
    "DEN": "Denver, Colorado, USA",
    "DTW": "Detroit, Michigan, USA",
    "IAH": "Houston, Texas, USA",
    "MCI": "Kansas City, Missouri, USA",
    "LAX": "Los Angeles, California, USA",
    "MIA": "Miami, Florida, USA",
    "MSP": "Minneapolis, Minnesota, USA",
    "BNA": "Nashville, Tennessee, USA",
    "JFK": "New York, New York, USA",
    "EWR": "Newark, New Jersey, USA",
    "PHL": "Philadelphia, Pennsylvania, USA",
    "PHX": "Phoenix, Arizona, USA",
    "PIT": "Pittsburgh, Pennsylvania, USA",
    "HIO": "Portland, Oregon, USA",
    "SLC": "Salt Lake City, Utah, USA",
    "SFO": "San Francisco, California, USA",
    "SEA": "Seattle, Washington, USA",
    "TPA": "Tampa, Florida, USA",
    "IAD": "Washington, DC, USA",
    "YUL": "Montreal, Quebec, Canada",
    "YTO": "Toronto, Ontario, Canada",
    "YVR": "Vancouver, British Columbia, Canada",
    "QRO": "Querétaro, Mexico",
    # South America
    "BOG": "Bogotá, Colombia",
    "EZE": "Buenos Aires, Argentina",
    "FOR": "Fortaleza, Brazil",
    "LIM": "Lima, Peru",
    "GIG": "Rio de Janeiro, Brazil",
    "SCL": "Santiago, Chile",
    "GRU": "São Paulo, Brazil",
    # Europe
    "AMS": "Amsterdam, Netherlands",
    "ATH": "Athens, Greece",
    "TXL": "Berlin, Germany",
    "BRU": "Brussels, Belgium",
    "OTP": "Bucharest, Romania",
    "BUD": "Budapest, Hungary",
    "CPH": "Copenhagen, Denmark",
    "DUB": "Dublin, Ireland",
    "DUS": "Düsseldorf, Germany",
    "FRA": "Frankfurt am Main, Germany",
    "HAM": "Hamburg, Germany",
    "HEL": "Helsinki, Finland",
    "LIS": "Lisbon, Portugal",
    "LHR": "London, United Kingdom",
    "MAD": "Madrid, Spain",
    "MAN": "Manchester, United Kingdom",
    "MRS": "Marseille, France",
    "MXP": "Milan, Italy",
    "MUC": "Munich, Germany",
    "OSL": "Oslo, Norway",
    "PMO": "Palermo, Italy",
    "CDG": "Paris, France",
    "PRG": "Prague, Czech Republic",
    "FCO": "Rome, Italy",
    "SOF": "Sofia, Bulgaria",
    "ARN": "Stockholm, Sweden",
    "VIE": "Vienna, Austria",
    "WAW": "Warsaw, Poland",
    "ZAG": "Zagreb, Croatia",
    "ZRH": "Zurich, Switzerland",
    "IST": "Istanbul, Turkey",
    # Middle East
    "DXB": "Dubai, UAE",
    "FJR": "Fujairah, UAE",
    "JED": "Jeddah, Saudi Arabia",
    "BAH": "Manama, Bahrain",
    "MCT": "Muscat, Oman",
    "DOH": "Doha, Qatar",
    "TLV": "Tel Aviv, Israel",
    # Africa
    "CAI": "Cairo, Egypt",
    "CPT": "Cape Town, South Africa",
    "JNB": "Johannesburg, South Africa",
    "LOS": "Lagos, Nigeria",
    "NBO": "Nairobi, Kenya",
    # Asia Pacific
    "BKK": "Bangkok, Thailand",
    "PEK": "Beijing, China",
    "BLR": "Bengaluru, India",
    "MAA": "Chennai, India",
    "DEL": "New Delhi, India",
    "HAN": "Hanoi, Vietnam",
    "SGN": "Ho Chi Minh City, Vietnam",
    "HKG": "Hong Kong, China",
    "HYD": "Hyderabad, India",
    "CGK": "Jakarta, Indonesia",
    "CCU": "Kolkata, India",
    "KUL": "Kuala Lumpur, Malaysia",
    "MNL": "Manila, Philippines",
    "BOM": "Mumbai, India",
    "KIX": "Osaka, Japan",
    "PNQ": "Pune, India",
    "ICN": "Seoul, South Korea",
    "PVG": "Shanghai, China",
    "SZX": "Shenzhen, China",
    "SIN": "Singapore",
    "TPE": "Taoyuan, Taiwan",
    "NRT": "Tokyo, Japan",
    "ZHY": "Zhongwei, China",
    # Australia & Oceania
    "AKL": "Auckland, New Zealand",
    "BNE": "Brisbane, Australia",
    "MEL": "Melbourne, Australia",
    "PER": "Perth, Australia",
    "SYD": "Sydney, Australia",
}


def extract_server_info(headers: dict[str, str]) -> dict[str, str | None]:
    """
    Extract server information from HTTP headers.

    Args:
        headers: HTTP response headers

    Returns:
        Dictionary with server information including POP location, CDN info, etc.
    """
    server_info = {
        "cdn_provider": None,
        "pop_code": None,
        "pop_location": None,
        "served_by": None,
        "via_header": None,
        "cache_status": None,
        "server_ip_info": None,
        "x_cache": None,
    }

    # Extract x-served-by header (Fastly specific)
    served_by = headers.get("x-served-by", "")
    if served_by:
        server_info["served_by"] = served_by

        # Extract POP code from served-by header
        # Format: cache-mex4329-MEX, cache-qro4141-QRO
        pop_match = re.search(r"-([A-Z]{3})$", served_by)
        if pop_match:
            server_info["pop_code"] = pop_match.group(1)
            server_info["pop_location"] = FASTLY_POP_LOCATIONS.get(
                pop_match.group(1), f"Unknown location ({pop_match.group(1)})",
            )
            server_info["cdn_provider"] = "Fastly"

    # Extract via header
    via = headers.get("via", "")
    if via:
        server_info["via_header"] = via

    # Extract cache status
    cache_status = headers.get("x-cache", "")
    if cache_status:
        server_info["x_cache"] = cache_status
        server_info["cache_status"] = "HIT" if "HIT" in cache_status.upper() else "MISS"

    # Extract Cloudflare CF-Ray header
    cf_ray = headers.get("cf-ray", "")
    if cf_ray:
        server_info["cf_ray"] = cf_ray
        # Extract data center code from CF-Ray (format: request_id-datacenter_code)
        cf_match = re.search(r"-([A-Z]{3})$", cf_ray)
        if cf_match:
            server_info["pop_code"] = cf_match.group(1)
            server_info["pop_location"] = CLOUDFLARE_POP_LOCATIONS.get(
                cf_match.group(1), f"Unknown location ({cf_match.group(1)})",
            )
            server_info["cdn_provider"] = "Cloudflare"

    # Extract AWS CloudFront headers
    cf_pop = headers.get("x-amz-cf-pop", "")
    cf_id = headers.get("x-amz-cf-id", "")
    if cf_pop:
        server_info["cf_pop"] = cf_pop
        server_info["cdn_provider"] = "Amazon CloudFront"

        # Extract POP code from x-amz-cf-pop header (format: DFW56-P1, SIN5-C1)
        cf_pop_match = re.search(r"^([A-Z]{3})", cf_pop)
        if cf_pop_match:
            server_info["pop_code"] = cf_pop_match.group(1)
            server_info["pop_location"] = AWS_POP_LOCATIONS.get(
                cf_pop_match.group(1), f"Unknown location ({cf_pop_match.group(1)})",
            )

    if cf_id:
        server_info["cf_id"] = cf_id
        if not server_info["cdn_provider"]:
            server_info["cdn_provider"] = "Amazon CloudFront"

    # Check for other CDN indicators
    if not server_info["cdn_provider"]:
        if "fastly" in headers.get("server", "").lower():
            server_info["cdn_provider"] = "Fastly"
        elif "cloudflare" in headers.get("server", "").lower():
            server_info["cdn_provider"] = "Cloudflare"
        elif (
            "amazon" in headers.get("server", "").lower()
            or "aws" in headers.get("server", "").lower()
        ):
            server_info["cdn_provider"] = "Amazon CloudFront"

    return server_info


# Register tools
@mcp.tool(icons=[ICON_DOWNLOAD])
async def measure_download_speed(
    size_limit: str = "100MB",
    sustain_time: int = 8,
    context: Context[ServerSession, None] = None,
) -> dict:
    """
    Measure download speed using incremental file sizes.

    Args:
        size_limit: Maximum file size to test (default: 100MB)
        sustain_time: Duration in seconds for each test (1-8, default: 8)

    Returns:
        Dictionary with download speed results
    """
    # Validate sustain_time
    sustain_time = max(MIN_TEST_DURATION, min(MAX_TEST_DURATION, float(sustain_time)))
    results = []
    final_result = None

    # Find the index of the size limit in our progression
    max_index = (
        SIZE_PROGRESSION.index(size_limit)
        if size_limit in SIZE_PROGRESSION
        else len(SIZE_PROGRESSION) - 1
    )

    total_steps = max_index + 1
    current_step = 0

    await safe_log_info(context, "Starting download speed test...")

    # Test each file size in order, up to the specified limit
    async with httpx.AsyncClient() as client:
        for size_key in SIZE_PROGRESSION[: max_index + 1]:
            current_step += 1
            progress_message = f"Testing {size_key} file..."
            await safe_report_progress(context, current_step, total_steps, progress_message)
            if size_key in ["100MB", "200MB", "500MB", "1GB"]:
                test_duration = sustain_time + ADDITIONAL_TEST_DURATION
            else:
                test_duration = sustain_time

            url = DEFAULT_DOWNLOAD_URLS[size_key]
            start = time.time()
            total_size = 0

            async with client.stream(
                "GET",
                url,
            ) as response:
                # Extract server information from headers
                server_info = extract_server_info(dict(response.headers))

                async for chunk in response.aiter_bytes(chunk_size=1024):
                    if chunk:
                        chunk_size = len(chunk)
                        total_size += chunk_size

                        # Check elapsed time during download
                        current_time = time.time()
                        elapsed_time = current_time - start

                        # Update our final result continuously
                        speed_mbps = ((total_size * 8) / (1024 * 1024)) / elapsed_time
                        final_result = {
                            "download_speed": round(speed_mbps, 2),
                            "elapsed_time": round(elapsed_time, 2),
                            "data_size": total_size,
                            "size": size_key,
                            "url": url,
                            "server_info": server_info,
                        }

                        # If test duration exceeded, stop the test
                        if elapsed_time >= test_duration:
                            break

    # Return the final result or an error if all tests failed
    if final_result:
        return {
            "download_speed": final_result["download_speed"],
            "unit": "Mbps",
            "elapsed_time": final_result["elapsed_time"],
            "data_size": final_result["data_size"],
            "size_used": final_result["size"],
            "server_info": final_result["server_info"],
            "all_tests": results,
        }
    return {
        "error": True,
        "message": "All download tests failed",
        "details": results,
    }


@mcp.tool(icons=[ICON_UPLOAD])
async def measure_upload_speed(
    url_upload: str = DEFAULT_UPLOAD_URL,
    size_limit: str = "100MB",
    sustain_time: int = 8,
    context: Context[ServerSession, None] = None,
) -> dict:
    """
    Measure upload speed using incremental file sizes.

    Args:
        url_upload: URL to upload data to
        size_limit: Maximum file size to test (default: 100MB)
        sustain_time: Duration in seconds for each test (1-8, default: 8)

    Returns:
        Dictionary with upload speed results
    """
    # Validate sustain_time
    sustain_time = max(MIN_TEST_DURATION, min(MAX_TEST_DURATION, float(sustain_time)))
    results = []
    final_result = None

    # Find the index of the size limit in our progression
    max_index = (
        SIZE_PROGRESSION.index(size_limit)
        if size_limit in SIZE_PROGRESSION
        else len(SIZE_PROGRESSION) - 1
    )

    total_steps = max_index + 1
    current_step = 0

    await safe_log_info(context, "Starting upload speed test...")

    # Only test up to the specified size limit
    async with httpx.AsyncClient() as client:
        for size_key in SIZE_PROGRESSION[: max_index + 1]:
            current_step += 1
            progress_message = f"Uploading {size_key} data..."
            await safe_report_progress(context, current_step, total_steps, progress_message)
            if size_key in ["100MB", "200MB", "500MB", "1GB"]:
                test_duration = sustain_time + ADDITIONAL_TEST_DURATION
            else:
                test_duration = sustain_time

            data_size = UPLOAD_SIZES[size_key]
            data = b"x" * data_size
            start = time.time()

            try:
                response = await client.post(url_upload, data=data, timeout=30.0)
                end = time.time()
                elapsed_time = end - start

                # Extract server information from headers
                server_info = extract_server_info(dict(response.headers))

                # Calculate upload speed in Mbps
                speed_mbps = (data_size * 8) / (1024 * 1024) / elapsed_time
                result = {
                    "size": size_key,
                    "upload_speed": round(speed_mbps, 2),
                    "elapsed_time": round(elapsed_time, 2),
                    "data_size": data_size,
                    "url": url_upload,
                    "server_info": server_info,
                }

                results.append(result)

                # Set the final result to the last result
                final_result = result

                # If this test took longer than our threshold, we're done
                if elapsed_time > test_duration:
                    break

            except (
                httpx.RequestError,
                httpx.HTTPStatusError,
                httpx.TimeoutException,
            ) as e:
                results.append(
                    {
                        "size": size_key,
                        "error": True,
                        "message": f"HTTP Error: {e!s}",
                        "url": url_upload,
                    },
                )
                # If we encounter an error, use the last successful result or continue
                if final_result:
                    break

    # Return the final result or an error if all tests failed
    if final_result:
        return {
            "upload_speed": final_result["upload_speed"],
            "unit": "Mbps",
            "elapsed_time": final_result["elapsed_time"],
            "data_size": final_result["data_size"],
            "size_used": final_result["size"],
            "server_info": final_result["server_info"],
            "all_tests": results,
        }
    return {
        "error": True,
        "message": "All upload tests failed",
        "details": results,
    }


@mcp.tool(icons=[ICON_LATENCY])
async def measure_latency(
    url: str = DEFAULT_LATENCY_URL,
    samples: int = 10,
) -> dict:
    """Measure the latency using multiple samples and report the minimum.

    Takes a number of samples and reports the lowest
    value for the most accurate representation of network latency.

    Args:
        url (str): The URL to measure latency to
        samples (int): Number of samples to take (default: 10)

    Returns:
        Dictionary with latency result (minimum of all samples)
    """
    latency_values = []
    server_info = None

    async with httpx.AsyncClient() as client:
        for sample_index in range(samples):
            start = time.time()
            response = await client.get(url)
            end = time.time()
            latency_values.append((end - start) * 1000)

            if sample_index == 0:
                server_info = extract_server_info(dict(response.headers))

    return {
        "latency": round(min(latency_values), 2),
        "unit": "ms",
        "url": url,
        "samples": samples,
        "min_latency": round(min(latency_values), 2),
        "max_latency": round(max(latency_values), 2),
        "avg_latency": round(sum(latency_values) / len(latency_values), 2),
        "server_info": server_info,
    }


@mcp.tool(icons=[ICON_JITTER])
async def measure_jitter(
    url: str = DEFAULT_LATENCY_URL,
    samples: int = 5,
    context: Context[ServerSession, None] = None,
) -> dict:
    """Jitter is the variation in latency, so we need multiple measurements."""
    latency_values = []
    server_info = None

    await safe_log_info(context, f"Starting jitter measurement with {samples} samples...")

    async with httpx.AsyncClient() as client:
        for sample_index in range(samples):
            msg = f"Sample {sample_index + 1}/{samples}"
            await safe_report_progress(context, sample_index + 1, samples, msg)
            start = time.time()
            response = await client.get(url)
            end = time.time()
            latency_values.append((end - start) * 1000)  # Convert to milliseconds

            # Extract server info from the first response
            if sample_index == 0:
                server_info = extract_server_info(dict(response.headers))

    # Calculate average latency
    avg_latency = sum(latency_values) / len(latency_values)

    # Calculate jitter (average deviation from the mean)
    jitter = sum(abs(latency - avg_latency) for latency in latency_values) / len(
        latency_values,
    )

    return {
        "jitter": round(jitter, 2),
        "unit": "ms",
        "average_latency": round(avg_latency, 2),
        "samples": samples,
        "url": url,
        "server_info": server_info,
    }


@mcp.tool(icons=[ICON_SERVER])
async def get_server_info(
    url_download: str = DEFAULT_DOWNLOAD_URLS["128KB"],
    url_upload: str = DEFAULT_UPLOAD_URL,
    url_latency: str = DEFAULT_LATENCY_URL,
) -> dict:
    """
    Get server information for any URL without performing speed tests.

    Args:
        url_download: URL to download data from
        url_upload: URL to upload data to
        url_latency: URL to measure latency to

    Returns:
        Dictionary with servers information including POP location, CDN info, etc.
    """
    async with httpx.AsyncClient() as client:
        try:
            response_url_download = await client.head(url_download, timeout=12.0)
            server_info_url_download = extract_server_info(
                dict(response_url_download.headers),
            )

            response_url_upload = await client.head(url_upload, timeout=12.0)
            server_info_url_upload = extract_server_info(
                dict(response_url_upload.headers),
            )

            response_url_latency = await client.head(url_latency, timeout=12.0)
            server_info_url_latency = extract_server_info(
                dict(response_url_latency.headers),
            )

            return {
                "url_download": url_download,
                "status_code_url_download": response_url_download.status_code,
                "server_info_url_download": server_info_url_download,
                "headers_url_download": dict(response_url_download.headers),
                "url_upload": url_upload,
                "status_code_url_upload": response_url_upload.status_code,
                "server_info_url_upload": server_info_url_upload,
                "headers_url_upload": dict(response_url_upload.headers),
                "url_latency": url_latency,
                "status_code_url_latency": response_url_latency.status_code,
                "server_info_url_latency": server_info_url_latency,
                "headers_url_latency": dict(response_url_latency.headers),
            }
        except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
            return {
                "error": True,
                "message": f"Failed to get servers info: {e!s}",
                "url_download": url_download,
                "url_upload": url_upload,
                "url_latency": url_latency,
            }


@mcp.tool(icons=[ICON_COMPLETE])
async def run_complete_test(
    max_size: str = "100MB",
    url_upload: str = DEFAULT_UPLOAD_URL,
    url_latency: str = DEFAULT_LATENCY_URL,
    sustain_time: int = 8,
    context: Context[ServerSession, None] = None,
) -> dict:
    """
    Run a complete speed test returning all metrics in a single call.

    This test uses the smart incremental approach inspired by SpeedOf.Me:
    - First measures download speed with gradually increasing file sizes
    - Then measures upload speed with gradually increasing data sizes
    - Measures latency and jitter
    - Returns comprehensive results with real-time data

    Args:
        max_size: Maximum file size to test (default: 100MB)
        url_upload: URL for upload testing
        url_latency: URL for latency testing
        sustain_time: Duration in seconds for each test (1-8, default: 8)

    Returns:
        Complete test results including download, upload, latency and jitter metrics
    """
    await safe_log_info(context, "Starting complete speed test...")
    await safe_report_progress(context, 1, 4, "Testing download speed...")

    download_result = await measure_download_speed(max_size, sustain_time, context)

    await safe_report_progress(context, 2, 4, "Testing upload speed...")

    upload_result = await measure_upload_speed(url_upload, max_size, sustain_time, context)

    await safe_report_progress(context, 3, 4, "Measuring latency...")

    latency_result = await measure_latency(url_latency)

    await safe_report_progress(context, 4, 4, "Measuring jitter...")

    jitter_result = await measure_jitter(url_latency, 5, context)

    await safe_log_info(context, "Complete speed test finished!")

    return {
        "timestamp": time.time(),
        "download": download_result,
        "upload": upload_result,
        "latency": latency_result,
        "jitter": jitter_result,
        "test_methodology": "Incremental file size approach with 8-second threshold",
    }


# Entry point to run the server
if __name__ == "__main__":
    mcp.run()
