import os
import shutil
import sys
import urllib.request
import zipfile

ELECTRON_URL = "https://github.com/e3kskoy7wqk/Electron-for-windows-7/releases/download/v37.2.2/dist.zip"

def resolve(*parts: str) -> str:
    return os.path.normpath(os.path.join(*parts))

def rmtree_verbose(path: str) -> None:
    if os.path.exists(path):
        print(f"  Removing : {path}")
        shutil.rmtree(path)
    else:
        print(f"  Not found (skip remove): {path}")

def copytree_verbose(src: str, dst: str) -> None:
    if not os.path.exists(src):
        print(f"  ERROR: source not found: {src}", file=sys.stderr)
        sys.exit(1)
    print(f"  Copying  : {src}")
    print(f"       to  : {dst}")
    shutil.copytree(src, dst)


# ---------------------------------------------------------------------------
# Step 0 – download & extract
# ---------------------------------------------------------------------------

def download_file(url: str, dest: str) -> None:
    print(f"\n[0a] Downloading electron dist")
    print(f"     URL : {url}")
    print(f"     Dest: {dest}")

    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)

    def _progress(block_count: int, block_size: int, total_size: int) -> None:
        if total_size > 0:
            downloaded = min(block_count * block_size, total_size)
            pct = downloaded * 100 // total_size
            mb_done = downloaded // 1024 // 1024
            mb_total = total_size // 1024 // 1024
            print(f"\r     {pct:3d}%  {mb_done} MB / {mb_total} MB", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=_progress)
    print()
    print("     Download complete.")


def extract_zip(zip_path: str, extract_to: str) -> None:
    print(f"\n[0b] Extracting zip")
    print(f"     Zip : {zip_path}")
    print(f"     Into: {extract_to}")

    if os.path.exists(extract_to):
        print(f"     Removing existing dir: {extract_to}")
        shutil.rmtree(extract_to)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    print("     Extraction complete.")


# ---------------------------------------------------------------------------
# Step 1 – node_modules/electron/dist
# ---------------------------------------------------------------------------

def patch_node_modules(dist_src: str, project_dir: str) -> None:
    target = resolve(project_dir, "node_modules", "electron", "dist")
    print(f"\n[1] Patching node_modules electron dist")
    print(f"    Target: {target}")
    rmtree_verbose(target)
    copytree_verbose(dist_src, target)
    print("    Done.")


# ---------------------------------------------------------------------------
# Step 2 – AppData cache
# ---------------------------------------------------------------------------

ELECTRON_ZIP_NAME = "electron-v37.2.2-win32-x64.zip"


def find_file(root: str, filename: str) -> str | None:
    """Walk *root* and return the first path matching *filename*, or None."""
    paths = []
    
    for dirpath, _dirs, files in os.walk(root):
        if filename in files:
            paths.append(resolve(dirpath, filename))
        
    return paths


def patch_appdata_cache(zip_src: str, dist_src: str, cache_dir: str) -> None:
    print(f"\n[2] Patching AppData electron cache")
    print(f"    Cache dir: {cache_dir}")

    if not os.path.exists(cache_dir):
        print(f"    Creating: {cache_dir}")
        os.makedirs(cache_dir, exist_ok=True)

    # Find and overwrite existing zip, or place it at the top of cache_dir
    existing_zips = find_file(cache_dir, ELECTRON_ZIP_NAME)
    
    for zip_path in existing_zips:
        print(f"      {zip_path}")
        print(f"      Overwriting with: {zip_src}")
        shutil.copy2(zip_src, zip_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    zip_path    = resolve(os.getcwd(), "dist.zip")
    dist_src    = resolve(os.getcwd(), "dist")
    project_dir = resolve(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    cache_dir = resolve(local_appdata, "electron", "Cache") if local_appdata else None

    print(f"Zip path          : {zip_path}")
    print(f"Dist source       : {dist_src}")
    print(f"Project dir       : {project_dir}")
    print(f"AppData cache dir : {cache_dir or '(skipped — LOCALAPPDATA not set)'}")

    download_file(ELECTRON_URL, zip_path)
    extract_zip(zip_path, dist_src)
    patch_node_modules(dist_src, project_dir)

    if cache_dir:
        patch_appdata_cache(zip_path, dist_src, cache_dir)
    else:
        print("\n[2] Skipping AppData patch (LOCALAPPDATA not set).")

    print("\nAll patches applied successfully.")


if __name__ == "__main__":
    main()
