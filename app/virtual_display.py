import os
import time
import shutil
import logging
import subprocess

log = logging.getLogger(__name__)

procs = []


def _ensure_openbox_config():
    try:
        config_dir = os.path.expanduser("~/.config/openbox")
        os.makedirs(config_dir, exist_ok=True)
        rc_xml = os.path.join(config_dir, "rc.xml")
        content = """<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <applications>
    <application class="*">
      <decor>no</decor>
      <maximized>yes</maximized>
      <position force="yes"><x>0</x><y>0</y></position>
    </application>
  </applications>
</openbox_config>"""
        with open(rc_xml, "w") as f:
            f.write(content)
    except Exception as e:
        log.warning("Could not write openbox config: %s", e)


def start_display(display: str = ":99", width: int = 1920, height: int = 1080):
    global procs
    if is_display_running():
        return
    os.environ["DISPLAY"] = display
    log.info("Starting virtual display %s (%dx%d)", display, width, height)

    _ensure_openbox_config()

    if shutil.which("Xvfb"):
        p_xvfb = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", f"{width}x{height}x24", "-ac", "+extension", "RANDR"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p_xvfb)
        time.sleep(1)

    if shutil.which("openbox"):
        env = os.environ.copy()
        env["DISPLAY"] = display
        p_wm = subprocess.Popen(
            ["openbox"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p_wm)

    if shutil.which("x11vnc"):
        p_vnc = subprocess.Popen(
            ["x11vnc", "-display", display, "-rfbport", "5900", "-shared", "-forever", "-nopw", "-wait", "50"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p_vnc)
        time.sleep(1)


def stop_display():
    global procs
    for p in reversed(procs):
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    procs.clear()


def is_display_running() -> bool:
    global procs
    return bool(procs and any(p.poll() is None for p in procs))
