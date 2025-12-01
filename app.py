import io
import os
import re
import shutil
import tempfile
import threading
import uuid
import zipfile
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import streamlit as st
import yt_dlp
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx


def apply_root_variables() -> str:
    return """
        :root {
            --glass-bg: rgba(15, 23, 42, 0.55);
            --glass-border: rgba(148, 163, 184, 0.35);
            --accent: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #f472b6 100%);
            --text-primary: #e2e8f0;
            --text-muted: #cbd5f5;
        }
    """


def apply_body_background() -> str:
    return """
        body {
            background: transparent;
            color: var(--text-primary);
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 15% 20%, rgba(96, 165, 250, 0.35), transparent 55%),
                        radial-gradient(circle at 85% 85%, rgba(244, 114, 182, 0.30), transparent 50%),
                        linear-gradient(135deg, #0f172a 0%, #0b1120 58%, #111827 100%);
            color: var(--text-primary);
        }

        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(30, 64, 175, 0.1));
            mix-blend-mode: screen;
            opacity: 0.45;
        }

        [data-testid="stHeader"] {
            background: transparent;
            z-index: 1;
        }
    """


def apply_hero_styles() -> str:
    return """
        .glass-hero {
            position: relative;
            margin: 0.75rem 0 1.75rem 0;
            padding: 2.75rem 3rem;
            border-radius: 32px;
            background: radial-gradient(circle at 25% -10%, rgba(96, 165, 250, 0.22), transparent 65%),
                        radial-gradient(circle at 85% 120%, rgba(236, 72, 153, 0.20), transparent 55%),
                        rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.24);
            backdrop-filter: blur(26px) saturate(120%);
            box-shadow: 0 25px 60px rgba(15, 23, 42, 0.55);
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-hero:hover {
            transform: translateY(-4px);
            box-shadow: 0 30px 70px rgba(15, 23, 42, 0.65);
            border-color: rgba(96, 165, 250, 0.4);
        }

        .glass-hero::after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            top: -140px;
            right: -120px;
            border-radius: 50%;
            background: rgba(59, 130, 246, 0.18);
            filter: blur(8px);
            animation: float 10s ease-in-out infinite;
        }
    """


def apply_card_styles() -> str:
    return """
        .glass-card {
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(94, 234, 212, 0.25);
            backdrop-filter: blur(24px) saturate(150%);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(15, 23, 42, 0.5);
            border-color: rgba(94, 234, 212, 0.4);
        }
    """


def apply_button_styles() -> str:
    return """
        button[kind="primary"], button[kind="secondary"], [data-testid="stDownloadButton"] button {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        button[kind="primary"]:hover, button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover {
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 20px rgba(96, 165, 250, 0.4) !important;
        }

        button[kind="primary"]:active, button[kind="secondary"]:active, [data-testid="stDownloadButton"] button:active {
            transform: translateY(0px) scale(0.98) !important;
        }
    """


def apply_input_styles() -> str:
    return """
        [data-testid="stTextInput"] > div > div > input {
            transition: all 0.3s ease !important;
        }

        [data-testid="stTextInput"] > div > div > input:hover {
            border-color: rgba(96, 165, 250, 0.5) !important;
            box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.3) !important;
        }

        [data-testid="stTextInput"] > div > div > input:focus {
            border-color: rgba(96, 165, 250, 0.7) !important;
            box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.4) !important;
        }
    """


def apply_expander_styles() -> str:
    return """
        [data-testid="stExpander"] {
            transition: all 0.3s ease !important;
        }

        [data-testid="stExpander"]:hover {
            transform: translateX(4px);
        }
    """


def apply_metric_styles() -> str:
    return """
        [data-testid="stMetric"] {
            transition: all 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: scale(1.05);
        }

        [data-testid="stMetricValue"] {
            color: var(--text-primary);
        }

        [data-testid="stMetricLabel"] {
            color: rgba(226, 232, 240, 0.76);
        }
    """


def apply_alert_styles() -> str:
    return """
        div[data-testid="stAlert"] p {
            color: var(--text-primary);
        }
    """


def apply_results_styles() -> str:
    return """
        .glass-results .st-expander {
            border-radius: 18px !important;
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(148, 163, 184, 0.3) !important;
        }

        .glass-results .st-expander:hover {
            border-color: rgba(129, 140, 248, 0.7) !important;
        }

        .glass-results .st-expander p {
            color: var(--text-primary);
        }

        .glass-results h3 {
            font-size: 1.35rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            margin-bottom: 1.2rem;
            color: var(--text-primary);
        }
    """


