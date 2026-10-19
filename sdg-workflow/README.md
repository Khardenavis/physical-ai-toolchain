# Cosmos Data Factory

This feature provides scripts for operating the external Cosmos Data Factory (CDF) Synthetic Data Generation (SDG) workflow on a Kubernetes GPU cluster. The scripts configure and manage the workflow without vendoring or modifying its repository.

## 🚀 Quick Start

### Prerequisites

Install the following tools and configure access to a Kubernetes cluster with GPU capacity:

| Requirement | Purpose |
|---|---|
| Docker | Build and push the Airflow controller image |
| `kubectl` | Access the Kubernetes cluster |
| Helm | Install workflow components |
| `make` | Run targets in the external SDG workflow repository |
| Python 3.11+ | Run workflow integration utilities |
| `curl` | Call the Airflow REST API |
| Kubeconfig | Authenticate to the target cluster |
| `NGC_API_KEY` and `HF_TOKEN` | Retrieve required container images and model artifacts |

The cluster needs a GPU node for GPU workloads. Preflight warns if Kubernetes reports no allocatable NVIDIA GPUs.

### Configure and Install

From the repository root, configure the external SDG workflow checkout and cluster credentials:

```bash
cp sdg-workflow/configs/sdg.env.example sdg-workflow/configs/sdg.env
```

Edit `sdg-workflow/configs/sdg.env` and set `SDG_WORKFLOW_DIR`, `KUBECONFIG`, `NGC_API_KEY`, and `HF_TOKEN`. The external checkout must contain a `Makefile` and `scripts/setup_airflow_secrets.sh`.

Then run:

```bash
sdg-workflow/scripts/sdg.sh preflight
sdg-workflow/scripts/sdg.sh --dry-run run
sdg-workflow/scripts/sdg.sh run
sdg-workflow/scripts/sdg.sh port-forward
```

The Airflow UI is available at <http://localhost:8080> while port forwarding is active. `--dry-run` prints the external `make` commands without executing them. It still validates the environment and required configuration.

## ⚙️ Configuration

`sdg-workflow/configs/sdg.env.example` lists the supported settings. Copy it to `sdg-workflow/configs/sdg.env`; the local file is excluded from Git.

| Setting | Required | Purpose |
|---|---:|---|
| `SDG_WORKFLOW_DIR` | Yes | Absolute path to the external SDG workflow checkout |
| `KUBECONFIG` | Yes | Path to the kubeconfig file for the target cluster |
| `NGC_API_KEY` | Yes | NVIDIA NGC authentication |
| `HF_TOKEN` | Yes | Hugging Face model-download authentication |
| `OSMO_TOKEN`, `VLM_API_KEY`, `LLM_API_KEY` | No | Optional workflow service credentials |
| `AWS_S3_BUCKET`, `AWS_S3_REGION`, `AWS_S3_ACCESS_KEY_ID`, `AWS_S3_SECRET_ACCESS_KEY` | No | Optional S3 storage settings |
| `AIRFLOW_IMAGE_REPOSITORY`, `AIRFLOW_IMAGE_TAG` | No | Airflow controller image overrides |
| `NFS_NAMESPACE`, `NFS_STORAGE_CLASS`, `NFS_EXPORT_PATH`, `NFS_NODE_HOSTNAME`, `NFS_SERVER` | No | NFS storage settings |
| `AIRFLOW_URL` | No | Airflow REST API URL; defaults to `http://localhost:8080` |
| `AIRFLOW_USERNAME`, `AIRFLOW_PASSWORD` | No | Airflow REST API credentials |
| `SDG_DAG_ID` | No | DAG to trigger; defaults to `autonomous_vehicle_dataset_generation_dag_k8s` |
| `ODD_IMAGE`, `ODD_VLM_URL`, `ODD_VLM_MODEL`, `ODD_THRESHOLD`, `ODD_MOCK_VLM` | No | ODD container image, VLM endpoint and model, gap threshold, and offline mock perception |
| `ODD_MAX_RUNS` | No | Cap on generation runs started from ODD gaps; empty or `0` means no cap |
| `CARLA_COSMOS_VIEWS`, `COSMOS_GPU_IDS`, `CARLA_GPU_ID` | No | CARLA backend camera views, Cosmos GPUs, and CARLA's GPU |
| `SDG_POLL_INTERVAL`, `SDG_RUN_TIMEOUT` | No | Seconds between DagRun state polls and the maximum wait per run |

Values exported in the shell take precedence over values in `sdg.env`. The loader reads simple `NAME=value` lines; keep secrets and environment-specific values out of tracked files.

