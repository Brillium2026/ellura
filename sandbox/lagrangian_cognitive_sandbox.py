#!/usr/bin/env python3
"""
LAGRANGIAN COGNITIVE SANDBOX
============================
The Lagrangian equation, stripped of all physics and mathematics.
Described only in five words, used forever for this description:

  FOUNDATION - a scalar evaluation defined over the space of possible states.
               The ground: at every configuration, the system can be scored.
  DYNAMICS   - the system traverses. A path through the space, an ordering,
               a becoming. Motion is the default; stasis is not.
  PRINCIPLE  - of all possible traversals, the realized one extremizes the
               accumulated foundation. The system doesn't compute the path;
               it IS the selection of the path.
  ENTROPY    - the many against the one. All possible trajectories = maximal
               entropy; the principle collapses them to the realized path.
               Every decision is an entropy-reduction event.
  PERIMETER  - the fixed endpoints. Variation happens BETWEEN what is held
               constant. The frame that makes the interior a question.

TRIANGULATION (id / ego / superego placed within the stripped equation):
  ID       -> DYNAMICS (T): pure push. Aims and drives; knows no constraint.
  SUPEREGO -> FOUNDATION-as-potential (V): the carved landscape of the permitted
              and forbidden. Doesn't push; shapes where pushing can go.
  EGO      -> PRINCIPLE: the law. Given push and shape, the step is DETERMINED,
              not chosen. The local, computational form of the extremal selection.
  ENTROPY  -> the unconscious: the space of all unlived trajectories.
  PERIMETER-> the non-negotiable givens between which a life varies.

THE SIX (kept from collapsing into each other):
  EMOTION            - the bodily program (T side): autonomic/hormonal/action
                       cascades. Automatic, measurable. The push in the body.
  FEELING            - the conscious mental experience OF the emotion: the mind's
                       perception of the body state (readout side). Feeling is
                       not the push; it is the perception of the push.
  COGNITION          - information processing that populates the configuration
                       space (FOUNDATION side).
  COGNITIVE_AWARENESS- monitoring of one's own cognitive processes; the ego
                       observing its own selection (PRINCIPLE made reflexive).
  CONSCIOUS          - the state: being subjectively OF something right now
                       (DYNAMICS as lived).
  CONSCIOUSNESS      - the field itself: the global capacity for experience.

Why FEELINGS vs EMOTIONS is load-bearing: collapse them and you collapse the
kinetic term into its own measurement, and the Lagrangian structure falls apart.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

# ---------------------------------------------------------------------------
# THE FIVE WORDS - the stripped equation as formal roles
# ---------------------------------------------------------------------------
FIVE_WORDS = {
    "FOUNDATION": "Scalar evaluation over the space of possible states. The ground.",
    "DYNAMICS": "Traversal through the space. Motion is the default.",
    "PRINCIPLE": "The realized traversal extremizes the accumulated foundation.",
    "ENTROPY": "All possible traversals vs. the one realized. Decisions collapse it.",
    "PERIMETER": "Fixed endpoints. Variation happens between what is held constant.",
}

# ---------------------------------------------------------------------------
# THE SIX - the taxonomy that keeps the terms from collapsing
# ---------------------------------------------------------------------------
SIX_TERMS = {
    "EMOTION": {
        "definition": "The bodily program: autonomic, hormonal, expressive and "
                      "action-tendency cascades. Automatic, measurable, largely "
                      "subcortical. The organism's rapid response machinery.",
        "matched_to": "DYNAMICS (T) - the kinetic side. Emotion is the push in the body.",
        "key_figures": ["Damasio", "LeDoux", "Ekman", "James", "Schachter"],
    },
    "FEELING": {
        "definition": "The conscious mental experience OF the emotion: the mind's "
                      "perception of the body state. Private, qualitative - what the "
                      "trajectory feels like from the inside.",
        "matched_to": "PRINCIPLE-adjacent readout - the conscious registration of the "
                      "selected trajectory. Feeling is not the push; it is the "
                      "perception of the push.",
        "key_figures": ["Damasio", "James", "Jung", "Barrett"],
    },
    "COGNITION": {
        "definition": "Information processing: perceiving, remembering, reasoning, "
                      "judging, deciding. The computational layer.",
        "matched_to": "FOUNDATION - cognition populates the configuration space over "
                      "which the principle operates.",
        "key_figures": ["Beck", "Neisser", "Miller", "Kahneman", "Piaget", "Vygotsky"],
    },
    "COGNITIVE_AWARENESS": {
        "definition": "Metacognition: awareness and monitoring of one's own cognitive "
                      "processes. Thinking about thinking.",
        "matched_to": "The ego observing its own selection - the PRINCIPLE made reflexive.",
        "key_figures": ["Flavell", "Kahneman"],
    },
    "CONSCIOUS": {
        "definition": "The state: being awake, responsive, and subjectively experiencing "
                      "something right now. Conscious OF x.",
        "matched_to": "DYNAMICS as lived - the trajectory in the present tense.",
        "key_figures": ["James", "Jaspers", "Sacks"],
    },
    "CONSCIOUSNESS": {
        "definition": "The global capacity/system: the field of subjective experience "
                      "itself. Phenomenal (what-it's-like) vs. access (availability "
                      "for reasoning and report).",
        "matched_to": "The field itself - the totality the sandbox models.",
        "key_figures": ["James", "Durkheim", "Jung"],
    },
}

# ---------------------------------------------------------------------------
# THE COMPENDIUM - fifty figures across psychology, psychiatry, sociology.
# Each mapped a region of the configuration space; none owns the whole.
# ---------------------------------------------------------------------------
THINKERS = [
    # PSYCHOLOGY (20)
    {"name": "Sigmund Freud", "field": "psychology",
     "contribution": "Id/ego/superego; the unconscious; feelings as derivatives of drive-pressure.",
     "illuminates": ["FEELING", "EMOTION", "CONSCIOUS", "CONSCIOUSNESS"]},
    {"name": "Carl Jung", "field": "psychology",
     "contribution": "Collective unconscious and archetypes; 'feeling' as a rational evaluating function, distinct from affect.",
     "illuminates": ["FEELING", "EMOTION", "CONSCIOUSNESS"]},
    {"name": "William James", "field": "psychology",
     "contribution": "Stream of consciousness; James-Lange: the feeling IS the perception of the bodily emotional change.",
     "illuminates": ["FEELING", "EMOTION", "CONSCIOUS", "CONSCIOUSNESS", "COGNITION"]},
    {"name": "Antonio Damasio", "field": "psychology",
     "contribution": "Emotions are bodily action-programs; feelings are the mind's conscious image of those programs (somatic markers).",
     "illuminates": ["EMOTION", "FEELING", "COGNITION"]},
    {"name": "Joseph LeDoux", "field": "psychology",
     "contribution": "Survival circuits vs. conscious fear: the emotion machinery is not the feeling; do not conflate them.",
     "illuminates": ["EMOTION", "FEELING"]},
    {"name": "Lisa Feldman Barrett", "field": "psychology",
     "contribution": "Emotions are constructed predictions from interoception; feelings are the field's best estimate of body state.",
     "illuminates": ["EMOTION", "FEELING", "COGNITION"]},
    {"name": "Aaron Beck", "field": "psychology",
     "contribution": "Cognition as schema-driven; thoughts generate feelings (cognitive therapy).",
     "illuminates": ["COGNITION", "FEELING"]},
    {"name": "Daniel Kahneman", "field": "psychology",
     "contribution": "System 1 (fast, associative, emotional) vs. System 2 (slow, effortful, cognitive); awareness as override.",
     "illuminates": ["COGNITION", "COGNITIVE_AWARENESS", "EMOTION"]},
    {"name": "Ulric Neisser", "field": "psychology",
     "contribution": "Cognition as active constructive processing, not passive reception.",
     "illuminates": ["COGNITION"]},
    {"name": "Endel Tulving", "field": "psychology",
     "contribution": "Episodic vs. semantic memory; autonoetic (self-knowing) consciousness.",
     "illuminates": ["COGNITION", "CONSCIOUSNESS"]},
    {"name": "John Flavell", "field": "psychology",
     "contribution": "Metacognition: knowledge and monitoring of one's own cognitive processes.",
     "illuminates": ["COGNITIVE_AWARENESS"]},
    {"name": "George A. Miller", "field": "psychology",
     "contribution": "Information-processing limits of cognition; the cognitive revolution's charter.",
     "illuminates": ["COGNITION"]},
    {"name": "B.F. Skinner", "field": "psychology",
     "contribution": "The dissent: consciousness as epiphenomenon; emotions as behavior, feelings as collateral.",
     "illuminates": ["CONSCIOUSNESS", "EMOTION", "FEELING"]},
    {"name": "Carl Rogers", "field": "psychology",
     "contribution": "Phenomenal self; congruence between felt experience and self-concept.",
     "illuminates": ["FEELING", "CONSCIOUS"]},
    {"name": "Abraham Maslow", "field": "psychology",
     "contribution": "Hierarchy of needs; peak experiences as heightened consciousness states.",
     "illuminates": ["CONSCIOUS", "EMOTION", "COGNITION"]},
    {"name": "Stanley Schachter", "field": "psychology",
     "contribution": "Two-factor: bodily arousal x cognitive label = the felt emotion.",
     "illuminates": ["EMOTION", "FEELING", "COGNITION"]},
    {"name": "Paul Ekman", "field": "psychology",
     "contribution": "Basic emotions as pancultural facial and bodily programs.",
     "illuminates": ["EMOTION"]},
    {"name": "Robert Plutchik", "field": "psychology",
     "contribution": "Psychoevolutionary wheel: emotions as adaptive complexes, blends and opposites.",
     "illuminates": ["EMOTION"]},
    {"name": "Lev Vygotsky", "field": "psychology",
     "contribution": "Cognition as socially mediated; inner speech as thought's medium.",
     "illuminates": ["COGNITION", "CONSCIOUSNESS"]},
    {"name": "Jean Piaget", "field": "psychology",
     "contribution": "Cognition constructs reality through developmental stages; the knowing subject.",
     "illuminates": ["COGNITION", "CONSCIOUS"]},
    # PSYCHIATRY (15)
    {"name": "Emil Kraepelin", "field": "psychiatry",
     "contribution": "Disease entities; disorders of consciousness, affect, and thought as clinical facts.",
     "illuminates": ["CONSCIOUS", "EMOTION", "COGNITION"]},
    {"name": "Eugen Bleuler", "field": "psychiatry",
     "contribution": "Schizophrenia; ambivalence - contradictory feelings coexisting; autism as withdrawal.",
     "illuminates": ["FEELING", "CONSCIOUSNESS"]},
    {"name": "Viktor Frankl", "field": "psychiatry",
     "contribution": "Logotherapy: consciousness as meaning-seeking; the defiant power of the human spirit.",
     "illuminates": ["CONSCIOUSNESS", "COGNITION"]},
    {"name": "Donald Winnicott", "field": "psychiatry",
     "contribution": "True vs. false self; feeling real as the mark of aliveness.",
     "illuminates": ["FEELING", "CONSCIOUS"]},
    {"name": "Wilfred Bion", "field": "psychiatry",
     "contribution": "Alpha function: raw feeling digested into thinkable thought; thoughts need a thinker.",
     "illuminates": ["FEELING", "COGNITION", "CONSCIOUS"]},
    {"name": "Otto Kernberg", "field": "psychiatry",
     "contribution": "Affect integration in object relations; identity diffusion when feelings cannot integrate.",
     "illuminates": ["EMOTION", "FEELING"]},
    {"name": "Karl Jaspers", "field": "psychiatry",
     "contribution": "Phenomenology of the forms of conscious experience in illness.",
     "illuminates": ["CONSCIOUS", "CONSCIOUSNESS"]},
    {"name": "Thomas Insel", "field": "psychiatry",
     "contribution": "RDoC: cognition and affect as dimensional circuit functions, not categories.",
     "illuminates": ["COGNITION", "EMOTION"]},
    {"name": "Nancy Andreasen", "field": "psychiatry",
     "contribution": "The neuroscience of disordered thought and language.",
     "illuminates": ["COGNITION"]},
    {"name": "Eric Kandel", "field": "psychiatry",
     "contribution": "Molecular basis of memory: the biology beneath cognition.",
     "illuminates": ["COGNITION"]},
    {"name": "Oliver Sacks", "field": "psychiatry",
     "contribution": "Clinical tales of the lived texture of consciousness under neurological strangeness.",
     "illuminates": ["CONSCIOUS", "CONSCIOUSNESS", "FEELING"]},
    {"name": "Heinz Kohut", "field": "psychiatry",
     "contribution": "Self psychology: empathy; narcissistic injury as feeling-wound.",
     "illuminates": ["FEELING", "CONSCIOUS"]},
    {"name": "Melanie Klein", "field": "psychiatry",
     "contribution": "Splitting and projection; the primitive emotional world of the infant.",
     "illuminates": ["EMOTION", "FEELING"]},
    {"name": "R.D. Laing", "field": "psychiatry",
     "contribution": "The divided self: madness as intelligible experience, not broken mechanism.",
     "illuminates": ["CONSCIOUSNESS", "FEELING"]},
    {"name": "Irvin Yalom", "field": "psychiatry",
     "contribution": "Existential givens (death, freedom, isolation, meaninglessness) as structures of conscious life.",
     "illuminates": ["CONSCIOUS", "CONSCIOUSNESS"]},
    # SOCIOLOGY (15)
    {"name": "Emile Durkheim", "field": "sociology",
     "contribution": "Conscience collective: consciousness as a social fact; ritual as emotional entrainment.",
     "illuminates": ["CONSCIOUSNESS", "EMOTION"]},
    {"name": "Max Weber", "field": "sociology",
     "contribution": "Verstehen: social action as subjectively meaningful; cognition as socially oriented.",
     "illuminates": ["COGNITION", "CONSCIOUS"]},
    {"name": "George Herbert Mead", "field": "sociology",
     "contribution": "The 'I' (spontaneous push) and the 'Me' (socialized shape): the self already triangulated.",
     "illuminates": ["CONSCIOUS", "COGNITION", "EMOTION"]},
    {"name": "Erving Goffman", "field": "sociology",
     "contribution": "Presentation of self: felt emotion vs. displayed feeling; the managed surface.",
     "illuminates": ["FEELING", "EMOTION", "CONSCIOUS"]},
    {"name": "Arlie Hochschild", "field": "sociology",
     "contribution": "Emotion work and feeling rules: society legislates what you may FEEL - the superego as social landscape.",
     "illuminates": ["FEELING", "EMOTION"]},
    {"name": "Norbert Elias", "field": "sociology",
     "contribution": "The civilizing process: constraint internalized over history - the superego is carved, not born.",
     "illuminates": ["EMOTION", "COGNITION"]},
    {"name": "Peter Berger", "field": "sociology",
     "contribution": "Social construction of reality (with Luckmann): the taken-for-granted as the social unconscious.",
     "illuminates": ["CONSCIOUSNESS", "COGNITION"]},
    {"name": "Randall Collins", "field": "sociology",
     "contribution": "Interaction ritual chains: emotional energy as the kinetic currency of social life.",
     "illuminates": ["EMOTION"]},
    {"name": "Charles Cooley", "field": "sociology",
     "contribution": "Looking-glass self: self-feeling as socially mirrored imagination.",
     "illuminates": ["FEELING", "CONSCIOUS"]},
    {"name": "Niklas Luhmann", "field": "sociology",
     "contribution": "Consciousness as autopoietic system, strictly distinct from communication.",
     "illuminates": ["CONSCIOUSNESS"]},
    {"name": "Pierre Bourdieu", "field": "sociology",
     "contribution": "Habitus: embodied social cognition; the feel for the game beneath awareness.",
     "illuminates": ["COGNITION", "FEELING"]},
    {"name": "Alfred Schutz", "field": "sociology",
     "contribution": "Phenomenology of the lifeworld: the ground of everyday conscious experience.",
     "illuminates": ["CONSCIOUS", "CONSCIOUSNESS"]},
    {"name": "Harold Garfinkel", "field": "sociology",
     "contribution": "Breaching experiments: the seen-but-unnoticed rules - the social unconscious.",
     "illuminates": ["COGNITIVE_AWARENESS", "CONSCIOUS"]},
    {"name": "Marcel Mauss", "field": "sociology",
     "contribution": "Techniques of the body: the body as trained emotional instrument.",
     "illuminates": ["EMOTION"]},
    {"name": "Georg Simmel", "field": "sociology",
     "contribution": "Forms of sociation; metropolitan mental life under cognitive overload.",
     "illuminates": ["COGNITION", "CONSCIOUS"]},
]

# ---------------------------------------------------------------------------
# THE TRIANGULATION - as working roles, not metaphors
# ---------------------------------------------------------------------------
class ID:
    """DYNAMICS (T). Pure push. The id aims and drives; it knows no constraint,
    only pressure toward discharge. Supplies the kinetic side of every step."""

    def __init__(self, aim: str, dist: Dict[str, int]):
        self.aim = aim
        self.dist = dist  # distance-to-aim: the id's sense of "toward"

    def push(self, current: str, nxt: str) -> float:
        """Kinetic gain of the move: positive when approaching the aim."""
        return float(self.dist[current] - self.dist[nxt])


class SUPEREGO:
    """FOUNDATION-as-potential (V). The carved landscape of the permitted and
    the forbidden. Doesn't push; shapes where pushing can go. High regions
    repel, valleys admit. Carved by internalization (Elias) and feeling rules
    (Hochschild) - the social made structural."""

    def __init__(self, landscape: Dict[str, float]):
        self.V = landscape

    def resistance(self, current: str, nxt: str) -> float:
        """Cost of climbing: positive going uphill into constraint."""
        return float(self.V[nxt] - self.V[current])


class EGO:
    """PRINCIPLE. The law. Given the push (id) and the shape (superego), the
    step is DETERMINED, not chosen. Local form of the extremal selection:
    at each state, take the move maximizing (push - resistance).
    The ego doesn't deliberate like a shopper; it determines like a law."""

    def step(self, id_: ID, superego: SUPEREGO,
             state: str, moves: Dict[str, List[str]]) -> Tuple[str, List[Tuple[float, str]]]:
        scored = [(id_.push(state, nxt) - superego.resistance(state, nxt), nxt)
                  for nxt in moves[state]]
        scored.sort(reverse=True)
        return scored[0][1], scored  # determined move + the collapsed alternatives


