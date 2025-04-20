import httpx
from config import JOBNIMBUS_API_KEY

HEADERS = {
    "Authorization": f"bearer {JOBNIMBUS_API_KEY}",
    "Content-Type": "application/json"
}

def search_job_by_name(name, exact=False):
    """Search jobs by name. Try exact first if specified, else fuzzy/substring."""
    size = 1000
    offset = 0
    all_jobs = []

    name = name.strip().lower()
    print(f"🔎 Searching all jobs for: '{name}' (exact={exact})")

    while True:
        url = f"https://app.jobnimbus.com/api1/jobs?size=1000&from={offset}"
        response = httpx.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Job fetch failed: {response.status_code} {response.text}")
            break

        results = response.json().get("results", [])
        all_jobs.extend(results)

        if len(results) < 1000:
            break
        offset += 1000

    if exact:
        matches = [job for job in all_jobs if job.get("name", "").strip().lower() == name]
        if matches:
            print(f"✅ Exact match: {matches[0]['name']}")
            return matches
        else:
            print("🔍 No exact match found.")
            return []

    # fallback: fuzzy + substring
    from difflib import get_close_matches
    job_name_map = {job.get("name", "").strip().lower(): job for job in all_jobs if job.get("name")}
    job_names = list(job_name_map.keys())

    close = get_close_matches(name, job_names, n=5, cutoff=0.6)
    if not close:
        close = [jn for jn in job_names if name in jn]

    matches = [job_name_map[jn] for jn in close]

    if len(matches) > 10:
        print(f"⚠️ Too many matches ({len(matches)}). Trimming to 10.")
        matches = matches[:10]

    print(f"🔍 Found {len(matches)} fuzzy matches")
    return matches

def upload_file_to_job(job_id, file_url, file_name):
    """Upload a file to JobNimbus using a public URL (Telegram file)."""
    url = "https://app.jobnimbus.com/api1/files/fromUrl"
    payload = {
        "related": [job_id],
        "type": "Photo",
        "description": f"Uploaded by Photo Bot: {file_name}",
        "url": file_url
    }

    headers = {
        "Authorization": f"bearer {JOBNIMBUS_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🌐 Uploading {file_name} to job {job_id} from URL:\n{file_url}")
    response = httpx.post(url, headers=headers, json=payload)

    print("🔁 Status:", response.status_code)
    print("🧾 Response:", response.text)

    if response.status_code == 200:
        print("✅ Upload successful")
        return response.json()
    else:
        print(f"❌ Upload failed: {response.status_code} {response.text}")
        return None

def list_all_job_names():
    """Optional: List all jobs in your system (first 1000 only)."""
    url = "https://app.jobnimbus.com/api1/jobs"
    response = httpx.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Failed to fetch jobs: {response.status_code} {response.text}")
        return

    results = response.json().get("results", [])
    print(f"📝 Found {len(results)} total jobs:")
    for job in results:
        print(f"- {job.get('name')} (jnid: {job.get('jnid')})")
