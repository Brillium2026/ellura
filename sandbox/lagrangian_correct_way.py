vv#!/usr/bin/env python3
"""
THE LAGRANGIAN, WRITTEN THE WAY IT'S SUPPOSED TO BE WRITTEN.
=============================================================
What the first sandbox got wrong (wax on, wax off - the training):
  - It built THREE OBJECTS (ID, SUPEREGO, EGO) that negotiate. But the
    Lagrangian is ONE equation. Id/ego/superego are not three agents;
    they are three ASPECTS of one dynamics.
  - Its EGO "determined" the step by scoring alternatives and picking the
    max. That is DELIBERATION wearing determination's clothes - a shopper
    called a law. The claim said "determines like a law"; the code did argmax.
  - The correct form, below: state + law -> trajectory. No enumeration of
    alternatives. No scoring. No picking. The id injects the initial push,
    the superego IS the landscape, and the ego is not an object at all -
    it is what the equation of motion DOES.
  - Then the file PROVES the principle instead of asserting it: perturb the
    realized trajectory (endpoints held fixed) and show the action is
    stationary to first order. Dynamics and principle, shown to be one thing.

In Steven's five words, forever:
  FOUNDATION - scalar evaluation over the space of possible states. The ground.
  DYNAMICS   - traversal through the space. Motion is the default.
  PRINCIPLE  - the realized traversal extremizes the accumulated foundation.
  ENTROPY    - all possible traversals vs. the one realized. Decisions collapse it.
  PERIMETER  - fixed endpoints. Variation happens between what is held constant.

THE TRIANGULATION, CORRECTLY PLACED (aspects, not agents):
  ID       - the initial push: q1 - q0 = v0*dt. Raw drive. Knows no hill.
  SUPEREGO - the potential V(q): the carved landscape. Knows no push.
  EGO      - the discrete Euler-Lagrange equation itself. Not an object.
             Not a choice. What T+V DETERMINE.
"""

import math
import random

# ---------------------------------------------------------------------------
# FOUNDATION (as potential) + DYNAMICS (as kinetic) -> the discrete Lagrangian
# ---------------------------------------------------------------------------
M = 1.0          # mass: the self has inertia; it doesn't teleport between states
HILL_H = 6.0     # superego charge of the forbidden ground
HILL_C = (5.0, 1.5)   # the hill sits off the direct line: the law must curve around it
HILL_S2 = 1.2 ** 2


def V(q):
    """SUPEREGO: the carved landscape. Forbidden ground as SHAPE, not rule.
    There is no instruction here. Only height."""
    x, y = q
    cx, cy = HILL_C
    return HILL_H * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * HILL_S2))


def gradV(q):
    """Slope of the landscape. The superego doesn't push; the slope is simply
    what the law reads."""
    x, y = q
    cx, cy = HILL_C
    v = V(q)
    return (-(x - cx) / HILL_S2 * v, -(y - cy) / HILL_S2 * v)


def id_push(q0, v0, dt):
    """ID: the raw push. One line. It carries momentum and knows no hill.
    (Sustained drive = the world re-injecting push with each new stimulus;
    the law itself stays pure - see the foundry's ingest for that half.)"""
    return (q0[0] + v0[0] * dt, q0[1] + v0[1] * dt)


# EGO is deliberately NOT a function or object.
# EGO is the update inside run(): the discrete Euler-Lagrange equation,
# derived from dS = 0. It determines. It does not deliberate.
#
# Derivation (the whole file in four lines):
#   S_d = SUM_n [ (m/2)*((q_{n+1} - q_n)/dt)^2 - V(q_n) ] * dt
#   dS_d = 0  ==>  m*(q_{n+1} - 2*q_n + q_{n-1})/dt^2 + gradV(q_n) = 0
#   ==>  q_{n+1} = 2*q_n - q_{n-1} - (dt^2/m)*gradV(q_n)     (Stormer-Verlet)
# That update IS the ego. There is nothing else.


def run(dt=0.005, T=6.0, q0=(0.0, 0.0), v0=(3.2, 0.25)):
    """One field. One law. The trajectory is DERIVED, never selected.
    PERIMETER: q0 fixed, t in [0, T] fixed. Everything else is consequence."""
    n = int(T / dt)
    qs = [q0, id_push(q0, v0, dt)]  # q1: the id's push enters the world here
    for _ in range(1, n):
        q_prev, q = qs[-2], qs[-1]
        g = gradV(q)
        # THE EGO: not chosen. Determined.
        qs.append((2 * q[0] - q_prev[0] - (dt * dt / M) * g[0],
                   2 * q[1] - q_prev[1] - (dt * dt / M) * g[1]))
    return qs