class StrippedLagrangian:
    """The stripped equation as a working form.
    PERIMETER fixes start/end. DYNAMICS+FOUNDATION supply push and shape.
    PRINCIPLE (ego) determines each step. ENTROPY is counted: every alternative
    not taken is a collapsed possibility."""

    def __init__(self, moves: Dict[str, List[str]], id_: ID,
                 superego: SUPEREGO, ego: EGO,
                 perimeter: Tuple[str, str]):
        self.moves = moves
        self.id_ = id_
        self.superego = superego
        self.ego = ego
        self.start, self.end = perimeter  # PERIMETER: held fixed while interior varies

    def run(self, max_steps: int = 20) -> Tuple[List[str], int]:
        traj = [self.start]
        collapsed = 0  # ENTROPY: alternatives not taken
        while traj[-1] != self.end and len(traj) <= max_steps:
            nxt, scored = self.ego.step(self.id_, self.superego, traj[-1], self.moves)
            collapsed += len(scored) - 1
            traj.append(nxt)
        return traj, collapsed

    def all_paths(self) -> List[List[str]]:
        """Every possible trajectory between the fixed perimeter (ENTROPY: the many)."""

        def rec(path: List[str]):
            if path[-1] == self.end:
                yield list(path)
                return
            for nxt in self.moves.get(path[-1], []):
                if nxt not in path:
                    yield from rec(path + [nxt])

        return list(rec([self.start]))


