# Partial audit: nine distinct dev baseline units

Seven new Random artifact ZIPs from run 39286848821 were downloaded and matched against their GitHub SHA256 digests. The two previously verified original units were imported by checksum. No experiment was rerun for this audit.

The original raw JSON snapshot hash rejected aggregation because derived pymatgen lattice scalars and Cartesian coordinates differ by at most 4.2633e-14 between CPUs. All independent reference data (energies, compositions, matrices, fractional positions, species and properties) match exactly. The initial failed `report/validation.json` remains unchanged.

The M2-only fix hashes exact independent data, without numeric rounding; regression tests require even 1e-14 changes to energy, matrix or fractional coordinates to remain detectable. Official metrics, evaluator source, oracle, runner and scientific configuration are unchanged. `report-canonical/` successfully validates nine units with zero issues and 27 missing baseline units. It contains per-unit official mSUN@B, AUDC, curves and recorded costs. Only the original Mg-Sn-Sr seed17 pair has both methods; no complete baseline method comparison is claimed.

Original ZIP IDs and digests are in artifact_manifest.json. An evidence-only GitHub workflow will preserve their exact bytes on main/M2 along with the failed batch256 recovery ZIPs, independently of scoring success. Copies in different evidence folders are the same units and must not be counted twice.
