"""
Server for the internet speed test
"""

import time
import requests

from mcp.server.fastmcp import FastMCP

# Create a singleton instance of FastMCP
mcp = FastMCP("internet_speed_test", dependencies=["requests"])

# Default URLs for testing
DEFAULT_DOWNLOAD_URL = "http://ipv4.download.thinkbroadband.com/10MB.zip"
DEFAULT_UPLOAD_URL = "https://httpbin.org/post"
DEFAULT_LATENCY_URL = "https://httpbin.org/get"


# Register tools
@mcp.tool()
def measure_download_speed(url_download: str = DEFAULT_DOWNLOAD_URL) -> dict:
    """Measure the download speed"""
    start = time.time()

    response = requests.get(url_download, stream=True)
    total_size = 0

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            total_size += len(chunk)

    end = time.time()
    elapsed_time = end - start

    speed_mbps = (total_size * 8) / (elapsed_time * 1_000_000)  # bits to megabits
    return {
        "download_speed": round(speed_mbps, 2),
        "unit": "Mbps",
        "elapsed_time": round(elapsed_time, 2),
        "total_size": total_size,
        "url": url_download,
    }


@mcp.tool()
def measure_upload_speed(url_upload: str = DEFAULT_UPLOAD_URL) -> dict:
    """Measure the upload speed"""
    data = b"x" * 10_000_000  # 10 MB of data

    start = time.time()
    response = requests.post(url_upload, files={"file": ("test.dat", data)})
    end = time.time()

    if response.status_code == 200:
        elapsed_time = end - start
        speed_mbps = (len(data) * 8) / (elapsed_time * 1_000_000)  # bits to megabits
        return {
            "upload_speed": round(speed_mbps, 2),
            "unit": "Mbps",
            "elapsed_time": round(elapsed_time, 2),
            "data_size": len(data),
            "url": url_upload,
        }
    else:
        return {
            "error": True,
            "message": f"HTTP Error: {response.status_code}",
            "url": url_upload,
        }


@mcp.tool()
def measure_latency(url: str = DEFAULT_LATENCY_URL) -> dict:
    """Measure the latency"""
    start = time.time()
    response = requests.get(url)
    end = time.time()
    elapsed_time = end - start
    return {
        "latency": round(elapsed_time * 1000, 2),  # Convert to milliseconds
        "unit": "ms",
        "url": url,
    }


@mcp.tool()
def measure_jitter(url: str = DEFAULT_LATENCY_URL, samples: int = 5) -> dict:
    """Jitter is the variation in latency, so we need multiple measurements."""
    latency_values = []

    for _ in range(samples):
        start = time.time()
        response = requests.get(url)
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
def run_complete_test(
    url_download: str = DEFAULT_DOWNLOAD_URL,
    url_upload: str = DEFAULT_UPLOAD_URL,
    url_latency: str = DEFAULT_LATENCY_URL,
) -> dict:
    """Run a complete speed test returning all metrics in a single call"""
    download_result = measure_download_speed(url_download)
    upload_result = measure_upload_speed(url_upload)
    latency_result = measure_latency(url_latency)
    jitter_result = measure_jitter(url_latency)

    return {
        "timestamp": time.time(),
        "download": download_result,
        "upload": upload_result,
        "latency": latency_result,
        "jitter": jitter_result,
    }


# Entry point to run the server
if __name__ == "__main__":
    mcp.run()