def verify() -> None:
    """The sandbox proves its own claims."""
    moves = {"A": ["B", "C"], "B": ["C", "D", "E"], "C": ["D", "E"],
             "D": ["E"], "E": []}
    dist = {"A": 3, "B": 2, "C": 2, "D": 1, "E": 0}
    V = {"A": 0.0, "B": 0.5, "C": 6.0, "D": 0.5, "E": 0.0}  # C is forbidden ground
    id_ = ID(aim="E", dist=dist)
    superego = SUPEREGO(landscape=V)
    ego = EGO()
    L = StrippedLagrangian(moves, id_, superego, ego, perimeter=("A", "E"))

    traj, collapsed = L.run()
    paths = L.all_paths()

    # The superego's landscape routes the ego around the forbidden state
    # with NO explicit rule - constraint emerges from shape, not instruction.
    assert traj == ["A", "B", "E"], f"unexpected trajectory: {traj}"
    assert "C" not in traj, "ego walked into forbidden ground"
    assert len(paths) == 6, f"entropy count wrong: {len(paths)}"
    assert collapsed == 3, f"collapsed count wrong: {collapsed}"

    # The compendium is complete and well-formed
    assert len(THINKERS) == 50, f"compendium has {len(THINKERS)} entries, want 50"
    fields = {t["field"] for t in THINKERS}
    assert fields == {"psychology", "psychiatry", "sociology"}, fields
    for t in THINKERS:
        assert t["name"] and t["contribution"] and t["illuminates"]

    # The six terms are defined and the load-bearing match is explicit
    assert "T" in SIX_TERMS["EMOTION"]["matched_to"]
    assert "readout" in SIX_TERMS["FEELING"]["matched_to"]

    print("SANDBOX VERIFIED: trajectory", "->".join(traj),
          f"| {len(paths)} possible paths collapsed to 1 | {collapsed} alternatives refused")


