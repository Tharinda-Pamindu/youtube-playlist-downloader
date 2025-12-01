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


def apply_liquid_glass_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --glass-bg: rgba(15, 23, 42, 0.55);
            --glass-border: rgba(148, 163, 184, 0.35);
            --accent: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #f472b6 100%);
            --text-primary: #e2e8f0;
            --text-muted: #cbd5f5;
        }

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
        }

        .glass-hero {
            position: relative;
            margin: 2.5rem 0 1.75rem 0;
            padding: 2.75rem 3rem;
            border-radius: 32px;
            background: radial-gradient(circle at 25% -10%, rgba(96, 165, 250, 0.22), transparent 65%),
                        radial-gradient(circle at 85% 120%, rgba(236, 72, 153, 0.20), transparent 55%),
                        rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.24);
            backdrop-filter: blur(26px) saturate(120%);
            box-shadow: 0 25px 60px rgba(15, 23, 42, 0.55);
            overflow: hidden;
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
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(94, 234, 212, 0.25);
            backdrop-filter: blur(24px) saturate(150%);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.4);
        }

        div[data-testid="stAlert"] p {
            color: var(--text-primary);
        }

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

        [data-testid="stMetricValue"] {
            color: var(--text-primary);
        }

        [data-testid="stMetricLabel"] {
            color: rgba(226, 232, 240, 0.76);
        }

        @media (max-width: 768px) {
            .glass-card {
                padding: 1.6rem 1.4rem;
            }

            .glass-hero {
                padding: 2.2rem 1.75rem;
            }
        }
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

                duration = normalize_duration(entry.get("duration"))
                file_info = {
                    "title": title,
                    "filename": media_file.name,
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


st.set_page_config(page_title="YouTube Playlist Downloader", page_icon="🎧", layout="centered")
apply_liquid_glass_theme()

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


st.markdown(
    """
    <div class="glass-hero">
        <h1>Liquid Glass Playlist Downloader</h1>
        <p>Transform any YouTube playlist into pristine MP3 or MP4 files with a single click. Paste your link,
        choose a format, and let the alchemy begin.</p>
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
        format_choice = st.radio("Select output format", options=["MP4", "MP3"], horizontal=True)
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