def apply_navigation_styles() -> str:
    return """
        .my-nav {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: radial-gradient(circle at 20% 50%, rgba(96, 165, 250, 0.15), transparent 70%),
                        radial-gradient(circle at 80% 50%, rgba(168, 85, 247, 0.12), transparent 70%),
                        rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(24px) saturate(140%);
            border-bottom: 1px solid rgba(148, 163, 184, 0.3);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            pointer-events: auto;
        }

        .nav-tabs {
            display: flex;
            justify-content: center;
            align-items: center;
            list-style: none;
            margin: 0;
            padding: 0.1rem 1rem;
            pointer-events: auto;
        }

        .nav-item {
            position: relative;
            display: inline-block;
            pointer-events: auto;
        }

        .nav-tab {
            padding: 0.8rem 2.5rem;
            margin: 0rem 0.5rem;
            background: transparent;
            border: none;
            color: rgba(226, 232, 240, 0.7);
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
            font-size: 0.95rem;
            text-decoration: none !important;
            letter-spacing: 0.02em;
            position: relative;
            display: inline-block;
            z-index: 10;
            pointer-events: auto;
        }

        .nav-tab::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 12px;
            background: radial-gradient(circle at 30% 40%, rgba(96, 165, 250, 0.3), transparent 70%),
                        radial-gradient(circle at 70% 60%, rgba(168, 85, 247, 0.25), transparent 70%),
                        rgba(15, 23, 42, 0.4);
            opacity: 0;
            transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            transform: scale(0.92);
            z-index: -1;
            pointer-events: none;
        }

        .nav-tab::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 50%;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, rgba(96, 165, 250, 0.8), rgba(168, 85, 247, 0.8), rgba(244, 114, 182, 0.7));
            border-radius: 2px;
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1), left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            z-index: 0;
        }

        .nav-tab:link, .nav-tab:visited, .nav-tab:hover, .nav-tab:active {
            text-decoration: none !important;
        }

        .nav-tab:hover {
            color: #ffffff !important;
            background: radial-gradient(circle at 35% 35%, rgba(96, 165, 250, 0.35), transparent 75%),
                        radial-gradient(circle at 65% 65%, rgba(168, 85, 247, 0.3), transparent 75%),
                        rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.35);
            box-shadow: 0 10px 32px rgba(96, 165, 250, 0.4),
                        0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                        0 2px 0 rgba(255, 255, 255, 0.15) inset;
            transform: translateY(-4px) scale(1.08);
            letter-spacing: 0.08em;
            border-radius: 14px;
        }

        .nav-tab:hover::before {
            opacity: 1;
            transform: scale(1);
        }

        .nav-tab:hover::after {
            width: 100%;
            left: 0%;
        }

        .nav-tab:active {
            transform: translateY(0px);
        }

        .nav-tab.disabled {
            color: rgba(226, 232, 240, 0.3);
            cursor: not-allowed;
            pointer-events: none;
            opacity: 0.5;
        }

        .nav-tab.active {
            color: #ffffff;
            background: radial-gradient(circle at 40% 40%, rgba(96, 165, 250, 0.4), transparent 80%),
                        radial-gradient(circle at 60% 60%, rgba(168, 85, 247, 0.35), transparent 80%),
                        rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(96, 165, 250, 0.5);
            border-radius: 14px;
            font-weight: 600;
            box-shadow: 0 6px 24px rgba(96, 165, 250, 0.45),
                        0 0 0 1px rgba(255, 255, 255, 0.15) inset,
                        0 2px 0 rgba(255, 255, 255, 0.2) inset;
        }

        .nav-tab.active::after {
            width: 100%;
            left: 0%;
        }

        .nav-logo {
            margin-right: 1.5rem;
            display: flex;
            align-items: center;
        }

        .nav-logo-img {
            height: 45px;
            width: auto;
            display: block;
            pointer-events: none;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }

        .nav-spacer {
            height: 30;
            pointer-events: none;
        }
    """


def apply_responsive_styles() -> str:
    return """
        @media (max-width: 768px) {
            .glass-card {
                padding: 1.6rem 1.4rem;
            }

            .glass-hero {
                padding: 2.2rem 1.75rem;
            }

            .nav-tabs {
                flex-direction: column;
            }

            .nav-tab {
                text-align: center;
            }
        }
    """


def apply_liquid_glass_theme() -> None:
    st.markdown(
        f"""
        <style>
        {apply_root_variables()}
        {apply_body_background()}
        {apply_hero_styles()}
        {apply_card_styles()}
        {apply_button_styles()}
        {apply_input_styles()}
        {apply_expander_styles()}
        {apply_metric_styles()}
        {apply_alert_styles()}
        {apply_results_styles()}
        {apply_navigation_styles()}
        {apply_responsive_styles()}
        </style>
        """,
        unsafe_allow_html=True,
    )


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", value)
    cleaned = re.sub(r"[-\s]+", "-", cleaned).strip("-_")
    return cleaned or "playlist"


def is_mix_playlist(url: str) -> bool:
    """Return True when the URL looks like an auto-generated YouTube mix."""

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if not parsed.query:
        return False

    params = parse_qs(parsed.query)
    list_id = (params.get("list") or [""])[0]
    return list_id.startswith("RD") or list_id.startswith("UL")


_FFMPEG_PATH_CACHE: Optional[str] = None


def resolve_ffmpeg_path() -> str | None:
    """Locate an FFmpeg executable, preferring bundled binaries over system ones."""

    global _FFMPEG_PATH_CACHE  # noqa: PLW0603

    if _FFMPEG_PATH_CACHE:
        return _FFMPEG_PATH_CACHE

    override = os.environ.get("FFMPEG_BINARY")
    if override:
        explicit_path = Path(override)
        if explicit_path.exists():
            _FFMPEG_PATH_CACHE = str(explicit_path)
            return _FFMPEG_PATH_CACHE
        resolved_override = shutil.which(override)
        if resolved_override:
            _FFMPEG_PATH_CACHE = resolved_override
            return _FFMPEG_PATH_CACHE

    bundled_bin = Path(__file__).resolve().parent / "deps" / "ffmpeg" / "bin"
    if bundled_bin.exists():
        current_path = os.environ.get("PATH", "")
        path_parts = current_path.split(os.pathsep) if current_path else []
        if str(bundled_bin) not in path_parts:
            os.environ["PATH"] = (
                f"{bundled_bin}{os.pathsep}{current_path}" if current_path else str(bundled_bin)
            )

    resolved = shutil.which("ffmpeg")
    if resolved:
        _FFMPEG_PATH_CACHE = resolved
    return resolved


def ensure_ffmpeg(media_format: str) -> None:
    if media_format in ("mp3", "mp4") and resolve_ffmpeg_path() is None:
        raise RuntimeError(
            "FFmpeg is required for the selected format. Provide a system install or place binaries in "
            "deps/ffmpeg/bin."
        )


