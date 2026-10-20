"""Bootstrap entrypoint for the MW4 trainer."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.core.pipeline import TrainerPipeline
from src.core.attach import GameAttacher
from src.offsets.resolver import OffsetResolver
from src.utils.logger import setup_logging


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mw4-trainer", description="Call of Duty: Modern Warfare 4 Trainer")
    p.add_argument("--no-overlay", action="store_true", help="disable the ESP overlay")
    p.add_argument("--profile", default="default", help="config profile name")
    p.add_argument("--dry-run", action="store_true", help="resolve offsets but do not write memory")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(verbose=args.verbose)
    log = logging.getLogger("mw4.trainer")

    attacher = GameAttacher(process_name="ModernWarfare4.exe")
    if not attacher.wait_for_game(timeout=30):
        log.error("MW4 process not found within timeout")
        return 2

    resolver = OffsetResolver.build_for_current_build(attacher.build_id)
    log.info("resolved %d offsets for build %s", len(resolver.table), attacher.build_id)

    pipeline = TrainerPipeline(
        attacher=attacher,
        resolver=resolver,
        profile=args.profile,
        overlay=not args.no_overlay,
        dry_run=args.dry_run,
    )
    try:
        pipeline.run_forever()
    except KeyboardInterrupt:
        log.info("shutdown requested")
    finally:
        pipeline.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())