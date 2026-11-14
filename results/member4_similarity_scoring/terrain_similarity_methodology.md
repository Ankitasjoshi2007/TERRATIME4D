# TERRATIME4D — Member 4 Terrain Comparison

## Slope difference method

Each Earth candidate is matched to the Moon and Mars reference latitude
band containing its latitude.

For each comparison:

- Mean slope difference = absolute difference between the two mean slopes.
- P90 slope difference = absolute difference between the two 90th-percentile slopes.
- Combined slope difference = arithmetic mean of those two differences.

All differences are expressed in degrees. Candidates are ranked separately
for the Moon and Mars, with the smallest difference ranked first.

## Scientific limitations

- This is a descriptive slope comparison, not a mission-suitability score.
- Planetary values are latitude-band averages, not exact local-site measurements.
- Earth and planetary datasets have different spatial resolutions and
  processing histories.
- Roughness is excluded because the available measurements use incompatible
  spatial scales.
- Elevation is excluded because the available elevation datums are not
  directly comparable.
- The two slope statistics receive equal weight as an initial descriptive
  comparison, not as a calibrated scientific weighting.
- These results do not establish physical equivalence between Earth and
  lunar or Martian environments.

A future mission-specific score requires validated criteria and weights.