def fetch_playlist_entries(url: str, max_items: Optional[int] = None):
    try:
        metadata_opts = {
            "quiet": True,
            "skip_download": True,
            "ignoreerrors": True,
            "extract_flat": "in_playlist",
        }
        if max_items:
            metadata_opts["playlist_items"] = f"1:{max_items}"
        with yt_dlp.YoutubeDL(metadata_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
    except Exception as err:
        raise RuntimeError(f"Unable to retrieve playlist metadata: {err}") from err

    if not playlist_info or "entries" not in playlist_info:
        raise ValueError("The provided URL does not point to a valid playlist.")

    entries = []
    for index, entry in enumerate(playlist_info.get("entries", []) or [], start=1):
        if entry is None:
            continue
        entry["_app_index"] = entry.get("playlist_index") or index
        entry.setdefault("webpage_url", entry.get("url"))
        entries.append(entry)

    if max_items:
        entries = entries[:max_items]

    if not entries:
        raise ValueError("No downloadable videos were found in this playlist.")

    return playlist_info, entries


def build_ydl_options(target_dir: Path, media_format: str):
    base_opts = {
        "outtmpl": str(target_dir / "%(autonumber)05d - %(title)s.%(ext)s"),
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "autonumber_start": 1,
    }

    if media_format == "mp3":
        base_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )
    else:
        base_opts.update(
            {
                "format": "bv*+ba/best",
                "merge_output_format": "mp4",
            }
        )

    return base_opts


def choose_media_file(candidates: set[Path], media_format: str) -> Optional[Path]:
    """Return the most appropriate media file from the candidate set."""

    if not candidates:
        return None

    ext_priority = (
        ("mp3", "m4a", "opus", "webm", "aac"),
        ("mp4", "mkv", "webm", "m4v", "mov"),
    )

    priorities = ext_priority[0] if media_format == "mp3" else ext_priority[1]

    normalized = {path: path.suffix.lower().lstrip(".") for path in candidates}

    for ext in priorities:
        for path, suffix in normalized.items():
            if suffix == ext:
                return path

    media_suffixes = {"mp3", "m4a", "aac", "opus", "ogg", "mp4", "mkv", "webm", "m4v", "mov"}
    generic_candidates = [path for path, suffix in normalized.items() if suffix in media_suffixes]
    if generic_candidates:
        return generic_candidates[0]

    # Fallback to the first candidate if no preferred extension matched
    return next(iter(candidates))


def guess_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return {
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
        ".opus": "audio/opus",
        ".ogg": "audio/ogg",
        ".webm": "video/webm",
        ".mp4": "video/mp4",
        ".mkv": "video/x-matroska",
        ".mov": "video/quicktime",
    }.get(suffix, "application/octet-stream")


def normalize_duration(value: Optional[float]) -> Optional[int]:
    if value is None:
        return None
    try:
        seconds = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return max(seconds, 0)


def format_duration(seconds: Optional[int]) -> str:
    if seconds is None:
        return ""
    minutes, remainder = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{remainder:02d}"
    return f"{minutes:d}:{remainder:02d}"


def initialize_job_state() -> dict:
    return {
        "running": False,
        "playlist_url": None,
        "media_format": None,
        "max_items": None,
        "playlist_total": None,
        "playlist_title": None,
        "items": [],
        "failures": [],
        "archive_data": None,
        "archive_name": None,
        "status_type": "info",
        "status_message": "Awaiting your playlist...",
        "progress_value": 0.0,
        "progress_text": "Awaiting your playlist...",
        "thread": None,
        "cancel_event": None,
        "job_id": None,
        "error": None,
    }


def get_job_state() -> dict:
    if "job_state" not in st.session_state:
        st.session_state["job_state"] = initialize_job_state()
    return st.session_state["job_state"]


def job_matches(job_id: str) -> bool:
    job = get_job_state()
    return bool(job_id and job.get("job_id") == job_id)


def update_job_status(job_id: str, level: str, message: str) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["status_type"] = level
    job["status_message"] = message


def update_job_progress(job_id: str, value: float, text: str) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["progress_value"] = max(0.0, min(1.0, value))
    job["progress_text"] = text


def update_job_total(job_id: str, total: int) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["playlist_total"] = total


def register_success(job_id: str, file_info: dict) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["items"].append(file_info)


def register_failure(job_id: str, failure: dict) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["failures"].append(failure)


def register_error(job_id: str, error: Exception) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["error"] = str(error)
    job["status_type"] = "error"
    job["status_message"] = str(error)
    job["running"] = False
    job["cancel_event"] = None
    job["thread"] = None


def finalize_job(job_id: str, playlist_info: Optional[dict], media_format: str) -> None:
    if not job_matches(job_id):
        return
    job = get_job_state()
    job["running"] = False
    job["cancel_event"] = None
    job["thread"] = None

    if playlist_info:
        job["playlist_title"] = playlist_info.get("title")

    if job["items"]:
        archive_title = slugify(job.get("playlist_title") or "youtube-playlist")
        archive_name = f"{archive_title}-{media_format.lower()}s.zip"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_info in job["items"]:
                zipf.writestr(file_info["filename"], file_info["data"])
        buffer.seek(0)
        job["archive_data"] = buffer.getvalue()
        job["archive_name"] = archive_name

    if job.get("error") is None and job.get("status_type") != "warning":
        success_count = len(job["items"])
        failure_count = len(job["failures"])
        job["status_type"] = "success"
        job["status_message"] = (
            f"Completed {success_count} of {success_count + failure_count} items from "
            f"{job.get('playlist_title') or 'the playlist'}."
        )
    if job.get("status_type") == "warning":
        total = job.get("playlist_total") or max(len(job["items"]) + len(job["failures"]), 1)
        job["progress_value"] = min(1.0, (len(job["items"]) + len(job["failures"])) / total)
        job["progress_text"] = "Download cancelled."
    else:
        job["progress_value"] = 1.0
        job["progress_text"] = "Downloads complete!"