## 🧭 Commands

Run `sdg-workflow/scripts/sdg.sh --help` to display the available commands.

| Command | Action |
|---|---|
| `preflight` | Check required tools, credentials, kubeconfig, and cluster access |
| `setup` | Run preflight, then generate Helm secret values in the external repository |
| `nfs` | Install the host NFS export and Kubernetes StorageClass |
| `build` | Build and push the Airflow controller image |
| `install` | Install or upgrade the SDG controller |
| `run` | Run preflight, setup, NFS installation, image build, and controller installation in order |
| `port-forward` | Forward the Airflow UI to `http://localhost:8080` |
| `trigger <payload>` | Submit a JSON payload to the configured Airflow DAG |
| `odd-build` | Build the ODD gap-analysis image from `workflows/ODD` |
| `odd <in> <out>` | Run the ODD container on a directory of videos |
| `pipeline <payload>` | Run curation, ODD gap analysis, then generation (one run per gap); `--backend carla` generates with CARLA + Cosmos Transfer multi-view instead of the DAG |
| `carla <odd-dir> [out-dir]` | Generate from an existing ODD output with CARLA + Cosmos Transfer 2.5 multi-view |
| `uninstall` | Uninstall the controller |

Individual installation steps can be run separately when needed. For example:

```bash
sdg-workflow/scripts/sdg.sh setup
sdg-workflow/scripts/sdg.sh nfs
sdg-workflow/scripts/sdg.sh build
sdg-workflow/scripts/sdg.sh install
```

## ▶️ Trigger a Dataset Generation Run

Start port forwarding in one terminal:

```bash
sdg-workflow/scripts/sdg.sh port-forward
```

In another terminal, trigger a payload from the external SDG workflow repository:

```bash
sdg-workflow/scripts/sdg.sh trigger payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-real-retrieval.json
```

Payload paths can be absolute or relative to the external repository. The script submits the payload as the `payload` field in the DAG run configuration. Use `--dry-run` to print the REST request without submitting it:

```bash
sdg-workflow/scripts/sdg.sh --dry-run trigger payloads/dev/autonomous_vehicle_dataset_generation_dag/cdf-avdg-real-retrieval.json
```

The trigger command obtains a bearer token from the Airflow authentication endpoint, then posts the run to the configured DAG. Set `AIRFLOW_URL`, `AIRFLOW_USERNAME`, `AIRFLOW_PASSWORD`, and `SDG_DAG_ID` in the environment or `sdg.env` as required by the deployment.

## 🔍 ODD Gap Analysis Between Curation and Generation

The SDG DAG runs curation, Cosmos Dataset Search retrieval, and generation as one run. The ODD (Operational Design Domain) step is spliced in from this feature without changing the external repository: `sdg.sh pipeline` runs the DAG twice around the [`workflows/ODD`](../workflows/ODD/README.md) container.

```text
sdg.sh pipeline <payload>
├── 1. curation    DAG run with search_mode "none" and generation disabled
├── 2. ODD         workflows/ODD container on <output_directory>/<run_id>/split/clips
│                  writes the gap report to <output_directory>/<run_id>/odd/
└── 3. generation  one DAG run per ODD gap
                   query_video = ODD base clip, cosmos.prompt = ODD paragraph
```

```bash
sdg-workflow/scripts/sdg.sh --dry-run pipeline <payload.json>   # show the stages
sdg-workflow/scripts/sdg.sh pipeline <payload.json>             # curation -> ODD -> generation
sdg-workflow/scripts/sdg.sh odd-build                           # rebuild the ODD image after changing workflows/ODD
sdg-workflow/scripts/sdg.sh odd <videos-dir> <output-dir>       # run only the ODD container
```

The ODD container runs with host networking and reaches the VLM at `ODD_VLM_URL` (default `http://localhost:8010/v1`, model `ODD_VLM_MODEL`). It builds the image on first use. Set `ODD_MOCK_VLM=1` to use heuristic perception when no VLM endpoint is available.

For every `weatherType` and `timeOfDay` gap in `wfm_generation_input.json`, the pipeline triggers a generation run with the ODD base clip as `query_video`, `search_mode: embedding`, and `cosmos.enabled: true`. `cosmos.prompt` is the single paragraph the ODD module wrote for that scene variation in `generation_prompts.json`: the VLM summarizes the variation's attributes, with a deterministic template when the endpoint is offline. If that file is missing, the fixed sentences in `sdg-workflow/configs/odd-prompts.json` are used, and gap values without a template are skipped. Gaps for any other attribute (road, traffic, agents) are not generated by the DAG backend; the CARLA backend covers those. The remaining payload fields, such as `cosmos` settings and `top_k`, are inherited from the payload you pass in.

