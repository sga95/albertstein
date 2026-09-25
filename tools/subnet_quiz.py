#!/usr/bin/env python3
"""make quiz: subnetting sprint. 20 esercizi, 10 minuti, nessun LLM.

Ogni domanda dà un indirizzo con prefisso e chiede una cosa a caso tra: indirizzo di rete,
broadcast, numero di host utilizzabili, maschera decimale, prefisso da maschera, primo o ultimo host.
Alla fine stampa punteggio e tempo, da copiare nella nota della quest "Subnetting sprint".

  python3 tools/subnet_quiz.py            20 domande
  python3 tools/subnet_quiz.py -n 5       meno domande, per provare
  python3 tools/subnet_quiz.py --seed 7   stessa sequenza (per sfidare qualcuno)
"""

from __future__ import annotations

import argparse
import ipaddress
import random
import sys
import time

KINDS = ["network", "broadcast", "hosts", "mask", "prefix", "first", "last"]


def make_question(rng: random.Random) -> tuple[str, str]:
    prefix = rng.choice([20, 22, 23, 24, 25, 26, 27, 28, 29, 30])
    base = rng.choice(["10", "172.16", "192.168"])
    if base == "10":
        ip = f"10.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    elif base == "172.16":
        ip = f"172.{rng.randint(16, 31)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    else:
        ip = f"192.168.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    kind = rng.choice(KINDS)
    if kind == "network":
        return f"Network address of {ip}/{prefix}?", str(net.network_address)
    if kind == "broadcast":
        return f"Broadcast address of {ip}/{prefix}?", str(net.broadcast_address)
    if kind == "hosts":
        return f"Usable hosts in {ip}/{prefix}?", str(net.num_addresses - 2)
    if kind == "mask":
        return f"Dotted mask for /{prefix}?", str(net.netmask)
    if kind == "prefix":
        return f"Prefix length for mask {net.netmask}?", f"/{prefix}"
    if kind == "first":
        return f"First usable host in {ip}/{prefix}?", str(net.network_address + 1)
    return f"Last usable host in {ip}/{prefix}?", str(net.broadcast_address - 1)


def normalize(s: str) -> str:
    s = s.strip().lower()
    return s if s.startswith("/") or not s.isdigit() else s


def run(n: int, seed: int | None, limit: int, ask=input, out=print) -> tuple[int, float]:
    rng = random.Random(seed)
    out(f"Subnetting sprint: {n} questions, {limit // 60} minutes. Answer like 192.168.1.0, 255.255.255.0, /26 or 62. Go.")
    score, start = 0, time.monotonic()
    for i in range(1, n + 1):
        q, a = make_question(rng)
        answer = normalize(ask(f"{i:>2}. {q} "))
        expected = normalize(a)
        if answer.startswith("/") is False and expected.startswith("/"):
            expected = expected[1:]
        if answer == expected or answer == "/" + expected:
            score += 1
            out("    ok")
        else:
            out(f"    no: {a}")
        if time.monotonic() - start > limit:
            out("Time is up.")
            break
    elapsed = time.monotonic() - start
    out(f"Score {score}/{n} in {elapsed / 60:.1f} minutes.")
    return score, elapsed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=20, help="numero di domande (default 20)")
    ap.add_argument("--seed", type=int, help="seme del generatore, per rifare la stessa serie")
    ap.add_argument("--minutes", type=int, default=10, help="limite di tempo (default 10)")
    a = ap.parse_args(argv)
    try:
        run(a.n, a.seed, a.minutes * 60)
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
