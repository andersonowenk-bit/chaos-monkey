"""Keeps the victims alive. This is the part the monkey is really testing."""
import argparse
import subprocess
import sys
import time
from datetime import datetime


def log(msg):
    print(f"{datetime.now():%H:%M:%S} [supervisor] {msg}", flush=True)


def spawn(name, port):
    proc = subprocess.Popen([sys.executable, "victim.py", name, str(port)])
    log(f"started {name} pid={proc.pid} port={port}")
    return proc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=3, help="how many services to run")
    parser.add_argument("--base-port", type=int, default=8001, help="first port; the rest count up")
    args = parser.parse_args()

    procs = {}
    for i in range(args.count):
        name, port = f"svc-{i + 1}", args.base_port + i
        procs[name] = (spawn(name, port), port)

    restarts = 0
    try:
        while True:
            for name, (proc, port) in list(procs.items()):
                code = proc.poll()
                if code is not None:
                    restarts += 1
                    log(f"{name} died (exit {code}), restarting (total restarts: {restarts})")
                    procs[name] = (spawn(name, port), port)
            time.sleep(0.5)
    except KeyboardInterrupt:
        log("shutting down")
        for proc, _ in procs.values():
            proc.terminate()


if __name__ == "__main__":
    main()