def start_download_job(url: str, media_format: str, max_items: Optional[int]) -> None:
    job = get_job_state()
    if job.get("running"):
        raise RuntimeError("A download task is already running. Please wait for it to finish or cancel it.")

    job_id = uuid.uuid4().hex
    cancel_event = threading.Event()

    status_message = "Preparing downloads..."
    if max_items:
        status_message = f"Preparing first {max_items} item(s)..."

    job.update(
        {
            "running": True,
            "playlist_url": url,
            "media_format": media_format,
            "max_items": max_items,
            "playlist_total": None,
            "playlist_title": None,
            "items": [],
            "failures": [],
            "archive_data": None,
            "archive_name": None,
            "status_type": "info",
            "status_message": status_message,
            "progress_value": 0.0,
            "progress_text": status_message,
            "thread": None,
            "cancel_event": cancel_event,
            "job_id": job_id,
            "error": None,
        }
    )

    ctx = get_script_run_ctx()

    def safe_rerun() -> None:
        try:
            st.rerun()
        except Exception:  # noqa: BLE001
            pass

    def status_callback(level: str, message: str) -> None:
        update_job_status(job_id, level, message)
        safe_rerun()

    def progress_callback(value: float, text: str) -> None:
        update_job_progress(job_id, value, text)
        safe_rerun()

    def total_callback(total: int) -> None:
        update_job_total(job_id, total)
        safe_rerun()

    def success_callback(file_info: dict) -> None:
        register_success(job_id, file_info)
        safe_rerun()

    def failure_callback(failure: dict) -> None:
        register_failure(job_id, failure)
        safe_rerun()

    def worker() -> None:
        try:
            playlist_info = download_playlist(
                url,
                media_format,
                status_callback=status_callback,
                progress_callback=progress_callback,
                total_callback=total_callback,
                success_callback=success_callback,
                failure_callback=failure_callback,
                cancel_event=cancel_event,
                max_items=max_items,
            )
            finalize_job(job_id, playlist_info, media_format)
        except Exception as err:  # noqa: BLE001
            register_error(job_id, err)
        finally:
            safe_rerun()

    worker_thread = threading.Thread(target=worker, daemon=True)
    add_script_run_ctx(worker_thread)
    worker_thread.start()
    job["thread"] = worker_thread
    safe_rerun()


def cancel_download_job() -> None:
    job = get_job_state()
    if not job.get("running") or not job.get("cancel_event"):
        return
    if not job["cancel_event"].is_set():
        job["cancel_event"].set()
        job["status_type"] = "warning"
        job["status_message"] = "Cancelling download..."

def download_playlist(
    url: str,
    media_format: str,
    status_callback=None,
    progress_callback=None,
    total_callback=None,
    success_callback=None,
    failure_callback=None,
    cancel_event=None,
    max_items: Optional[int] = None,
):
    ensure_ffmpeg(media_format.lower())
    playlist_info, entries = fetch_playlist_entries(url, max_items=max_items)
    total_items = len(entries)

    if total_callback:
        total_callback(total_items)

    if total_items == 0:
        return playlist_info

    media_format_lower = media_format.lower()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        ydl_opts = build_ydl_options(temp_path, media_format_lower)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for position, entry in enumerate(entries, start=1):
                if cancel_event and cancel_event.is_set():
                    if status_callback:
                        status_callback("warning", "Download cancelled by user.")
                    break

                title = entry.get("title") or f"Video {position}"
                if status_callback:
                    status_callback("info", f"Downloading {title} ({position}/{total_items})")

                video_url = entry.get("webpage_url") or entry.get("url")
                if not video_url:
                    failure = {"title": title, "error": "Missing video URL"}
                    if failure_callback:
                        failure_callback(failure)
                    if progress_callback:
                        progress_callback(position / total_items, f"Processed {position}/{total_items}")
                    continue

                before_download = {path for path in temp_path.iterdir() if path.is_file()}

                try:
                    ydl.download([video_url])
                except Exception as err:  # noqa: BLE001
                    failure = {"title": title, "error": str(err)}
                    if failure_callback:
                        failure_callback(failure)
                    if progress_callback:
                        progress_callback(position / total_items, f"Processed {position}/{total_items}")
                    continue

                after_download = {path for path in temp_path.iterdir() if path.is_file()}
                new_candidates = after_download - before_download
                media_file = choose_media_file(new_candidates, media_format_lower)

                if not media_file or not media_file.exists():
                    failure = {"title": title, "error": "Media file not produced"}
                    if failure_callback:
                        failure_callback(failure)
                    if progress_callback:
                        progress_callback(position / total_items, f"Processed {position}/{total_items}")
                    continue

                file_bytes = media_file.read_bytes()
                media_file.unlink(missing_ok=True)

                # Add "| Music Bank " to filename before extension
                original_name = media_file.name
                name_parts = original_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    modified_filename = f"{name_parts[0]} | Music Bank .{name_parts[1]}"
                else:
                    modified_filename = f"{original_name} | Music Bank "

                duration = normalize_duration(entry.get("duration"))
                file_info = {
                    "title": title,
                    "filename": modified_filename,
                    "data": file_bytes,
                    "duration": duration,
                    "url": video_url,
                    "position": position,
                    "mime": guess_mime_type(media_file.name),
                    "token": f"{position}-{uuid.uuid4().hex}",
                }

                if success_callback:
                    success_callback(file_info)

                if progress_callback:
                    progress_callback(position / total_items, f"Processed {position}/{total_items}")

    return playlist_info


st.set_page_config(page_title="Music Bank | YouTube Playlist Downloader", page_icon="🎵", layout="centered")
apply_liquid_glass_theme()

# Initialize preloader state
if "preloader_shown" not in st.session_state:
    st.session_state["preloader_shown"] = False