Constraints:

* `output_directory` must be a local path because the ODD container reads the curated clips from disk.
* Each generation run repeats curation on `input_video_path`; set `limit` in the payload to keep that cheap, and `ODD_MAX_RUNS` to bound the number of runs.
* Cosmos-Reason models are gated on Hugging Face; `ODD_VLM_MODEL` must be one your `HF_TOKEN` can access.

### CARLA backend: ODD gap, CARLA, Cosmos Transfer 2.5 multi-view

`--backend carla` replaces stage 3 (the per-gap DAG runs) with the [`workflows/carla-cosmos`](../workflows/carla-cosmos/README.md) pipeline. The ODD stage and everything before it are unchanged.

```bash
sdg-workflow/scripts/sdg.sh --backend carla pipeline <payload.json>   # curation -> ODD -> CARLA + Cosmos
sdg-workflow/scripts/sdg.sh carla <odd-output-dir> [out-dir]          # only the CARLA stage, from an ODD output
sdg-workflow/scripts/sdg.sh --dry-run --backend carla pipeline <payload.json>
```

For the CARLA stage, `sdg.sh`:

1. Validates the plan: the camera views fit the Cosmos GPUs, and at least one ODD gap maps to a CARLA scenario.
2. Stages `wfm_generation_input.json` in the pipeline's data directory.
3. Runs `run_pipeline.py`, which starts CARLA with Docker Compose, runs every scenario in the pipeline container through CARLA capture and Cosmos Transfer multi-view inference, and stops both containers afterwards.
4. Copies each finished task to `<output_directory>/<run_id>/carla/` (`multiview_grid.mp4`, `caption.txt`, `metadata.json`, `carla_simulation/`, `cosmos_synthesized/`) and writes `carla_results.json`. The command fails if any task did not finish, but keeps the tasks that did.

**Views and GPUs.** The default rig skips the narrow-FOV `front_tele` camera, leaving `front_wide`, `cross_left`, `cross_right`, `rear_left`, `rear_right`, and `rear`. This does not reduce the Cosmos GPU count: multi-view inference encodes one view per GPU rank, so the rank count must be at least the view count, and its attention splits the 2B model's 16 heads across ranks, so the rank count must divide 16. That gives 4 GPUs for up to four views and 8 GPUs for five to eight; 6 is not valid. With the defaults:

| GPUs | Used by |
|---|---|
| 0-7 | Cosmos Transfer multi-view (`COSMOS_GPU_IDS`), about 42 GB each in a six-view run |
| 7 | Also CARLA (`CARLA_GPU_ID`, about 6 GB); GPU 0 can also hold the ODD VLM (about 17 GB) |

To use fewer GPUs, run four views (for example `CARLA_COSMOS_VIEWS=front_wide,cross_left,cross_right,rear`) with four `COSMOS_GPU_IDS`. The plan check rejects a view and GPU count that do not match.

Constraints:

* CARLA scenarios exist only for road width, traffic-light direction, road surface, lane change, cut-in, and pedestrian gaps. Other gaps, such as `weatherType` and `timeOfDay`, are listed and skipped; the stage fails if nothing maps.
* The CARLA images are built locally on first use (`workflows/carla-cosmos/build-cosmos-image.sh`), which downloads about 7 GB of CARLA maps and needs `HF_TOKEN` for the gated Cosmos checkpoint.
* Prompts come from the CARLA pipeline's own prompt files, not the ODD paragraphs.
* Files under `workflows/carla-cosmos/data/runs/<run_id>/` are written by the container as root.

## 🏗️ Architecture

The CDF scripts are a thin operator interface to the external SDG workflow repository:

```text
Cosmos Data Factory
└── sdg-workflow/scripts/sdg.sh
    ├── validates local tools, credentials, and cluster access
    ├── invokes Makefile targets in the external SDG workflow checkout
    ├── submits DAG runs to the Airflow REST API
    ├── runs the workflows/ODD container between curation and generation
    └── optionally generates with workflows/carla-cosmos (CARLA + Cosmos Transfer multi-view)
```

The external repository owns the Airflow DAGs, Kubernetes deployment, curation and generation stages, and payload definitions. CDF supplies the checkout path and deployment configuration; it does not copy or patch the external repository.

## 🔐 Security

Keep `sdg.env`, kubeconfig files, API keys, and storage credentials out of source control. Use environment variables or the Git-ignored local configuration file for deployment-specific values. Protect credentials with the access controls required by the target environment.
