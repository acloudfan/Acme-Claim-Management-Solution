# AI-Powered Auto Insurance Claims System

Build a prototype/demo for showing a customer how auto claims can be streamlined using AI for damage detection and repair estimation.

## Quick Start

See **[Quick Start Guide](specifications/QUICK-START-UV.md)** for complete setup instructions.

### 30-Second Setup

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup and run
./scripts/setup_uv.sh && ./scripts/start_api.sh
```

Access API at: http://localhost:8000/docs

## Documentation

- **[Quick Start](specifications/QUICK-START-UV.md)** - Get up and running fast
- **[API Documentation](specifications/README-API.md)** - Complete API reference
- **[Implementation Summary](specifications/API-IMPLEMENTATION-SUMMARY.md)** - What's been built
- **[Design Specification](specifications/API-BACKEND-DESIGN.md)** - Architecture details
- **[Project Overview](CLAUDE.md)** - High-level project context

## Project Structure

- `src/api/` - FastAPI backend (37 files, ~3,500 LOC)
- `expts/` - YOLO experiments and model training
- `repos/` - Reference implementation (Streamlit app)
- `scripts/` - Setup and utility scripts
- `specifications/` - Documentation and design docs

## Setup

### Backend API (FastAPI)
```bash
./scripts/setup_uv.sh  # One-time setup
make run               # Start API server
```

### Experiments (YOLO)
```bash
cd expts
python -m venv .venv
source .venv/bin/activate
pip install ultralytics gdown huggingface_hub
python main.py
```

### Reference App (Streamlit)
```bash
cd repos/Car-Damage-Assessment-AI
docker-compose up --build
```

## Development Tools

Claude Code extensions:
```bash
/plugin install frontend-design@claude-plugins-official
```

# References

* Car-Damage-Assessment-AI

https://github.com/artemxdata/Car-Damage-Assessment-AI

* Repair cost estimation

https://www.aaa.com/autorepair/articles/average-mechanic-labor-rate-repair-costs-in-your-state-2026

* Car damage images dataset

https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset

* Open data annotation platform (CVAT)

https://www.cvat.ai/?ref=blog.paperspace.com

* YOLO v8 training tutorial

https://www.digitalocean.com/community/tutorials/yolov8


* Interesting report

https://dl.acm.org/doi/fullHtml/10.1145/3627631.3627662

![severity detection](expts/images/report-severity-detection.jpg)