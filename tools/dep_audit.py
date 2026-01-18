#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import glob

def audit_dependencies(requirements_path="api/requirements.txt", max_size_mb=1000):
    print(f"Auditing dependencies from {requirements_path}...")
    temp_dir = "temp_wheels"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        # Download wheels
        print("Downloading wheels (this may take a moment)...")
        # Use --no-deps if we only want to check top-level, but usually we care about transitive
        # The prompt says "download wheels". Defaults to including deps.
        subprocess.check_call(
            [sys.executable, "-m", "pip", "download", "-d", temp_dir, "-r", requirements_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Calculate total size
        total_size = 0
        forbidden_packages = []
        nvidia_cuda_patterns = ["nvidia-", "cuda-", "torch", "triton"]
        
        # Check for specific GPU packages if we want to be strict, 
        # but size is the main metric. Any heavy GPU dep will blow the budget.
        
        wheels = glob.glob(os.path.join(temp_dir, "*"))
        print(f"Downloaded {len(wheels)} files.")

        for wheel in wheels:
            size = os.path.getsize(wheel)
            total_size += size
            filename = os.path.basename(wheel).lower()
            
            # Check for forbidden patterns
            if any(p in filename for p in nvidia_cuda_patterns):
                # Special case: torch is allowed if it's CPU only (smallish), 
                # but standard torch is huge. We flag it if we see it.
                forbidden_packages.append((filename, size))

        total_size_mb = total_size / (1024 * 1024)
        print(f"Total dependency size: {total_size_mb:.2f} MB")

        failed = False
        
        if total_size_mb > max_size_mb:
            print(f"❌ SIZE VIOLATION: Total size {total_size_mb:.2f} MB exceeds limit {max_size_mb} MB")
            failed = True
        
        if forbidden_packages:
            print("⚠️  POTENTIAL GPU DEPENDENCIES FOUND:")
            for name, size in forbidden_packages:
                print(f"   - {name} ({size / (1024*1024):.2f} MB)")
            # We strictly fail on nvidia/cuda packages as per prompt
            # "fail CI ... if CUDA/nvidia packages appear"
            if any("nvidia" in f[0] or "cuda" in f[0] for f in forbidden_packages):
                 print("❌ FORBIDDEN PACKAGES DETECTED (nvidia/cuda)")
                 failed = True

        if failed:
            sys.exit(1)
        
        print("✅ Dependency audit passed.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download dependencies: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    req_path = sys.argv[1] if len(sys.argv) > 1 else "api/requirements.txt"
    audit_dependencies(req_path)
