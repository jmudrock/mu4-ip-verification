#!/usr/bin/env python3
"""
Decide whether kappa(l) <= N using a binary integer program.

After normalizing the first permutation to the identity, the candidate blocks
are all tuples (id, sigma_2, ..., sigma_l). The IP selects at most N blocks
and requires every element of [l]^l to be covered.

Usage:
    python verify_mu4_ip.py 4 11 highs
"""

import math
import sys
from itertools import permutations, product


def model(l):
    idp = tuple(range(l))
    perms = list(permutations(range(l)))
    pts = list(product(range(l), repeat=l))
    idx = {a: i for i, a in enumerate(pts)}

    cols = []
    for rest in product(perms, repeat=l - 1):
        pi = (idp,) + rest
        col = [
            idx[a]
            for a in pts
            if len({pi[i][a[i]] for i in range(l)}) == l
        ]
        cols.append(col)

    expected_blocks = math.factorial(l) ** (l - 1)
    expected_block_size = math.factorial(l)

    if len(cols) != expected_blocks:
        raise RuntimeError(
            f"model-generation error: expected {expected_blocks} blocks, "
            f"got {len(cols)}"
        )

    if any(len(c) != expected_block_size for c in cols):
        raise RuntimeError(
            f"model-generation error: every block should have size "
            f"{expected_block_size}"
        )

    return pts, cols


def run_mip_decision(N, pts, cols, backend):
    try:
        import pulp
    except ImportError as e:
        raise RuntimeError(
            "PuLP is not installed. Run: py -m pip install pulp"
        ) from e

    prob = pulp.LpProblem("kappa_cover_decision", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{j}", cat="Binary") for j in range(len(cols))]
    prob += 0

    hit = [[] for _ in range(len(pts))]
    for j, c in enumerate(cols):
        for p in c:
            hit[p].append(x[j])

    for p in range(len(pts)):
        if not hit[p]:
            raise RuntimeError(f"model-generation error: point {p} is uncovered")
        prob += pulp.lpSum(hit[p]) >= 1

    prob += pulp.lpSum(x) <= N

    if backend == "highs":
        solver = pulp.HiGHS(msg=True)
    elif backend == "gurobi":
        solver = pulp.GUROBI(msg=True)
    elif backend == "cbc":
        solver = pulp.PULP_CBC_CMD(msg=True)
    else:
        raise ValueError("backend must be one of: highs, gurobi, cbc")

    prob.solve(solver)
    status = pulp.LpStatus[prob.status]

    chosen = None
    if status == "Optimal":
        chosen = [
            j for j, var in enumerate(x)
            if pulp.value(var) is not None and pulp.value(var) > 0.5
        ]

    return status, chosen


def verify(chosen, cols, pts, N):
    if chosen is None or len(chosen) > N:
        return False

    covered = set()
    for j in chosen:
        covered.update(cols[j])

    return len(covered) == len(pts)


def main():
    l = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    backend = sys.argv[3].lower() if len(sys.argv) > 3 else "highs"

    if backend not in {"highs", "gurobi", "cbc"}:
        print("Backend must be one of: highs, gurobi, cbc")
        return 2

    print("Building decision set-cover instance...", flush=True)
    pts, cols = model(l)

    print(
        f"l={l} N={N} backend={backend}: "
        f"{len(cols)} blocks, {len(pts)} points, block size {len(cols[0])}",
        flush=True,
    )

    print(
        f"Decision question: can at most {N} blocks cover all {len(pts)} points?",
        flush=True,
    )

    try:
        status, chosen = run_mip_decision(N, pts, cols, backend)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print(f"Solver status: {status}")

    if status == "Infeasible":
        print(
            f"INFEASIBLE: no covering family of size <= {N}. "
            f"Therefore kappa({l}) > {N}."
        )
        return 0

    if status == "Optimal":
        ok = verify(chosen, cols, pts, N)
        print(
            f"FEASIBLE: family of size {len(chosen)} found; verified = {ok}."
        )

        if not ok:
            print("ERROR: solver solution failed independent verification.")
            return 3

        print(f"Therefore kappa({l}) <= {N}.")
        return 0

    print(
        "Search ended without a proof of feasibility or infeasibility. "
        "No mathematical conclusion is drawn."
    )
    return 4


if __name__ == "__main__":
    sys.exit(main())
