from requests import get


def download(url, dst, default="", chunk_size=8192):
    from hyper import mkdir_file
    """Download file from URL to destination path, streaming for large files"""
    try:
        mkdir_file(dst)  # Create parent dirs if needed
        resp = get(url, stream=True, timeout=30)
        resp.raise_for_status()
        
        with open(dst, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        
        return dst  # Return path on success
    except Exception:
        return default  # Safe default on any error
