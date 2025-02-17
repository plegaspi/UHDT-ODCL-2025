import subprocess

scripts = ["simulate_watch_directory.py", "ODCL2.py", "show_detections.py"]

processes = []

# Start Process 1 (simulate_watch_directory.py) in parallel
processes.append(subprocess.Popen(["python", scripts[0], "synthetic_images/source2", "synthetic_images/dest"]))

# Start Process 2 (ODCL2.py) and wait for it to finish
process2 = subprocess.Popen(["python", scripts[1]])
process2.wait()  # This ensures Process 3 only starts after Process 2 finishes

# Start Process 3 (show_detections.py) only after Process 2 has ended
process3 = subprocess.Popen(["python", scripts[2], "odcl_demo/unique_targets"])

# Wait for all processes to finish
for process in processes:
    process.wait()

process3.wait()  # Ensure Process 3 completes before exiting