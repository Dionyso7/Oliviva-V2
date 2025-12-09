import argparse
import os
import sys
import shutil
from pathlib import Path
import re

try:
    from PIL import Image
except Exception as e:
    print("Pillow requis: installer avec 'pip install pillow'")
    sys.exit(1)

ALLOWED_EXTS = {".png", ".jpg", ".jpeg"}
IGNORE_EXTS = {".svg", ".gif", ".webp"}

def normalize(s):
    return s.lower()

def is_excluded(path: Path, extra_patterns):
    name = normalize(path.name)
    if any(k in name for k in ["logo", "favicon", "webclip"]):
        return True
    if any(k in name for k in extra_patterns):
        return True
    for p in path.parents:
        pn = normalize(p.name)
        if pn.startswith("logo"):
            return True
    return False

def find_candidates(images_dir: Path, extra_patterns):
    items = []
    for root, _, files in os.walk(images_dir):
        for f in files:
            p = Path(root) / f
            ext = p.suffix.lower()
            if ext in IGNORE_EXTS:
                continue
            if ext not in ALLOWED_EXTS:
                continue
            if is_excluded(p, extra_patterns):
                continue
            items.append(p)
    return items

def ensure_mode(img: Image.Image):
    if img.mode in ("RGB", "RGBA"):
        return img
    if img.mode in ("P", "LA"):
        return img.convert("RGBA")
    return img.convert("RGB")

def convert_to_webp(src: Path, dst: Path, quality: int, lossless_png: bool):
    with Image.open(src) as im:
        im = ensure_mode(im)
        params = {}
        if src.suffix.lower() == ".png":
            if lossless_png:
                params["lossless"] = True
            else:
                params["quality"] = quality
        else:
            params["quality"] = quality
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, format="WEBP", **params)

def build_webp_path(src: Path):
    return src.with_suffix(".webp")

def backup_file(fp: Path, backup_dir: Path):
    backup_dir.mkdir(parents=True, exist_ok=True)
    rel = fp.relative_to(Path.cwd()) if fp.is_absolute() else fp
    target = backup_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fp, target)

def rewrite_in_text(text: str, mapping):
    out = text
    for k, v in mapping.items():
        out = out.replace(k, v)
    return out

def rewrite_references(project_root: Path, mapping, backup_dir: Path):
    html_css = []
    for ext in [".html", ".css"]:
        html_css.extend(project_root.rglob(f"*{ext}"))
    for fp in html_css:
        content = fp.read_text(encoding="utf-8", errors="ignore")
        new_content = rewrite_in_text(content, mapping)
        if new_content != content:
            if backup_dir:
                backup_file(fp, backup_dir)
            fp.write_text(new_content, encoding="utf-8")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--images-dir", default="images")
    p.add_argument("--quality", type=int, default=82)
    p.add_argument("--lossless-png", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--replace-originals", action="store_true")
    p.add_argument("--rewrite-html", action="store_true")
    p.add_argument("--backup-dir", default=None)
    p.add_argument("--exclude", action="append", default=[])
    p.add_argument("--cleanup-unused", action="store_true")
    p.add_argument("--minify-css", action="store_true")
    p.add_argument("--add-img-attrs", action="store_true")
    return p.parse_args()

def main():
    args = parse_args()
    project_root = Path.cwd()
    images_dir = project_root / args.images_dir
    if not images_dir.exists():
        print(f"Dossier introuvable: {images_dir}")
        sys.exit(1)
    extra_patterns = [normalize(x) for x in args.exclude]
    items = find_candidates(images_dir, extra_patterns)
    print(f"Candidats: {len(items)}")
    mapping = {}
    for src in items:
        dst = build_webp_path(src)
        rel_src = str(src.relative_to(project_root)).replace("\\", "/")
        rel_dst = str(dst.relative_to(project_root)).replace("\\", "/")
        mapping[rel_src] = rel_dst
        if args.dry_run:
            print(f"Convertir: {src} -> {dst}")
            continue
        convert_to_webp(src, dst, args.quality, args.lossless_png)
        if args.replace_originals:
            try:
                os.remove(src)
            except Exception:
                pass
    if args.rewrite_html:
        backup_dir = None
        if args.backup_dir:
            backup_dir = Path(args.backup_dir)
        else:
            backup_dir = project_root / "backup" / __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
        if args.dry_run:
            print("Réécriture HTML/CSS simulée")
        else:
            rewrite_references(project_root, mapping, backup_dir)
            print(f"Backup: {backup_dir}")
    if args.add_img_attrs:
        if args.dry_run:
            print("Ajout d'attributs IMG simulé")
        else:
            backup_dir = project_root / "backup" / __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S") if not args.backup_dir else Path(args.backup_dir)
            html_files = list(project_root.rglob("*.html"))
            for fp in html_files:
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                def repl(m):
                    tag = m.group(0)
                    tl = tag.lower()
                    attrs = []
                    if "decoding=" not in tl:
                        attrs.append('decoding="async"')
                    if "loading=" not in tl:
                        attrs.append('loading="lazy"')
                    if attrs:
                        return tag.replace("<img", "<img " + " ".join(attrs), 1)
                    return tag
                new_content = re.sub(r"<img[^>]*>", repl, content, flags=re.IGNORECASE)
                if new_content != content:
                    backup_file(fp, backup_dir)
                    fp.write_text(new_content, encoding="utf-8")
    if args.minify_css:
        if args.dry_run:
            print("Minification CSS simulée")
        else:
            backup_dir = project_root / "backup" / __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S") if not args.backup_dir else Path(args.backup_dir)
            css_dir = project_root / "css"
            for fp in css_dir.rglob("*.css"):
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                content = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", content)
                content = content.replace("\r", "")
                lines = [ln.strip() for ln in content.split("\n")]
                content = "".join(lines)
                content = re.sub(r"\s+", " ", content)
                if content:
                    backup_file(fp, backup_dir)
                    fp.write_text(content, encoding="utf-8")
    if args.cleanup_unused:
        refs = set()
        for ext in [".html", ".css", ".js"]:
            for fp in project_root.rglob(f"*{ext}"):
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for img_ext in [".webp", ".png", ".jpg", ".jpeg", ".svg", ".gif"]:
                    base = "images/"
                    i = 0
                    while True:
                        idx = content.find(base, i)
                        if idx == -1:
                            break
                        end = idx
                        while end < len(content) and content[end] not in ['"', "'", ")", "(", " ", "\n", "]", ";"]:
                            end += 1
                        path = content[idx:end]
                        if path.endswith(img_ext):
                            refs.add(path.replace("\\", "/"))
                        i = end
        to_delete = []
        for root, _, files in os.walk(images_dir):
            for f in files:
                p = Path(root) / f
                ext = p.suffix.lower()
                if ext in {".svg", ".gif"}:
                    continue
                rel = str(p.relative_to(project_root)).replace("\\", "/")
                if rel not in refs:
                    to_delete.append(p)
        print(f"Non référencés: {len(to_delete)}")
        for p in to_delete:
            if args.dry_run:
                print(f"Supprimer: {p}")
            else:
                try:
                    os.remove(p)
                except Exception:
                    pass
    print("Terminé")

if __name__ == "__main__":
    main()

