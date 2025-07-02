"""
Server for the internet speed test

This module implements an internet speed test service inspired by SpeedOf.Me methodology.

## How It Works

This speed test uses an incremental testing approach:

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

import time
import re
from typing import Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Create a singleton instance of FastMCP
mcp = FastMCP("internet_speed_test", dependencies=["httpx"])

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
        "priority": 1  # Highest priority due to global distribution
    },
    {
        "url": "https://httpbin.org/", 
        "name": "HTTPBin (AWS)",
        "provider": "AWS",
        "priority": 2
    }
]

# Primary endpoints for backward compatibility
DEFAULT_UPLOAD_URL = UPLOAD_ENDPOINTS[0]["url"] + "post" # Use Cloudflare by default
DEFAULT_LATENCY_URL = UPLOAD_ENDPOINTS[0]["url"] + "get" # Use Cloudflare by default

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
BASE_TEST_DURATION = 8.0
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
    "SJU": "San Juan, Puerto Rico"
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


def extract_server_info(headers: Dict[str, str]) -> Dict[str, Optional[str]]:
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
        "x_cache": None
    }

    # Extract x-served-by header (Fastly specific)
    served_by = headers.get("x-served-by", "")
    if served_by:
        server_info["served_by"] = served_by

        # Extract POP code from served-by header
        # Format examples: cache-mex4329-MEX, cache-qro4141-QRO, cache-dfw-kdfw8210052-DFW
        pop_match = re.search(r'-([A-Z]{3})$', served_by)
        if pop_match:
            server_info["pop_code"] = pop_match.group(1)
            server_info["pop_location"] = FASTLY_POP_LOCATIONS.get(
                pop_match.group(1), f"Unknown location ({pop_match.group(1)})"
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
        cf_match = re.search(r'-([A-Z]{3})$', cf_ray)
        if cf_match:
            server_info["pop_code"] = cf_match.group(1)
            server_info["pop_location"] = CLOUDFLARE_POP_LOCATIONS.get(
                cf_match.group(1), f"Unknown location ({cf_match.group(1)})"
            )
            server_info["cdn_provider"] = "Cloudflare"

    # Check for other CDN indicators
    if not server_info["cdn_provider"]:
        if "fastly" in headers.get("server", "").lower():
            server_info["cdn_provider"] = "Fastly"
        elif "cloudflare" in headers.get("server", "").lower():
            server_info["cdn_provider"] = "Cloudflare"
        elif "amazon" in headers.get("server", "").lower() or "aws" in headers.get("server", "").lower():
            server_info["cdn_provider"] = "Amazon CloudFront"

    return server_info


# Register tools
@mcp.tool()
async def measure_download_speed(size_limit: str = "100MB") -> dict:
    """
    Measure download speed using incremental file sizes.

    Args:
        size_limit: Maximum file size to test (default: 100MB)

    Returns:
        Dictionary with download speed results
    """
    results = []
    final_result = None

    # Find the index of the size limit in our progression
    max_index = (
        SIZE_PROGRESSION.index(size_limit)
        if size_limit in SIZE_PROGRESSION
        else len(SIZE_PROGRESSION) - 1
    )

    # Test each file size in order, up to the specified limit
    async with httpx.AsyncClient() as client:
        for size_key in SIZE_PROGRESSION[: max_index + 1]:
            if size_key in DEFAULT_DOWNLOAD_URLS:
                if size_key in ["100MB", "200MB", "500MB", "1GB"]:
                    test_duration = BASE_TEST_DURATION + ADDITIONAL_TEST_DURATION
                else:
                    test_duration = BASE_TEST_DURATION

                url = DEFAULT_DOWNLOAD_URLS[size_key]
                start = time.time()
                total_size = 0

                async with client.stream(
                    "GET", url,
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
                            speed_mbps = (
                                (total_size * 8) / (1024 * 1024)
                            ) / elapsed_time
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

            else:
                # Skip sizes that don't have a corresponding URL
                continue

                # Store individual test result
                results.append({
                    "size": size_key,
                    "download_speed": round(speed_mbps, 2),
                    "elapsed_time": round(elapsed_time, 2),
                    "data_size": total_size,
                    "url": url,
                    "server_info": server_info,
                })

                # If this test took longer than our threshold, we're done
                if elapsed_time > test_duration:
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
    else:
        return {"error": True, "message": "All download tests failed", "details": results}


@mcp.tool()
async def measure_upload_speed(
    url_upload: str = DEFAULT_UPLOAD_URL, size_limit: str = "100MB"
) -> dict:
    """
    Measure upload speed using incremental file sizes.

    Args:
        url_upload: URL to upload data to
        size_limit: Maximum file size to test (default: 100MB)

    Returns:
        Dictionary with upload speed results
    """
    results = []
    final_result = None

    # Find the index of the size limit in our progression
    max_index = (
        SIZE_PROGRESSION.index(size_limit)
        if size_limit in SIZE_PROGRESSION
        else len(SIZE_PROGRESSION) - 1
    )

    # Only test up to the specified size limit
    async with httpx.AsyncClient() as client:
        for size_key in SIZE_PROGRESSION[: max_index + 1]:
            if size_key in ["100MB", "200MB", "500MB", "1GB"]:
                test_duration = BASE_TEST_DURATION + ADDITIONAL_TEST_DURATION
            else:
                test_duration = BASE_TEST_DURATION

            data_size = UPLOAD_SIZES[size_key]
            data = b"x" * data_size
            start = time.time()

            try:
                response = await client.post(
                    url_upload, data=data, timeout=30.0
                )
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

            except Exception as e:
                results.append(
                    {
                        "size": size_key,
                        "error": True,
                        "message": f"Exception: {str(e)}",
                        "url": url_upload,
                    }
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
    else:
        return {"error": True, "message": "All upload tests failed", "details": results}


@mcp.tool()
async def measure_latency(url: str = DEFAULT_LATENCY_URL) -> dict:
    """Measure the latency"""
    start = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    end = time.time()
    elapsed_time = end - start

    # Extract server information from headers
    server_info = extract_server_info(dict(response.headers))

    return {
        "latency": round(elapsed_time * 1000, 2),  # Convert to milliseconds
        "unit": "ms",
        "url": url,
        "server_info": server_info,
    }


@mcp.tool()
async def get_server_info(url: str) -> dict:
    """
    Get server information for any URL without performing speed tests.

    Args:
        url: URL to analyze

    Returns:
        Dictionary with server information including POP location, CDN info, etc.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.head(url, timeout=10.0)
            server_info = extract_server_info(dict(response.headers))

            return {
                "url": url,
                "status_code": response.status_code,
                "server_info": server_info,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to get server info: {str(e)}",
                "url": url
            }


