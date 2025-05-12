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
import httpx

from mcp.server.fastmcp import FastMCP

# Create a singleton instance of FastMCP
mcp = FastMCP("internet_speed_test", dependencies=["httpx"])

# Default URLs for testing
# Using different file sizes from ThinkBroadband for download testing
DEFAULT_DOWNLOAD_URLS = {
    "128KB": "http://ipv4.download.thinkbroadband.com/128KB.zip",
    "256KB": "http://ipv4.download.thinkbroadband.com/256KB.zip",
    "512KB": "http://ipv4.download.thinkbroadband.com/512KB.zip",
    "1MB": "http://ipv4.download.thinkbroadband.com/1MB.zip",
    "2MB": "http://ipv4.download.thinkbroadband.com/2MB.zip",
    "5MB": "http://ipv4.download.thinkbroadband.com/5MB.zip",
    "10MB": "http://ipv4.download.thinkbroadband.com/10MB.zip",
    "20MB": "http://ipv4.download.thinkbroadband.com/20MB.zip",
    "40MB": "http://ipv4.download.thinkbroadband.com/40MB.zip",
    "50MB": "http://ipv4.download.thinkbroadband.com/50MB.zip",
    "100MB": "http://ipv4.download.thinkbroadband.com/100MB.zip",
    "200MB": "http://ipv4.download.thinkbroadband.com/200MB.zip",
    "512MB": "http://ipv4.download.thinkbroadband.com/512MB.zip",
}

DEFAULT_UPLOAD_URL = "https://httpbin.org/post"
DEFAULT_LATENCY_URL = "https://httpbin.org/get"

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
    "200MB": 200 * 1024 * 1024,
    "512MB": 512 * 1024 * 1024,
}

# Maximum time threshold for a test (in seconds)
MAX_TEST_DURATION = 8.0

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
    "200MB",
    "512MB",
]


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
            url = DEFAULT_DOWNLOAD_URLS[size_key]
            # tracker = BandwidthTracker()

            start = time.time()
            total_size = 0

            async with client.stream("GET", url) as response:
                async for chunk in response.aiter_bytes(chunk_size=1024):
                    if chunk:
                        chunk_size = len(chunk)
                        total_size += chunk_size
                        # tracker.update(chunk_size)

            end = time.time()
            elapsed_time = end - start

            speed_mbps = (total_size * 8) / (
                elapsed_time * 1_000_000
            )  # bits to megabits
            result = {
                "size": size_key,
                "download_speed": round(speed_mbps, 2),
                "unit": "Mbps",
                "elapsed_time": round(elapsed_time, 2),
                "total_size": total_size,
                "url": url,
            }
            results.append(result)

            # Set the final result to the last result
            final_result = result

            # If this test took longer than our threshold, we're done
            if elapsed_time > MAX_TEST_DURATION:
                break

    return {
        "download_speed": final_result["download_speed"],
        "unit": "Mbps",
        "elapsed_time": final_result["elapsed_time"],
        "total_size": final_result["total_size"],
        "size_used": final_result["size"],
        "all_tests": results,
    }


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
            # Skip larger sizes to avoid excessive resource usage in testing
            if size_key in ["256MB", "512MB"]:
                continue

            data_size = UPLOAD_SIZES[size_key]
            data = b"x" * data_size

            # tracker = BandwidthTracker()

            start = time.time()

            try:
                response = await client.post(
                    url_upload,
                    files={"file": ("test.dat", data)},
                    timeout=60.0,  # Timeout for very large files
                )

                end = time.time()
                elapsed_time = end - start

                if response.status_code == 200:
                    speed_mbps = (data_size * 8) / (
                        elapsed_time * 1_000_000
                    )  # bits to megabits
                    result = {
                        "size": size_key,
                        "upload_speed": round(speed_mbps, 2),
                        "unit": "Mbps",
                        "elapsed_time": round(elapsed_time, 2),
                        "data_size": data_size,
                        "url": url_upload,
                    }

                    results.append(result)

                    # Set the final result to the last result
                    final_result = result

                    # If this test took longer than our threshold, we're done
                    if elapsed_time > MAX_TEST_DURATION:
                        break
                else:
                    results.append(
                        {
                            "size": size_key,
                            "error": True,
                            "message": f"HTTP Error: {response.status_code}",
                            "url": url_upload,
                        }
                    )
                    # If we encounter an error, use the last successful result or continue
                    if final_result:
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
    return {
        "latency": round(elapsed_time * 1000, 2),  # Convert to milliseconds
        "unit": "ms",
        "url": url,
    }


@mcp.tool()
async def measure_jitter(url: str = DEFAULT_LATENCY_URL, samples: int = 5) -> dict:
    """Jitter is the variation in latency, so we need multiple measurements."""
    latency_values = []

    async with httpx.AsyncClient() as client:
        for _ in range(samples):
            start = time.time()
            response = await client.get(url)
            end = time.time()
            latency_values.append((end - start) * 1000)  # Convert to milliseconds

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
