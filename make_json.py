import subprocess

min_time = -1
min_i = 0

times = subprocess.check_output(['./what.exe']).decode('utf-8').split()
times = map(lambda x: float(x), times)
print(min(times))
