import re


def normalize_job_link(link: str) -> str:
    """
    Normalize job links from known sources like JobVision or Karbord.
    Returns a cleaned link containing only the base + unique ID.
    """
    if not link:
        return None

    if "jobvision.ir" in link:
        match = re.search(r'/jobs/(\d+)', link)
        if match:
            job_id = match.group(1)
            return f"https://jobvision.ir/jobs/{job_id}"
        
    elif "karbord.io" in link:
        match = re.search(r'/jobs/detail/(\d+)', link)
        if match:
            job_id = match.group(1)
            return f"https://karbord.io/jobs/detail/{job_id}"

    # fallback: return original if not matched
    return link