@mcp.tool()
async def measure_jitter(url: str = DEFAULT_LATENCY_URL, samples: int = 5) -> dict:
    """Jitter is the variation in latency, so we need multiple measurements."""
    latency_values = []
    server_info = None

    async with httpx.AsyncClient() as client:
        for i in range(samples):
            start = time.time()
            response = await client.get(url)
            end = time.time()
            latency_values.append((end - start) * 1000)  # Convert to milliseconds

            # Extract server info from the first response
            if i == 0:
                server_info = extract_server_info(dict(response.headers))

    # Calculate average latency
    avg_latency = sum(latency_values) / len(latency_values)

    # Calculate jitter (average deviation from the mean)
    jitter = sum(abs(latency - avg_latency) for latency in latency_values) / len(
        latency_values
    )

    return {
        "jitter": round(jitter, 2),
        "unit": "ms",
        "average_latency": round(avg_latency, 2),
        "samples": samples,
        "url": url,
        "server_info": server_info,
    }


@mcp.tool()
async def run_complete_test(
    max_size: str = "100MB",
    url_upload: str = DEFAULT_UPLOAD_URL,
    url_latency: str = DEFAULT_LATENCY_URL,
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

    Returns:
        Complete test results including download, upload, latency and jitter metrics
    """
    download_result = await measure_download_speed(max_size)
    upload_result = await measure_upload_speed(url_upload, max_size)
    latency_result = await measure_latency(url_latency)
    jitter_result = await measure_jitter(url_latency)

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
