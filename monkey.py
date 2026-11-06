"""Chaos Monkey, local edition.

Randomly kills victim processes so you can watch the supervisor recover.
Inspired by Netflix's Simian Army: https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116
"""
import argparse
import os
import random
import signal
import subprocess
import time
from datetime import datetime


def log(msg):
    print(f"{datetime.now():%H:%M:%S} [monkey] {msg}", flush=True)


def find_victims(script):
    """Return PIDs of python processes running the given script.

    Deliberately strict: it only matches "python ... victim.py", never any process whose
    command line merely mentions the name. The first version used `pgrep -f` and killed
    the shell that launched it, because that shell's command line contained "victim.py".
    """
    result = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True)
    me = os.getpid()
    victims = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        pid, program, first_arg = int(parts[0]), os.path.basename(parts[1]), parts[2]
        if pid != me and program.startswith("python") and first_arg.endswith(script):
            victims.append(pid)
    return victims


def choose_victim(pids, rng=random):
    """Pick one PID at random, or None if there is nothing to kill."""
    return rng.choice(pids) if pids else None


def main():
    parser = argparse.ArgumentParser(description="Randomly kill local processes to test resilience.")
    parser.add_argument("--interval", type=float, default=5, help="seconds between attacks (default 5)")
    parser.add_argument("--probability", type=float, default=0.5, help="chance of a kill each interval (default 0.5)")
    parser.add_argument("--match", default="victim.py", help="script name to hunt (default victim.py)")
    parser.add_argument("--signal", choices=["TERM", "KILL"], default="KILL", help="TERM asks nicely, KILL does not")
    parser.add_argument("--dry-run", action="store_true", help="report what would die, kill nothing")
    args = parser.parse_args()

    sig = signal.SIGKILL if args.signal == "KILL" else signal.SIGTERM
    log(f"loose: every {args.interval}s, p={args.probability}, match='{args.match}', "
        f"signal={args.signal}, dry_run={args.dry_run}")

    kills = 0
    while True:
        time.sleep(args.interval)
        pids = find_victims(args.match)
        if not pids:
            log("no victims found, is the supervisor running?")
            continue
        if random.random() > args.probability:
            log(f"spared all {len(pids)} processes this round")
            continue
        pid = choose_victim(pids)
        if args.dry_run:
            log(f"would kill pid={pid}")
            continue
        try:
            os.kill(pid, sig)
            kills += 1
            log(f"killed pid={pid} with SIG{args.signal} (total kills: {kills})")
        except ProcessLookupError:
            log(f"pid={pid} vanished before I got there")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("back in the cage")
