# White-Box Flow Graph: `check_image_quality`

The pipeline's gatekeeper is `src/pipeline.py::check_image_quality`. Its
control-flow graph and the independent paths covered by the test suite are
documented here so a reviewer can map tests back to logic in one glance.

## Flow graph

```
              ┌─────────────┐
              │ 1: imread() │
              └──────┬──────┘
                     │ image is None?
            ┌────────┴────────┐
        yes │                 │ no
            ▼                 ▼
     ┌──────────────┐  ┌────────────────────┐
     │ 2: Corrupted │  │ 3: blur < THRESHOLD│
     └──────────────┘  └─────────┬──────────┘
                                 │
                       ┌─────────┴─────────┐
                   yes │                   │ no
                       ▼                   ▼
                ┌──────────────┐  ┌─────────────────────┐
                │ 4: Blurry    │  │ 5: brightness in    │
                └──────────────┘  │    [LOW, HIGH]?     │
                                  └─────────┬───────────┘
                                            │
                                  ┌─────────┴─────────┐
                              out │                   │ in
                                  ▼                   ▼
                       ┌────────────────────┐  ┌──────────────────────┐
                       │ 6: Poorly Exposed  │  │ 7: Ready for Training│
                       └────────────────────┘  └──────────────────────┘
```

## Cyclomatic complexity

3 binary decisions ⇒ V(G) = 3 + 1 = **4 independent paths**.

## Path coverage matrix

| Path | Route          | Input fixture            | Test                                          |
|------|----------------|--------------------------|-----------------------------------------------|
| P1   | 1 → 2          | `corrupted_image_path`   | `test_path_1_corrupted_file_is_flagged`       |
| P1'  | 1 → 2          | missing file             | `test_path_1_missing_file_is_flagged`         |
| P2   | 1 → 3 → 4      | `blurry_image_path`      | `test_path_2_blurry_image_is_flagged`         |
| P3   | 1 → 3 → 5 → 6  | `dark_image_path`        | `test_path_3_dark_image_is_flagged`           |
| P4   | 1 → 3 → 5 → 7  | `sharp_image_path`       | `test_path_4_sharp_image_passes`              |

Every edge in the graph is exercised, satisfying basis-path coverage.