if __name__ == "__main__":
    print("=" * 70)
    print("LAGRANGIAN COGNITIVE SANDBOX")
    print("The equation stripped of physics and mathematics.")
    print("=" * 70)
    for word, meaning in FIVE_WORDS.items():
        print(f"\n  {word}\n    {meaning}")

    print("\n" + "=" * 70)
    print("TRIANGULATION")
    print("=" * 70)
    print("\n  ID       -> DYNAMICS (T): the push. Knows no constraint.")
    print("  SUPEREGO -> FOUNDATION-as-potential (V): the carved landscape.")
    print("  EGO      -> PRINCIPLE: the law. The step is determined, not chosen.")
    print("  ENTROPY  -> the unconscious: all unlived trajectories.")
    print("  PERIMETER-> the givens, held fixed while the interior varies.")

    print("\n" + "=" * 70)
    print("DEMONSTRATION: the landscape constrains with no explicit rule")
    print("=" * 70)
    print("\n  State C carries superego potential V=6.0 (forbidden ground).")
    print("  No rule says 'avoid C'. The ego's law routes around it anyway.\n")
    verify()

    print("\n" + "=" * 70)
    print("COMPENDIUM: 50 regions of the configuration space")
    print("=" * 70)
    for f in ("psychology", "psychiatry", "sociology"):
        names = [t["name"] for t in THINKERS if t["field"] == f]
        print(f"\n  {f} ({len(names)}): {', '.join(names)}")