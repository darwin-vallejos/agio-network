import os
import urllib.request
import zipfile
import shutil

# CONFIG - Using a stable 2026-ready release
VERSION = "v2.0.3"
URL = f"https://github.com/solana-labs/solana/releases/download/{VERSION}/solana-release-x86_64-pc-windows-msvc.tar.bz2"
INSTALL_DIR = r"C:\solana-tools"

def install():
    print(f"--- STARTING DIRECT TOOL INJECTION ({VERSION}) ---")
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
    
    print("1. Downloading binaries (This may take a minute)...")
    # Note: Using a simpler zip if available for Windows logic
    zip_url = f"https://github.com/solana-labs/solana/releases/download/{VERSION}/solana-mainnet-beta-x86_64-pc-windows-msvc.zip"
    tmp_zip = os.path.join(INSTALL_DIR, "solana.zip")
    
    try:
        urllib.request.urlretrieve(zip_url, tmp_zip)
        print("2. Extracting tools...")
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
        
        bin_path = os.path.join(INSTALL_DIR, "bin")
        print(f"\nSUCCESS: Solana tools injected to {bin_path}")
        print("-" * 40)
        print(f"FINAL STEP: Run this command to add it to your PATH:")
        print(f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{bin_path}", "User")')
    except Exception as e:
        print(f"INJECTION FAILED: {e}")

if __name__ == "__main__":
    install()
