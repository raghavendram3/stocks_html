import os
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    """Test the static site generation process locally"""
    print("Starting static site generation test...")
    
    # Run the static site generator
    try:
        subprocess.run(["python", "static_site_generator.py"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Static site generation failed.")
        return
    
    # Check if the build directory was created
    build_dir = Path("build")
    if not build_dir.exists() or not build_dir.is_dir():
        print("Error: Build directory was not created.")
        return
    
    # Check if key files exist
    required_files = ["index.html", "stock_analysis.html", "predictive_analytics.html"]
    missing_files = [f for f in required_files if not (build_dir / f).exists()]
    
    if missing_files:
        print(f"Error: The following required files are missing: {', '.join(missing_files)}")
        return
    
    # Start a simple HTTP server to serve the static files
    server_process = subprocess.Popen(
        ["python", "-m", "http.server", "8000"],
        cwd=build_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start
    time.sleep(2)
    
    # Open the browser to view the generated site
    print("Opening browser to view the generated static site...")
    webbrowser.open("http://localhost:8000")
    
    print("\nStatic site is now running at http://localhost:8000")
    print("Press Ctrl+C when you're done viewing the site.")
    
    try:
        # Keep the server running until user interrupts
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        server_process.terminate()
        server_process.wait()
    
    print("Test complete.")

if __name__ == "__main__":
    main()