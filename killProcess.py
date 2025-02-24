#!/usr/bin/env python3
import subprocess
import sys

def get_gphot_processes():
    """
    Retrieve a list of PIDs for processes whose command line contains 'gphot'.
    Excludes the grep process itself.
    """
    try:
        # Get the output of 'ps aux'
        output = subprocess.check_output(["ps", "aux"], text=True)
    except subprocess.CalledProcessError as e:
        print("Error running ps aux:", e, file=sys.stderr)
        sys.exit(1)
    
    pids = []
    for line in output.splitlines():
        # Look for 'gphot' in the line but ignore lines that include 'grep'
        if "gphot" in line and "grep" not in line:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                pids.append(pid)
    return pids

def kill_process(pid):
    """
    Kill a process given its PID using the kill command.
    """
    try:
        subprocess.run(["kill", "-9", pid], check=True)
        print(f"Killed process with PID {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Error killing process {pid}: {e}", file=sys.stderr)

def main():
    pids = get_gphot_processes()
    if not pids:
        print("No matching 'gphot' processes found.")
        return

    # Kill the first 2 processes found (or fewer if less than 2 exist)
    for pid in pids[:2]:
        kill_process(pid)

if __name__ == "__main__":
    main()

