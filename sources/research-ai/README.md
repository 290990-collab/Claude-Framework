# CVCS · AI-Assisted Interior Design

Floor-plan **retrieval** (and, later, generation) for AI-assisted interior design.
Given a floor plan, the system retrieves the most similar layouts from **RPLAN** — including from **partial / incomplete** plans, to mirror real design workflows where the input is a sketch.

> **Status — Phase 1 (Retrieval).** Both branches implemented, trained and benchmarked on the same 2000 test queries. Vision: 5 interchangeable frozen encoders (+ optional projection head for partial queries). Graph: three GNN encoders trained with InfoNCE, beating the training-free baseline on topology. Late fusion is the next step.

---

## Approach

Two complementary retrieval pipelines, separate FAISS indices, late score-level fusion.

| Branch | Pipeline | Captures | Status |
|--------|----------|----------|--------|
| **Vision** | image → frozen vision encoder → PCA whitening → FAISS `IndexFlatIP` | visual & geometric similarity | ✅ implemented |
| **Graph**  | RPLAN `.mat` → room graph → GNN encoder (GCN/GAT/GraphSAGE, InfoNCE) → FAISS | topological & semantic relations | ✅ implemented |

**Interchangeable vision encoders.** The vision backbone is pluggable through a single configuration switch: the same pipeline can run on **DINOv2, DINOv3, SigLIP2, RADIO or I-JEPA** (all frozen — no fine-tuning on the vision side). These cover complementary representation axes (two self-supervised, one vision-language, one agglomerative "mixed", one predictive/masked). Each encoder ships with its own preprocessing and pooling, and embeddings are extracted, whitened and indexed the same way regardless of backbone, so multi-encoder benchmarking is just a config change.

**Graph encoder, two stages.** A *training-free* structural descriptor first validates the pipeline as a baseline; the **final** encoder is a **trained GNN** (GCN / GAT / GraphSAGE).

**Fusion.** Scores are normalized per branch (different score scales), then combined:
`s = α·ẑ_vision + (1−α)·ẑ_graph`, with `α` tuned on validation.

```
                 ┌──────────── Floor plan (RPLAN) ────────────┐
                 │                                            │
        VISION: raster PNG                       GRAPH: RPLAN .mat
                 │  frozen encoder (swappable)     │  room graph (rooms, adjacency)
                 │  PCA whitening (fit on DB)      │  GNN encoder + PCA whitening
                 │  FAISS IndexFlatIP              │  FAISS IndexFlatIP
                 └──────────────┬─────────────────┘
                                │  late fusion (z-score, α-weighted)
                                ▼
                            Top-K results
```

## Getting started

```bash
pip install -r requirements.txt
```

The vision pipeline is config-driven: the active encoder and its preprocessing are selected from a YAML config, so switching backbone (or running the multi-encoder benchmark) needs no code changes.

```bash
# local — runs the full vision pipeline end-to-end
python -m tests.test_vision_retrieval
#   extract embeddings (gallery = query pool) → fit PCA whitening
#   → build FAISS index → query top-K

# HPC (SLURM) — numbered jobs, run in order; see COMANDI.md for dependencies
sbatch scripts/vision/01_extract_raw.sh      # vision: extract RAW embeddings
sbatch scripts/graph/03_train_gnn.sh         # graph:  train the GNN encoders
sbatch scripts/graph/04_eval_gnn.sh          # graph:  index + per-axis evaluation
```

## Evaluation

- **Per-axis relevance** derived from RPLAN `.mat` metadata — composition (room-type histogram), topology (typed adjacency), geometry (footprint shape) — evaluated against the **whole gallery**, self-match excluded. **nDCG@K** is primary; **Recall@K / mAP@K** apply to the two discrete axes.
- **Semantic** — room-type / composition match between query and retrieved.
- **Adjacency** — preservation of key room connections.
- **Partial retrieval** — degraded queries (rooms removed) to test layout completion, with a study on how much masking the system tolerates; the input is degraded consistently across branches.

## Project structure

```
src/
  data/         RPLAN .mat reader                  (shared core, used by both branches)
  evaluation/   per-axis relevance + metrics       (shared core, used by both branches)
  vision/       data/ models/ training/ evaluation/ utils/
                  models/vision_encoders/  swappable frozen backbones
                                           (DINOv2 / DINOv3 / SigLIP2 / RADIO / I-JEPA)
                  models/retrieval_model   RAW embeddings + on-the-fly head/whitening + FAISS
  graph/        graph_builder, graph_dataset, transforms, draw_graph
                  models/     GCN / GAT / GraphSAGE behind one contract
                  training/   InfoNCE self-supervised loop + graph augmentations
                  evaluation/ FAISS indexing, per-axis metrics, retrieval probe
configs/        vision_retrieval.yaml + vision_models/, graph_retrieval.yaml + graph_models/
scripts/        vision/ and graph/ — numbered sbatch jobs (see COMANDI.md)
tests/          CPU smoke tests (test_vision_retrieval.py is the indexing entry point)
embeddings/     outputs: raw embeddings, graph cache, checkpoints
results/        evaluation reports & visualizations
```

## Dataset

**RPLAN** — raster floor plans used as a single gallery that also serves as the query pool; `.mat` metadata (room types, adjacency, boundary) provides relevance labels and the exact graph for the graph branch.
**ResPlan** is excluded as a training corpus (no relevance labels, out-of-domain, taxonomy mismatch).

## Documentation

Detailed internal design notes (architecture, structure, retrieval, dataset, experiments,
conventions, current status) are kept under `.claude/shared/`; the live task state is
`.claude/TODO.md`, and the multi-agent orchestration framework is `CLAUDE.md` +
`.claude/agents/`.
