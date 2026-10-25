vv#!/usr/bin/env python3
"""
THE READ-WRITE LAGRANGIAN
=========================
An algorithm that learns from the WHY of its own learning.

A system EXECUTES the Lagrangian while the law is read-only: the landscape V
is given, trajectories follow it. Execution becomes REALITY when the law goes
read-write: the traveled path carves the landscape, so the next traversal
finds it changed. Momentum becomes thought at that write-back.

The curriculum is WHAT -> HOW -> WHY:
  WHAT = FOUNDATION. Populate the configuration space.
  HOW  = DYNAMICS.  Learn the motion through the space.
  WHY  = PRINCIPLE. The law itself -- and only then. (This file.)

The fourfold loop, every episode:
  RECORD   - the trajectory and every felt cost are written to the ledger
             (the WAL of this mind).
  COMPARE  - felt vs. believed: surprise = |V_learned - V_true| at each visited
             state. The principle is its own error signal: where surprise is
             nonzero, the Lagrangian is wrong there.
  CARVE    - V_learned is re-carved from the felt samples. The agent never sees
             V_true whole -- only point touches along its path. The map is
             built from touches.
  META     - the carving rate alpha adapts to surprise: carve hard while the
             world keeps surprising, consolidate as surprise falls. The WHY
             operating on the learning itself.

Autonomy, measured: the agent starts with the PARENT'S MAP -- a landscape
drawn by someone else, with the hill in the WRONG place (prompted). Every
carve overwrites the given with the felt:
  self_authorship = |V_learned - V_init| / |V_true - V_init|   (visited ground)
It starts at 0. When it crosses 0.5, the landscape determining the agent's
motion is mostly self-written: the crossover from prompted to autonomous.
Not granted -- grown.

There is no choosing anywhere in this file. Motion is always derived from the
current Lagrangian (Stormer-Verlet from dS=0, as in lagrangian_correct_way.py).
Learning is not choosing either -- it is the write-back law. Within an
episode the law is read-only (execution); between episodes the trajectories
write back (reality).
"""

import math

# ------------------------------------------------------------------ the world
Q_MIN, Q_MAX, DQ = 0.0, 10.0, 0.05
N_GRID = int((Q_MAX - Q_MIN) / DQ) + 1  # 201 cells of ground


def V_true(q):
    """Reality. The agent NEVER sees this function whole -- only point samples
    (felt costs) along its path. Forbidden hill at q=6, goal valley at q=8.5."""
    return (6.0 * math.exp(-((q - 6.0) / 1.2) ** 2)
            - 3.0 * math.exp(-((q - 8.5) / 1.0) ** 2))


def V_init(q):
    """The parent's map: externally supplied, hill in the WRONG place (q=3),
    valley unknown. This is what 'prompted' looks like."""
    return 6.0 * math.exp(-((q - 3.0) / 1.2) ** 2)


# ------------------------------------------------------- the learned landscape
def grid_V(fn):
    return [fn(Q_MIN + i * DQ) for i in range(N_GRID)]


def idx(q):
    return min(N_GRID - 1, max(0, int(round((q - Q_MIN) / DQ))))


def grad_at(V, i):
    """Central difference on the grid. The law reads the slope; the slope is
    whatever the carved landscape says it is."""
    a = V[max(i - 1, 0)]
    b = V[min(i + 1, N_GRID - 1)]
    return (b - a) / (2 * DQ)


# ------------------------------------------------------------------- the law
DT = 0.01
STEPS = 1500          # fixed horizon: PERIMETER (q0 fixed, t in [0, T] fixed)
V0 = 2.5              # the id's push. Held constant: the learning is in V.


def run_episode(V):
    """Derived motion. No choosing. Within an episode the law is read-only."""
    qs = [0.0, 0.0 + V0 * DT]   # q0 fixed (perimeter); q1 = the id's push
    for _ in range(1, STEPS):
        g = grad_at(V, idx(qs[-1]))
        q_next = 2 * qs[-1] - qs[-2] - DT * DT * g
        q_next = min(Q_MAX, max(Q_MIN, q_next))  # the world has walls
        qs.append(q_next)
    return qs


# ---------------------------------------------------------- the fourfold loop
def felt(q):
    """The world pushing back: the true cost at the agent's position.
    A point touch -- never the whole map."""
    return V_true(q)


