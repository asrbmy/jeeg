# keywords: organize, organise, sort downloads, clean downloads, tidy downloads, arrange files, sort files, declutter
# desc: Sort loose files in Downloads into folders by type (add 'preview' to just look)
# category: files
# usage: organize downloads [preview]
# confirm: yes
import shutil, time
from pathlib import Path
from _lib import args_text, user_dir
from _files import unique_path
CATS = {
 "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic", ".tiff", ".ico"},
 "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".md", ".epub"},
 "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm", ".flv"},
 "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"},
 "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz"},
 "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk", ".appimage"},
 "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".go", ".rs", ".sh", ".ipynb"},
}
PARTIAL = {".crdownload", ".part", ".tmp", ".download", ".partial", ".opdownload"}
preview = "preview" in args_text().lower().split()
folder = user_dir("Downloads")
moved = {}
done_moves = []
for f in sorted(folder.iterdir()):
    if not f.is_file() or f.is_symlink() or f.name.startswith("."):
        continue
    ext = f.suffix.lower()
    if ext in PARTIAL or time.time() - f.stat().st_mtime < 120:
        continue                                    # still downloading / just created
    cat = next((c for c, exts in CATS.items() if ext in exts), None)
    if not cat:
        continue
    dest = unique_path(folder / cat / f.name)
    print(f"  {f.name}  ->  {cat}/")
    if not preview:
        dest.parent.mkdir(exist_ok=True)
        shutil.move(str(f), str(dest)); done_moves.append((f, dest))
    moved[cat] = moved.get(cat, 0) + 1
n = sum(moved.values())
if done_moves:
    from _undo import record
    record("organise downloads", done_moves)
print(f"{'Would move' if preview else 'Moved'} {n} file(s)." + ("" if n else " Nothing to organise."))
