# Cosmos Integration

Integration specification for NVIDIA Cosmos world foundation models within the Physical AI Toolchain SDG pipeline.

## Status

Partially implemented. The end-to-end CARLA capture, conditioning, and Cosmos
Transfer 2.5 pipeline is available in
[`AVOPS/carla-cosmos/`](../../AVOPS/carla-cosmos/README.md). Cosmos Predict and
Cosmos Reason integrations remain planned.

## Models

| Model           | Version | Purpose                              |
|-----------------|---------|--------------------------------------|
| Cosmos Transfer | 2.5     | Sim-to-real image style transfer     |
| Cosmos Predict  | 2.5     | Future frame generation              |
| Cosmos Reason   | 2       | Data quality assessment and curation |

## Container Images

| Model               | Registry                                               | Image                | Tag     |
|---------------------|--------------------------------------------------------|----------------------|---------|
| Cosmos Transfer 2.5 | Built locally from NVIDIA's official source repository | `cosmos-transfer2.5` | `local` |
| Cosmos Predict 2.5  | nvcr.io                                                | TBD                  | TBD     |
| Cosmos Reason 2     | nvcr.io                                                | TBD                  | TBD     |

CARLA simulation uses the official `carlasim/carla:0.9.15` image. The task
runner and CARLA-specific pipeline code are layered onto the Cosmos
Transfer image; upstream Cosmos and ScenarioRunner code are fetched during
image builds rather than vendored into this repository.

## Environment Variables

All Cosmos containers require:

| Variable                     | Value | Description                |
|------------------------------|-------|----------------------------|
| `ACCEPT_EULA`                | `Y`   | NVIDIA EULA acceptance     |
| `PRIVACY_CONSENT`            | `Y`   | NVIDIA privacy consent     |
| `NVIDIA_DRIVER_CAPABILITIES` | `all` | Full GPU capability access |

## Integration Patterns

### OSMO Workflows

Cosmos workflows use OSMO dataset injection for input/output data. Workflow YAML uses Jinja templates (`{{ }}`) for parameterization.

### AzureML Jobs

Cosmos jobs use the `commandJob` schema with GPU instance types. Code snapshots and model artifacts follow the standard AzureML patterns.

## External References

| Resource               | URL                                            |
|------------------------|------------------------------------------------|
| NVIDIA Cosmos Platform | <https://developer.nvidia.com/cosmos>          |
| Cosmos Transfer 2.5    | <https://github.com/NVIDIA/Cosmos-Transfer2.5> |
| Cosmos Predict 2.5     | <https://github.com/NVIDIA/Cosmos-Predict2.5>  |
| Cosmos Cookbook        | <https://github.com/NVIDIA/Cosmos-Cookbook>    |
