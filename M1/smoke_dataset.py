"""Tiny local-only dataset for exercising the official MADE runner end to end."""

from pymatgen.analysis.phase_diagram import PDEntry, PhaseDiagram
from pymatgen.core.composition import Composition
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure

from made.data.chemical_system import PhaseDiagramDataset


class SmokeDataset(PhaseDiagramDataset):
    """Synthetic Li-O phase diagram; not for benchmark metrics or reporting."""

    def __init__(
        self, elements: list[str], thermo_types: list[str] | None = None
    ) -> None:
        if set(elements) != {"Li", "O"}:
            raise ValueError("SmokeDataset only supports the synthetic Li-O system")

        self.elements = list(elements)
        self.thermo_types = thermo_types or []
        elemental_entries = []
        for element in self.elements:
            structure = Structure(
                Lattice.cubic(3.0), [element], [[0.0, 0.0, 0.0]]
            )
            elemental_entries.append(
                PDEntry(
                    structure.composition,
                    0.0,
                    attribute={"structure": structure.as_dict()},
                )
            )

        compound = Structure(
            Lattice.cubic(3.2),
            ["Li", "O"],
            [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
        )
        entries = elemental_entries + [
            PDEntry(
                Composition("LiO"),
                -1.0,
                attribute={"structure": compound.as_dict()},
            )
        ]
        self.dataset = PhaseDiagram(entries)
        self._ground_truth_pd = self.dataset
