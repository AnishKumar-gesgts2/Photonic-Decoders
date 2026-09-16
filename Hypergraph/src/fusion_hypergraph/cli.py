from __future__ import annotations

import argparse
from pathlib import Path

from .analyze import process_results
from .config import load_config
from .data import generate_data
from .experiment import run_benchmark
from .plotting import make_plots


def main() -> None:
    parser = argparse.ArgumentParser(description="Fusion-hypergraph decoder benchmark")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate deterministic data shards")
    _config_argument(generate)
    generate.add_argument("--output", type=Path, required=True)

    run = subparsers.add_parser("run", help="Decode all generated shots")
    _config_argument(run)
    run.add_argument("--data", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=1)

    analyze = subparsers.add_parser("analyze", help="Compute confidence intervals and paired Δinfo")
    analyze.add_argument("--results", type=Path, required=True)
    analyze.add_argument("--bootstrap-samples", type=int, default=4000)

    plot = subparsers.add_parser("plot", help="Render publication-oriented figures")
    plot.add_argument("--summary", type=Path, required=True)
    plot.add_argument("--output", type=Path, required=True)

    all_steps = subparsers.add_parser("all", help="Run generate, decode, analyze, and plot")
    _config_argument(all_steps)
    all_steps.add_argument("--workdir", type=Path, required=True)
    all_steps.add_argument("--workers", type=int, default=1)

    args = parser.parse_args()
    if args.command == "generate":
        generate_data(load_config(args.config), args.output)
    elif args.command == "run":
        run_benchmark(load_config(args.config), args.data, args.output, workers=args.workers)
    elif args.command == "analyze":
        process_results(args.results, bootstrap_samples=args.bootstrap_samples)
    elif args.command == "plot":
        make_plots(args.summary, args.output)
    elif args.command == "all":
        config = load_config(args.config)
        data_dir = args.workdir / "data"
        result_dir = args.workdir / "results"
        generate_data(config, data_dir)
        run_benchmark(config, data_dir, result_dir, workers=args.workers)
        summary = process_results(result_dir)
        make_plots(summary, args.workdir / "figures")


def _config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, required=True)


if __name__ == "__main__":
    main()