# Show preloader for 10 seconds on first load
if not st.session_state["preloader_shown"]:
    st.markdown(
        """
        <style>
        .preloader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 50%, rgba(96, 165, 250, 0.15), transparent 70%),
                        radial-gradient(circle at 30% 70%, rgba(168, 85, 247, 0.12), transparent 70%),
                        linear-gradient(135deg, #0f172a 0%, #0b1120 58%, #111827 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeOut 0.5s ease-in-out 9.5s forwards;
        }
        
        .preloader-content {
            text-align: center;
        }
        
        .preloader-logo {
            width: 250px;
            height: auto;
            animation: pulse 2s ease-in-out infinite;
            filter: drop-shadow(0 10px 30px rgba(96, 165, 250, 0.4));
        }
        
        .preloader-text {
            margin-top: 2rem;
            font-size: 1.5rem;
            font-weight: 600;
            color: #e2e8f0;
            letter-spacing: 0.05em;
            animation: fadeInOut 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                filter: drop-shadow(0 10px 30px rgba(96, 165, 250, 0.4));
            }
            50% {
                transform: scale(1.05);
                filter: drop-shadow(0 15px 40px rgba(96, 165, 250, 0.6));
            }
        }
        
        @keyframes fadeInOut {
            0%, 100% {
                opacity: 0.6;
            }
            50% {
                opacity: 1;
            }
        }
        
        @keyframes fadeOut {
            to {
                opacity: 0;
                visibility: hidden;
            }
        }
        </style>
        
        <div class="preloader">
            <div class="preloader-content">
                <svg class="preloader-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 375 374.999991" preserveAspectRatio="xMidYMid meet">
                    <defs>
                        <clipPath id="preloader-clip1"><path d="M 116.664062 76.050781 L 249 76.050781 L 249 231 L 116.664062 231 Z M 116.664062 76.050781 " clip-rule="nonzero"/></clipPath>
                    </defs>
                    <g clip-path="url(#preloader-clip1)">
                        <path fill="#5366b4" d="M 237.476562 141.773438 L 214.496094 128.46875 L 214.496094 76.050781 L 205.875 76.050781 L 205.875 158.472656 C 205.734375 169.183594 196.316406 176.121094 186.613281 173.195312 C 179.785156 171.117188 175.074219 164.089844 175.921875 157.105469 C 176.863281 149.511719 183.316406 142.90625 190.851562 143.988281 C 195.609375 144.652344 198.011719 143.800781 199.09375 141.726562 L 199.09375 112.238281 C 198.246094 110.632812 196.550781 110.398438 193.441406 112.191406 C 192.265625 112.898438 191.039062 113.558594 189.863281 114.265625 C 180.441406 119.691406 171.023438 125.210938 161.558594 130.542969 C 158.871094 132.054688 158.636719 134.269531 158.589844 136.628906 L 158.589844 170.503906 C 158.636719 176.070312 156.894531 180.789062 152.371094 184.140625 C 147.050781 188.054688 140.929688 189.046875 135.230469 185.742188 C 129.4375 182.394531 126.988281 172.957031 129.25 166.730469 C 131.460938 160.644531 138.574219 155.597656 144.980469 157.199219 C 149.875 158.425781 151.382812 157.199219 151.808594 154.417969 L 151.808594 103.699219 C 151.808594 103.699219 155.953125 101.386719 161.933594 98.085938 L 143.707031 87.515625 C 128.871094 78.929688 116.71875 85.960938 116.71875 103.132812 L 116.71875 211.597656 C 116.71875 228.773438 128.871094 235.800781 143.707031 227.214844 L 237.476562 172.957031 C 252.359375 164.417969 252.359375 150.359375 237.476562 141.773438 Z"/>
                    </g>
                    <g transform="translate(29, 241)">
                        <g fill="#000000">
                            <path d="M 48.109375 0 L 40.21875 0 L 36.671875 -23.4375 L 25.953125 -0.046875 L 24.0625 -0.046875 L 13.34375 -23.4375 L 9.796875 0 L 1.84375 0 L 7.484375 -35.90625 L 15.28125 -35.90625 L 24.984375 -13.90625 L 34.734375 -35.90625 L 42.53125 -35.90625 Z" transform="translate(1.238117, 40.159961)"/>
                            <path d="M 16.265625 0.765625 C 13.660156 0.765625 11.375 0.242188 9.40625 -0.796875 C 7.445312 -1.835938 5.925781 -3.289062 4.84375 -5.15625 C 3.769531 -7.019531 3.234375 -9.203125 3.234375 -11.703125 L 3.234375 -27.703125 L 10.71875 -27.703125 L 10.71875 -12.5625 C 10.71875 -10.582031 11.203125 -9.035156 12.171875 -7.921875 C 13.148438 -6.816406 14.515625 -6.265625 16.265625 -6.265625 C 18.003906 -6.265625 19.351562 -6.828125 20.3125 -7.953125 C 21.269531 -9.078125 21.75 -10.613281 21.75 -12.5625 L 21.75 -27.703125 L 29.234375 -27.703125 L 29.234375 -11.703125 C 29.234375 -9.203125 28.691406 -7.019531 27.609375 -5.15625 C 26.535156 -3.289062 25.023438 -1.835938 23.078125 -0.796875 C 21.128906 0.242188 18.859375 0.765625 16.265625 0.765625 Z" transform="translate(48.316515, 40.159961)"/>
                            <path d="M 13.4375 0.765625 C 11.113281 0.765625 9.078125 0.359375 7.328125 -0.453125 C 5.585938 -1.273438 4.226562 -2.429688 3.25 -3.921875 C 2.28125 -5.410156 1.796875 -7.144531 1.796875 -9.125 L 9.078125 -9.125 C 9.109375 -7.894531 9.550781 -6.972656 10.40625 -6.359375 C 11.269531 -5.742188 12.367188 -5.4375 13.703125 -5.4375 C 14.753906 -5.4375 15.671875 -5.664062 16.453125 -6.125 C 17.242188 -6.59375 17.640625 -7.285156 17.640625 -8.203125 C 17.640625 -9.160156 17.117188 -9.835938 16.078125 -10.234375 C 15.035156 -10.628906 13.78125 -10.945312 12.3125 -11.1875 C 11.21875 -11.351562 10.078125 -11.585938 8.890625 -11.890625 C 7.710938 -12.203125 6.628906 -12.648438 5.640625 -13.234375 C 4.648438 -13.816406 3.835938 -14.617188 3.203125 -15.640625 C 2.566406 -16.671875 2.25 -18.003906 2.25 -19.640625 C 2.25 -21.390625 2.71875 -22.929688 3.65625 -24.265625 C 4.601562 -25.597656 5.90625 -26.628906 7.5625 -27.359375 C 9.21875 -28.097656 11.175781 -28.46875 13.4375 -28.46875 C 15.664062 -28.46875 17.609375 -28.082031 19.265625 -27.3125 C 20.921875 -26.539062 22.207031 -25.460938 23.125 -24.078125 C 24.050781 -22.691406 24.515625 -21.078125 24.515625 -19.234375 L 17.390625 -19.234375 C 17.390625 -20.328125 17.019531 -21.144531 16.28125 -21.6875 C 15.550781 -22.238281 14.535156 -22.515625 13.234375 -22.515625 C 12.066406 -22.515625 11.160156 -22.265625 10.515625 -21.765625 C 9.867188 -21.273438 9.546875 -20.640625 9.546875 -19.859375 C 9.546875 -18.929688 10.054688 -18.296875 11.078125 -17.953125 C 12.109375 -17.609375 13.34375 -17.316406 14.78125 -17.078125 C 15.90625 -16.878906 17.066406 -16.632812 18.265625 -16.34375 C 19.460938 -16.050781 20.570312 -15.613281 21.59375 -15.03125 C 22.625 -14.445312 23.453125 -13.640625 24.078125 -12.609375 C 24.710938 -11.585938 25.03125 -10.238281 25.03125 -8.5625 C 25.03125 -6.6875 24.550781 -5.046875 23.59375 -3.640625 C 22.632812 -2.234375 21.28125 -1.144531 19.53125 -0.375 C 17.789062 0.382812 15.757812 0.765625 13.4375 0.765625 Z" transform="translate(77.85555, 40.159961)"/>
                            <path d="M 3.59375 -31.390625 L 3.59375 -38.375 L 11.078125 -38.375 L 11.078125 -31.390625 Z M 3.59375 0 L 3.59375 -27.703125 L 11.078125 -27.703125 L 11.078125 0 Z" transform="translate(101.855824, 40.159961)"/>
                            <path d="M 16.46875 0.765625 C 13.695312 0.765625 11.195312 0.117188 8.96875 -1.171875 C 6.75 -2.472656 5 -4.234375 3.71875 -6.453125 C 2.4375 -8.679688 1.796875 -11.179688 1.796875 -13.953125 C 1.796875 -16.722656 2.4375 -19.203125 3.71875 -21.390625 C 5 -23.578125 6.75 -25.300781 8.96875 -26.5625 C 11.195312 -27.832031 13.710938 -28.46875 16.515625 -28.46875 C 18.910156 -28.46875 21.085938 -28 23.046875 -27.0625 C 25.015625 -26.125 26.65625 -24.796875 27.96875 -23.078125 C 29.289062 -21.367188 30.175781 -19.390625 30.625 -17.140625 L 23.1875 -17.140625 C 22.570312 -18.503906 21.671875 -19.5625 20.484375 -20.3125 C 19.304688 -21.0625 17.96875 -21.4375 16.46875 -21.4375 C 15.132812 -21.4375 13.925781 -21.101562 12.84375 -20.4375 C 11.769531 -19.769531 10.925781 -18.875 10.3125 -17.75 C 9.695312 -16.625 9.390625 -15.34375 9.390625 -13.90625 C 9.390625 -12.46875 9.695312 -11.175781 10.3125 -10.03125 C 10.925781 -8.882812 11.769531 -7.96875 12.84375 -7.28125 C 13.925781 -6.601562 15.132812 -6.265625 16.46875 -6.265625 C 18.007812 -6.265625 19.351562 -6.664062 20.5 -7.46875 C 21.644531 -8.269531 22.539062 -9.421875 23.1875 -10.921875 L 30.734375 -10.921875 C 30.285156 -8.597656 29.394531 -6.554688 28.0625 -4.796875 C 26.726562 -3.035156 25.066406 -1.664062 23.078125 -0.6875 C 21.097656 0.28125 18.894531 0.765625 16.46875 0.765625 Z" transform="translate(113.599058, 40.159961)"/>
                        </g>
                    </g>
                    <g transform="translate(183, 243)">
                        <g fill="#5366b4">
                            <path d="M 25.703125 -18.921875 C 27.273438 -18.109375 28.492188 -16.957031 29.359375 -15.46875 C 30.234375 -13.976562 30.671875 -12.273438 30.671875 -10.359375 C 30.671875 -8.441406 30.164062 -6.695312 29.15625 -5.125 C 28.15625 -3.550781 26.789062 -2.300781 25.0625 -1.375 C 23.332031 -0.457031 21.441406 0 19.390625 0 L 4.109375 0 L 4.109375 -35.90625 L 18.984375 -35.90625 C 21.035156 -35.90625 22.875 -35.503906 24.5 -34.703125 C 26.125 -33.898438 27.40625 -32.796875 28.34375 -31.390625 C 29.28125 -29.992188 29.75 -28.421875 29.75 -26.671875 C 29.75 -25.128906 29.390625 -23.675781 28.671875 -22.3125 C 27.953125 -20.945312 26.960938 -19.816406 25.703125 -18.921875 Z M 22.21875 -25.4375 C 22.21875 -26.570312 21.859375 -27.5 21.140625 -28.21875 C 20.421875 -28.9375 19.441406 -29.296875 18.203125 -29.296875 L 11.75 -29.296875 L 11.75 -21.640625 L 18.203125 -21.640625 C 19.441406 -21.640625 20.421875 -22 21.140625 -22.71875 C 21.859375 -23.4375 22.21875 -24.34375 22.21875 -25.4375 Z M 18.625 -7.125 C 19.914062 -7.125 20.945312 -7.5 21.71875 -8.25 C 22.488281 -9.007812 22.875 -9.988281 22.875 -11.1875 C 22.875 -12.34375 22.488281 -13.296875 21.71875 -14.046875 C 20.945312 -14.804688 19.914062 -15.1875 18.625 -15.1875 L 11.75 -15.1875 L 11.75 -7.125 Z" transform="translate(0.361662, 38.663296)"/>
                            <path d="M 26.21875 -27.75 L 31.796875 -27.75 L 31.796875 -0.046875 L 25.90625 -0.046875 L 25.296875 -2.515625 C 24.097656 -1.484375 22.734375 -0.675781 21.203125 -0.09375 C 19.679688 0.476562 18.050781 0.765625 16.3125 0.765625 C 13.539062 0.765625 11.0625 0.125 8.875 -1.15625 C 6.6875 -2.4375 4.957031 -4.175781 3.6875 -6.375 C 2.425781 -8.582031 1.796875 -11.09375 1.796875 -13.90625 C 1.796875 -16.675781 2.425781 -19.160156 3.6875 -21.359375 C 4.957031 -23.566406 6.6875 -25.300781 8.875 -26.5625 C 11.0625 -27.832031 13.539062 -28.46875 16.3125 -28.46875 C 18.09375 -28.46875 19.75 -28.164062 21.28125 -27.5625 C 22.820312 -26.96875 24.191406 -26.140625 25.390625 -25.078125 Z M 16.921875 -6.3125 C 18.359375 -6.3125 19.648438 -6.632812 20.796875 -7.28125 C 21.941406 -7.9375 22.835938 -8.835938 23.484375 -9.984375 C 24.140625 -11.128906 24.46875 -12.4375 24.46875 -13.90625 C 24.46875 -15.34375 24.140625 -16.632812 23.484375 -17.78125 C 22.835938 -18.925781 21.941406 -19.832031 20.796875 -20.5 C 19.648438 -21.164062 18.359375 -21.5 16.921875 -21.5 C 15.453125 -21.5 14.15625 -21.164062 13.03125 -20.5 C 11.90625 -19.832031 11.015625 -18.925781 10.359375 -17.78125 C 9.710938 -16.632812 9.390625 -15.34375 9.390625 -13.90625 C 9.390625 -12.4375 9.710938 -11.132812 10.359375 -10 C 11.015625 -8.875 11.90625 -7.976562 13.03125 -7.3125 C 14.15625 -6.644531 15.453125 -6.3125 16.921875 -6.3125 Z" transform="translate(30.362255, 38.663296)"/>
                            <path d="M 19.390625 -28.375 C 22.535156 -28.375 25.019531 -27.320312 26.84375 -25.21875 C 28.675781 -23.113281 29.59375 -20.300781 29.59375 -16.78125 L 29.59375 0 L 22.109375 0 L 22.109375 -15.59375 C 22.109375 -19.726562 20.5 -21.796875 17.28125 -21.796875 C 15.375 -21.796875 13.863281 -21.144531 12.75 -19.84375 C 11.632812 -18.550781 11.078125 -16.789062 11.078125 -14.5625 L 11.078125 0 L 3.59375 0 L 3.59375 -27.703125 L 8.71875 -27.703125 L 10.203125 -24.265625 C 11.234375 -25.523438 12.550781 -26.523438 14.15625 -27.265625 C 15.757812 -28.003906 17.503906 -28.375 19.390625 -28.375 Z" transform="translate(62.824521, 38.663296)"/>
                            <path d="M 29.03125 0 L 19.953125 0 L 11.078125 -13.234375 L 11.078125 0 L 3.59375 0 L 3.59375 -37.703125 L 11.078125 -37.703125 L 11.078125 -15.390625 L 19.390625 -27.703125 L 28.015625 -27.703125 L 18.671875 -14.515625 Z" transform="translate(92.773829, 38.663296)"/>
                        </g>
                    </g>
                </svg>
                <div class="preloader-text">Loading Music Bank...</div>
            </div>
        </div>
        
        <script>
            setTimeout(function() {
                document.querySelector('.preloader').style.display = 'none';
            }, 10000);
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Mark preloader as shown after 10 seconds
    import time
    time.sleep(10)
    st.session_state["preloader_shown"] = True
    st.rerun()

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "MP3"

job_state = get_job_state()


def render_results(placeholder) -> None:
    holder = placeholder.empty()
    job = get_job_state()

    with holder.container():
        st.markdown('<div class="glass-results">', unsafe_allow_html=True)
        st.markdown("### Ready to download", unsafe_allow_html=False)

        col_ready, col_failed, col_total = st.columns(3)
        col_ready.metric("Ready", len(job["items"]))
        col_failed.metric("Failed", len(job["failures"]))
        playlist_total = job.get("playlist_total")
        col_total.metric("Playlist size", playlist_total if playlist_total else "–")

        if job["items"]:
            for idx, item in enumerate(job["items"], start=1):
                button_label = f"Download {item['filename']}"
                key = f"download-{idx}-{item['token']}"
                st.download_button(
                    label=button_label,
                    data=item["data"],
                    file_name=item["filename"],
                    mime=item["mime"],
                    key=key,
                )
                meta_bits = [item.get("title")]
                duration_text = format_duration(item.get("duration"))
                if duration_text:
                    meta_bits.append(duration_text)
                meta_line = " • ".join(filter(None, meta_bits))
                if meta_line:
                    st.caption(meta_line)
        else:
            st.caption("Completed files will appear here as soon as they finish processing.")

        if job.get("archive_data") and job.get("archive_name"):
            st.download_button(
                label="Download all as ZIP",
                data=job["archive_data"],
                file_name=job["archive_name"],
                mime="application/zip",
                key="download-archive",
            )

        if job["failures"]:
            st.warning(f"{len(job['failures'])} item(s) failed. See details below.")
            with st.expander("Failed items", expanded=False):
                for item in job["failures"]:
                    st.write(f"- {item['title']}: {item['error']}")

        st.markdown('</div>', unsafe_allow_html=True)


def render_status(status_placeholder, progress_holder) -> None:
    job = get_job_state()
    status_level = job.get("status_type", "info")
    status_message = job.get("status_message", "Awaiting your playlist...")
    if status_level == "error":
        status_placeholder.error(status_message)
    elif status_level == "success":
        status_placeholder.success(status_message)
    elif status_level == "warning":
        status_placeholder.warning(status_message)
    else:
        status_placeholder.info(status_message)

    progress_holder.progress(
        job.get("progress_value", 0.0),
        text=job.get("progress_text", "Awaiting your playlist..."),
    )


# Check URL query params for tab selection
query_params = st.query_params
if "tab" in query_params:
    tab_value = query_params["tab"].upper()
    if tab_value in ["MP3", "MP4"] and tab_value != st.session_state.get("active_tab"):
        st.session_state["active_tab"] = tab_value
        st.rerun()

active_format = st.session_state["active_tab"]

mp3_active = "active" if active_format == "MP3" else ""
mp4_active = "active" if active_format == "MP4" else ""

st.markdown(
    f"""
    <div class="my-nav">
        <ul class="nav-tabs">
            <li class="nav-item nav-logo">
                <svg class="nav-logo-img" viewBox="0 0 500 500" xmlns="./assets/Music Bank.svg">
                    <defs>
                        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#5B7EC8;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#4A5F9D;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <path fill="url(#logoGradient)" d="M200,160 L200,240 C200,260 220,260 220,240 L220,200 L250,200 L250,240 C250,260 270,260 270,240 L270,180 L290,160 L310,280 L200,280 Z M180,300 L330,300 L350,160 L310,140 L270,160 L270,140 L240,140 L240,180 L200,180 L180,300 Z"/>
                    <text x="120" y="360" font-family="Arial, sans-serif" font-size="48" font-weight="bold" fill="#000000">Music</text>
                    <text x="250" y="360" font-family="Arial, sans-serif" font-size="48" font-weight="600" fill="#5B7EC8">Bank</text>
                </svg>
            </li>
            <li class="nav-item">
                <a href="?tab=mp3" target="_self" class="nav-tab {mp3_active}">🎵 MP3</a>
            </li>
            <li class="nav-item">
                <a href="?tab=mp4" target="_self" class="nav-tab {mp4_active}">🎬 MP4</a>
            </li>
        </ul>
    </div>
    <div class="nav-spacer"></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="glass-hero">
        <h1>YouTube Playlist Downloader - {active_format}</h1>
        <p>Transform any YouTube playlist into pristine {active_format} files with a single click. Paste your link,
        choose options, and let the alchemy begin.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="glass-card glass-form">', unsafe_allow_html=True)
    with st.form("download_form"):
        playlist_url = st.text_input(
            "Playlist URL",
            placeholder="https://www.youtube.com/playlist?list=...",
        )
        format_choice = active_format
        with st.expander("Advanced options", expanded=False):
            limit_playlist = st.checkbox("Limit playlist items", value=False)
            limit_value = st.number_input(
                "Maximum items to process",
                min_value=1,
                max_value=2000,
                value=250,
                step=25,
                disabled=not limit_playlist,
                help="Process only the first N entries. Helpful for auto-generated mixes with thousands of tracks.",
            )
        submitted = st.form_submit_button("Start Download")
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="glass-card glass-status">', unsafe_allow_html=True)
    status_placeholder = st.empty()
    progress_holder = st.empty()
    if job_state.get("running"):
        with st.container():
            if st.button("Cancel downloads", key="cancel_download", type="secondary"):
                cancel_download_job()
    result_zone = st.container()
    result_placeholder = result_zone.empty()
    st.markdown("</div>", unsafe_allow_html=True)

render_status(status_placeholder, progress_holder)
render_results(result_placeholder)

if job_state.get("running"):
    import time
    time.sleep(0.5)
    st.rerun()

if submitted:
    url = playlist_url.strip()
    selected_limit: Optional[int] = int(limit_value) if limit_playlist else None
    auto_limit_applied = False
    if selected_limit is None and url and is_mix_playlist(url):
        selected_limit = 250
        auto_limit_applied = True

    if not url:
        status_placeholder.error("Please provide a playlist URL.")
    elif job_state.get("running"):
        status_placeholder.warning("A download is already in progress. Please wait or cancel it before starting a new one.")
    else:
        try:
            ensure_ffmpeg(format_choice.lower())
        except Exception as err:  # noqa: BLE001
            job_state.update(
                {
                    "status_type": "error",
                    "status_message": str(err),
                    "progress_value": 0.0,
                    "progress_text": "Awaiting your playlist...",
                    "running": False,
                }
            )
            status_placeholder.error(str(err))
        else:
            try:
                if auto_limit_applied:
                    status_placeholder.info("Detected a mix playlist. Limiting to the first 250 items for stability.")
                start_download_job(url, format_choice, selected_limit)
            except RuntimeError as err:
                status_placeholder.warning(str(err))
            except Exception as err:  # noqa: BLE001
                status_placeholder.error(str(err))

    render_status(status_placeholder, progress_holder)
    render_results(result_placeholder)
