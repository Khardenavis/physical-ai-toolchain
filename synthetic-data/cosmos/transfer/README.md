# Cosmos Transfer 2.5

Sim-to-real image transformation using NVIDIA Cosmos Transfer 2.5. Converts
simulation-rendered frames from Isaac Sim or CARLA into photorealistic data for
training robot policies and autonomous-driving systems.

## Capabilities

| Capability        | Description                                                           |
|-------------------|-----------------------------------------------------------------------|
| Style transfer    | Transform simulation renders to match real-world visual distributions |
| Domain adaptation | Bridge the sim-to-real gap for visual policy training                 |
| Batch processing  | Process full episode frame sequences                                  |

## Integration Points

| Component         | Description                                              |
|-------------------|----------------------------------------------------------|
| Simulation output | Rendered frames and conditioning from Isaac Sim or CARLA |
| Training pipeline | Photorealistic frames fed to RL/IL training              |
| Cosmos Predict    | Output frames can chain to future prediction             |

The end-to-end CARLA capture, geometric conditioning, and multi-view Cosmos
workflow is implemented in
[CARLA + Cosmos Transfer](../../../AVOPS/carla-cosmos/README.md).

## References

- [Cosmos Transfer 2.5](https://github.com/NVIDIA/Cosmos-Transfer2.5)
- [NVIDIA Cosmos Platform](https://developer.nvidia.com/cosmos)
