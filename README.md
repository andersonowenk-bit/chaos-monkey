# Chaos Monkey, local edition

A small chaos engineering tool that randomly kills processes on your own machine so you can watch a supervisor recover them. No cloud, no Docker, just Python's standard library.

Inspired by [The Netflix Simian Army](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116). Netflix built Chaos Monkey to randomly terminate production instances, forcing engineers to design services that survive failure. This repo is the same idea at the smallest possible scale.

## How it works

Three scripts:

- `victim.py` is a tiny HTTP service that reports its name, PID, and uptime at `GET /`.
- `supervisor.py` launches several victims and restarts any that die. This is the resilience layer under test.
- `monkey.py` wakes up every few seconds and, with some probability, kills one victim with `SIGKILL`.

If the supervisor is doing its job, the services keep answering even while the monkey is loose.

## Run it

Open two terminal tabs in this folder.

Tab 1, start the services:

    python3 supervisor.py --count 3

Tab 2, release the monkey:

    python3 monkey.py --interval 3 --probability 0.7

Optional tab 3, watch a service stay alive while its PID keeps changing:

    while true; do curl -s localhost:8001; echo; sleep 1; done

Stop everything with Ctrl-C in each tab.

## What you'll see

    18:04:12 [monkey] killed pid=51230 with SIGKILL (total kills: 1)
    18:04:12 [supervisor] svc-2 died (exit -9), restarting (total restarts: 1)
    18:04:12 [supervisor] started svc-2 pid=51241 port=8002

## Knobs

| Flag | Default | Meaning |
|---|---|---|
| `--interval` | 5 | seconds between attacks |
| `--probability` | 0.5 | chance of a kill each interval |
| `--signal` | KILL | `TERM` asks nicely, `KILL` does not |
| `--match` | victim.py | script name to hunt |
| `--dry-run` | off | report what would die, kill nothing |

## A lesson learned while building it

The first version found victims with `pgrep -f victim.py`. That matches any process whose command line contains the text, so it killed the shell that launched it. The current version only matches a `python` process whose first argument is the script name. Chaos tools need a very precise blast radius.

## Tests

    python3 -m unittest -v

## Ideas for next versions

- A latency monkey that slows responses instead of killing processes
- Kill the supervisor itself and see what breaks
- Point it at Docker containers instead of local processes