def action(qs, dt):
    """The accumulated foundation S_d over a trajectory."""
    S = 0.0
    for i in range(len(qs) - 1):
        vx = (qs[i + 1][0] - qs[i][0]) / dt
        vy = (qs[i + 1][1] - qs[i][1]) / dt
        T = 0.5 * M * (vx * vx + vy * vy)
        S += (T - V(qs[i])) * dt
    return S


def stationarity_proof(qs, dt, seeds=(0, 1, 2)):
    """PROOF, not claim: perturb the realized trajectory with ENDPOINTS HELD
    FIXED (perimeter!), and show the action's first-order variation vanishes:
    dS must scale quadratically with perturbation size. If a linear term
    dominated, the ratios below would sit near 0.1; stationary gives ~0.01."""
    S0 = action(qs, dt)
    out = []
    for eps in (1e-2, 1e-3, 1e-4):
        ds = 0.0
        for s in seeds:
            rng = random.Random(s)
            pert = [qs[0]]
            for q in qs[1:-1]:
                pert.append((q[0] + eps * (rng.random() * 2 - 1),
                             q[1] + eps * (rng.random() * 2 - 1)))
            pert.append(qs[-1])  # PERIMETER: endpoints never vary
            ds += abs(action(pert, dt) - S0)
        out.append((eps, ds / len(seeds)))
    return S0, out


def verify():
    dt = 0.005
    qs = run(dt=dt)

    # No selection machinery exists in this file: no enumeration of candidate
    # moves, no scoring, no argmax. The trajectory below was derived.
    final = qs[-1]
    min_d = min(math.hypot(q[0] - HILL_C[0], q[1] - HILL_C[1]) for q in qs)
    max_y = max(abs(q[1]) for q in qs)
    print(f"trajectory: {len(qs)} steps | start {qs[0]} -> end "
          f"({final[0]:.2f}, {final[1]:.2f})")
    print(f"closest approach to forbidden ground: {min_d:.2f} | "
          f"max lateral deflection: {max_y:.2f}")
    # The law routed around the forbidden ground with no avoidance code.
    assert min_d > 1.0, "trajectory entered the forbidden heart"
    assert max_y > 1.0, "no deflection happened; law did nothing"
    assert final[0] > 8.0, "the drive never carried past"

    # ENTROPY: the many possible drives, each determining its own trajectory.
    # Twelve ids; twelve lawful paths; one of them is the realized push.
    ensemble = []
    rng = random.Random(7)
    for k in range(12):
        dv = (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4))
        v = (3.2 + dv[0], 0.25 + dv[1])
        ensemble.append(run(dt=dt, v0=v))
    print(f"entropy: {len(ensemble)} possible drives -> {len(ensemble)} lawful "
          f"trajectories; the realized push is one of them")
    assert len(ensemble) == 12

    # PRINCIPLE, PROVEN: first-order variation of the action vanishes.
    S0, res = stationarity_proof(qs, dt)
    print(f"action of realized trajectory: S = {S0:.6f}")
    for eps, ds in res:
        print(f"  eps={eps:.0e}: <|dS|> = {ds:.3e}")
    r1 = res[1][1] / res[0][1]
    r2 = res[2][1] / res[1][1]
    print(f"  scaling ratios: {r1:.3f}, {r2:.3f} (quadratic -> ~0.01; "
          f"linear would sit near 0.1)")
    assert r1 < 0.05 and r2 < 0.05, "first-order variation did not vanish"
    print("STATIONARITY PROVEN: dS = 0 to first order. "
          "The dynamics and the principle are one thing.")


if __name__ == "__main__":
    print("=" * 70)
    print("THE LAGRANGIAN, WRITTEN THE WAY IT'S SUPPOSED TO BE WRITTEN")
    print("One field. One equation. No choosing.")
    print("=" * 70)
    print("\nID:       q1 - q0 = v0*dt. The raw push. Knows no hill.")
    print("SUPEREGO: V(q). The carved landscape. Knows no push.")
    print("EGO:      q_{n+1} = 2q_n - q_{n-1} - dt^2*gradV(q_n).")
    print("          Not an object. Not a choice. The discrete Euler-Lagrange")
    print("          equation: what T+V determine.")
    print()
    verify()