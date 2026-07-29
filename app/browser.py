"""
Camoufox browser launcher with extension loading and profile management.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
import sys
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple, Any

from camoufox.async_api import AsyncCamoufox

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
EXTENSIONS_DIR = Path(
    os.getenv("EXTENSIONS_DIR", str(BASE_DIR / "extensions" / "plugins"))
)
UNPACKED_EXTENSIONS_DIR = Path(
    os.getenv(
        "UNPACKED_EXTENSIONS_DIR", str(BASE_DIR / "data" / "unpacked_extensions")
    )
)
PROFILE_BASE_DIR = Path(
    os.getenv("PROFILE_BASE_DIR", str(BASE_DIR / "data" / "profiles"))
)
BROWSER_NAVIGATION_TIMEOUT_MS = int(
    os.getenv("BROWSER_NAVIGATION_TIMEOUT_MS", "60000")
)

_SKIP_DIR_NAMES = frozenset({"scripts", "__pycache__", ".git"})

_browser_proc: Optional[subprocess.Popen] = None


def ensure_extensions_unzipped(
    extensions_dir: Optional[Path] = None,
    unpacked_dir: Optional[Path] = None,
) -> Path:
    """
    Find and unzip any .zip files from extensions/plugins/ into the runtime unpacked directory.
    Returns the path to the directory containing unpacked extensions.
    """
    src_root = Path(extensions_dir) if extensions_dir else Path(EXTENSIONS_DIR)
    target_root = Path(unpacked_dir) if unpacked_dir else Path(UNPACKED_EXTENSIONS_DIR)
    target_root.mkdir(parents=True, exist_ok=True)

    if not src_root.is_dir():
        log.debug("Extensions source directory does not exist: %s", src_root)
        return target_root

    for item in sorted(src_root.iterdir()):
        if item.is_file() and item.suffix == ".zip":
            target_name = item.stem
            target_dir = target_root / target_name

            if not target_dir.is_dir() or not any(target_dir.iterdir()):
                log.info("Extracting extension zip %s to %s", item.name, target_dir)
                with zipfile.ZipFile(item, "r") as zip_ref:
                    zip_ref.extractall(target_root)
                log.info("Successfully extracted %s", item.name)
            else:
                log.debug("Extension %s already extracted at %s", item.name, target_dir)

    return target_root


def run_extension_prelaunch_scripts(extensions_dir: Optional[Path] = None) -> None:
    """Run any `.py` scripts under extensions/scripts/ before launch."""
    root = Path(extensions_dir) if extensions_dir else Path(EXTENSIONS_DIR)
    scripts_dir = root.parent / "scripts"
    if not scripts_dir.is_dir():
        return
    for script in sorted(scripts_dir.iterdir()):
        if script.is_file() and script.suffix == ".py":
            log.info("Running pre-launch extension script: %s", script.name)
            subprocess.run(
                [sys.executable, str(script)],
                check=True,
                cwd=str(scripts_dir),
            )


def discover_extension_paths(unpacked_dir: Optional[Path] = None) -> List[Path]:
    """Scan unpacked extensions dir for Firefox extensions (manifest.json)."""
    root = Path(unpacked_dir) if unpacked_dir else Path(UNPACKED_EXTENSIONS_DIR)
    if not root.is_dir():
        log.warning("Unpacked extensions directory does not exist: %s", root)
        return []

    found: List[Path] = []
    seen: set[str] = set()
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in _SKIP_DIR_NAMES or child.name.startswith("."):
            continue
        resolved = child.resolve()
        if not (resolved / "manifest.json").is_file():
            continue
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        found.append(resolved)

    if found:
        log.info(
            "Discovered %d extension(s): %s",
            len(found),
            ", ".join(p.name for p in found),
        )
    else:
        log.info("No extensions found under %s", root)
    return found


def _profile_slug(label: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", (label or "default").strip().lower())
    return slug[:120] or "default"


@asynccontextmanager
async def launch_browser_context(
    *,
    profile_label: str = "default",
    profile_base: Optional[Path] = None,
    extensions_dir: Optional[Path] = None,
    ephemeral: bool = False,
) -> AsyncGenerator[Tuple[Any, Any, Any], None]:
    """
    Launch an isolated Camoufox persistent context with all extensions.
    Yields (None, context, page).
    """
    ext_dir = Path(extensions_dir) if extensions_dir else Path(EXTENSIONS_DIR)
    unpacked_target = ensure_extensions_unzipped(ext_dir)
    run_extension_prelaunch_scripts(ext_dir)
    extension_paths = discover_extension_paths(unpacked_target)

    base = Path(profile_base or PROFILE_BASE_DIR)
    base.mkdir(parents=True, exist_ok=True)

    if ephemeral:
        import tempfile
        profile_dir = Path(tempfile.mkdtemp(prefix="ephemeral_", dir=str(base)))
    else:
        profile_dir = base / f"profile_{_profile_slug(profile_label)}"
    profile_dir.mkdir(parents=True, exist_ok=True)

    addons = [str(p) for p in extension_paths] if extension_paths else None

    async with AsyncCamoufox(
        headless=False,
        persistent_context=True,
        user_data_dir=str(profile_dir),
        addons=addons,
    ) as context:
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(BROWSER_NAVIGATION_TIMEOUT_MS)
        log.info(
            "Camoufox launched (profile=%s extensions=%d)",
            profile_dir,
            len(extension_paths),
        )
        yield None, context, page


async def run_interactive_instance(profile_label: str = "interactive") -> None:
    """Entry point to start the headful browser instance and keep it active."""
    display = os.getenv("DISPLAY", ":99")
    log.info("Launching headful Camoufox browser on display %s...", display)
    async with launch_browser_context(profile_label=profile_label) as (_, context, page):
        log.info("Navigating initial tab to about:blank")
        await page.goto("about:blank")
        log.info("Camoufox headful instance is active and ready.")
        while True:
            await asyncio.sleep(1)


def is_instance_running() -> bool:
    global _browser_proc
    from app.virtual_display import is_display_running
    return bool(_browser_proc and _browser_proc.poll() is None and is_display_running())


def start_instance() -> dict:
    global _browser_proc
    if is_instance_running():
        return {"status": "running"}

    from app.virtual_display import start_display
    start_display()

    env = os.environ.copy()
    env["DISPLAY"] = os.getenv("DISPLAY", ":99")
    _browser_proc = subprocess.Popen([sys.executable, "-m", "app.browser"], env=env)
    return {"status": "running"}


def stop_instance() -> dict:
    global _browser_proc
    if _browser_proc:
        try:
            _browser_proc.terminate()
            _browser_proc.wait(timeout=3)
        except Exception:
            try:
                _browser_proc.kill()
            except Exception:
                pass
        _browser_proc = None

    from app.virtual_display import stop_display
    stop_display()
    return {"status": "stopped"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_interactive_instance())
    except (KeyboardInterrupt, SystemExit):
        log.info("Camoufox interactive browser exiting.")