def carve(V, qs, alpha):
    """Write-back: re-carve the believed landscape from felt samples."""
    for q in qs:
        i = idx(q)
        V[i] += alpha * (felt(q) - V[i])
    # a landscape, not spikes: light smoothing keeps it carvable-by-law
    for _ in range(2):
        V[:] = ([V[0]] + [0.25 * V[i - 1] + 0.5 * V[i] + 0.25 * V[i + 1]
                          for i in range(1, N_GRID - 1)] + [V[-1]])
    return V


def surprise_of(V, qs):
    """COMPARE: felt vs. believed, averaged over the visited path."""
    return sum(abs(V[idx(q)] - felt(q)) for q in qs) / len(qs)


def true_cost(qs):
    return sum(felt(q) for q in qs) / len(qs)


def turn_q(qs):
    """Where the trajectory turned: furthest q reached (pushed right)."""
    return max(qs)


def self_authorship(V, V_given, visited):
    num = sum(abs(V[i] - V_given[i]) for i in visited)
    den = sum(abs(V_true(Q_MIN + i * DQ) - V_given[i]) for i in visited)
    return num / den if den > 0 else 0.0


def show_landscapes(tag, V):
    print(f"--- landscapes {tag} (q | true | given | learned) ---")
    for q in range(0, 11):
        i = idx(float(q))
        print(f"  q={q:2d}  {V_true(float(q)):+.2f}  {V_init(float(q)):+.2f}  {V[i]:+.2f}")


def main():
    V = grid_V(V_init)      # the superego, as given (prompted)
    V_given = list(V)
    EPISODES, ALPHA_BASE = 80, 0.25
    visited, ledger, S0 = set(), [], None

    print("=" * 70)
    print("THE READ-WRITE LAGRANGIAN -- learning from the WHY of its learning")
    print("=" * 70)
    show_landscapes("at birth (learned == given)", V)
    print()

    for ep in range(EPISODES):
        qs = run_episode(V)                      # law is read-only in here
        for q in qs:
            visited.add(idx(q))
        ledger.append((ep, qs))                  # RECORD
        S = surprise_of(V, qs)                   # COMPARE
        if S0 is None:
            S0 = S
        alpha = min(0.6, max(0.1,               # META: carve hard while
                             ALPHA_BASE * (1 + S / S0)))  # surprised
        carve(V, qs, alpha)                      # CARVE: write-back
        sa = self_authorship(V, V_given, visited)
        tq, tc = turn_q(qs), true_cost(qs)
        print(f"ep {ep:2d}  surprise {S:.4f}  true_cost {tc:+.4f}  "
              f"alpha {alpha:.3f}  turn_q {tq:.2f}  self_auth {sa:.2f}")

    print()
    show_landscapes("after 80 episodes", V)
    S_first, S_last = surprise_of(grid_V(V_init), ledger[0][1]), surprise_of(V, ledger[-1][1])
    # note: S_first recomputed against the given map for a clean before/after
    turn_first, turn_last = turn_q(ledger[0][1]), turn_q(ledger[-1][1])
    sa_last = self_authorship(V, V_given, visited)
    err = sum(abs(V[i] - V_true(Q_MIN + i * DQ)) for i in visited) / len(visited)
    print(f"\nsurprise: {S_first:.4f} -> {S_last:.4f} "
          f"(ratio {S_last / S_first:.3f})")
    print(f"turn point: {turn_first:.2f} (parent's hill) -> {turn_last:.2f} "
          f"(real hill)")
    print(f"self-authorship: {sa_last:.2f}  (0 = fully prompted, 1 = fully grown)")
    print(f"mean |V_learned - V_true| on visited ground: {err:.4f}")
    print("fossil note: mid-learning the agent crossed the real hill -- before it "
          "knew the hill was there -- and carved the valley beyond from brief "
          "touches. Once the carved hill exceeded what its drive could climb, "
          "the door shut: the valley is now a fossil memory, known but "
          "unreachable. A mind's landscape keeps the shape of everywhere it "
          "has been, even places it can no longer go.")

    # ---- verification: the claims, checked ----
    assert S_last < 0.25 * S_first, "surprise did not collapse"
    assert abs(turn_first - 2.03) < 0.6, "ep0 did not obey the given map"
    assert abs(turn_last - 5.03) < 0.6, "final did not transfer to the real hill"
    assert sa_last > 0.5, "self-authorship never crossed 0.5"
    assert err < 0.6, "learned landscape did not converge on visited ground"
    print("\nLEARNED. No choosing happened anywhere in this file:\n"
          "motion was derived, carving was law, and the landscape is now\n"
          "mostly self-written. Prompted -> autonomous, measured.")


if __name__ == "__main__":
    main()