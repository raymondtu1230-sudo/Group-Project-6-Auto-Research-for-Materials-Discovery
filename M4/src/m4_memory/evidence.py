"""Shared public-observation fields for online and exported evidence."""

import math
import re


def normalize_elements(elements):
    if not isinstance(elements, (list, tuple)) or not elements:
        raise ValueError("Provide the complete run chemical system as elements")
    if any(
        not isinstance(x, str) or not re.fullmatch(r"[A-Z][a-z]?", x) for x in elements
    ):
        raise ValueError("elements must contain element-symbol strings")
    return sorted(set(elements))


def candidate_composition(proposal, elements):
    """Read only species/occupancy from a public proposal Structure dictionary."""
    if not isinstance(proposal, dict) or not proposal.get("sites"):
        return None
    composition = {}
    for site in proposal["sites"]:
        for species in site["species"]:
            element = species["element"]
            amount = species.get("occu", 1)
            if element not in elements:
                raise ValueError("Proposal contains an element outside the run system")
            if (
                isinstance(amount, bool)
                or not isinstance(amount, (int, float))
                or not math.isfinite(amount)
                or amount <= 0
            ):
                raise ValueError("Species occupancy must be finite and positive")
            composition[element] = composition.get(element, 0) + amount
    return composition or None


def observed_outcome(observation):
    """Classify the exposed stability flag, without inferring a physical cause."""
    stable = observation.get("is_stable")
    if stable is True:
        return (
            "stable",
            "Stable within the observed phase-diagram tolerance at evaluation",
        )
    if stable is False:
        return (
            "unstable",
            "Unstable relative to the observed phase-diagram tolerance at evaluation",
        )
    return "unknown", "No observed stability flag supplied"
