import subprocess

result = subprocess.run(
    ["powershell", "-Command", "powercfg /setacvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOIDLE 0"],
    capture_output=True, text=True
)
