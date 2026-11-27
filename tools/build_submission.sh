#!/usr/bin/env bash
# Dựng submission/{Product,Slide,Document}. Dùng: TEAM="Tên đội" MEMBERS="A, B, C" WEB_URL="https://..." tools/build_submission.sh
set -euo pipefail
cd "$(dirname "$0")/.."
TEAM="${TEAM:-Odylytics}"; MEMBERS="${MEMBERS:-}"; WEB_URL="${WEB_URL:-https://innate.odylytics.com}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=submission; T=$(mktemp -d)
rm -rf $OUT; mkdir -p $OUT/Product $OUT/Slide $OUT/Document
fill() { sed -e "s|@TEAM@|$TEAM|g" -e "s|@WEB_URL@|$WEB_URL|g" "$1"; }
pdf() { "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf="$2" "file://$1" >/dev/null 2>&1; }

# 1) Product: hướng dẫn 1 trang A4
fill tools/product-guide.html > $T/g0.html && python3 tools/brand/build_brand.py $T/g0.html $T/guide.html "$PWD/tools/assets" && pdf $T/guide.html "$PWD/$OUT/Product/Innate-product-guide.pdf"
# 2) Slide: editable PPTX (tools/build_pptx.js) -> PDF exported by PowerPoint itself (macOS), so the PDF is exactly what the PPTX shows
[ -d tools/node_modules/pptxgenjs ] || npm --prefix tools i pptxgenjs --silent
node tools/build_pptx.js "$PWD/$OUT/Slide/Innate-slides.pptx" "$TEAM" "$WEB_URL"
osascript tools/lib/export_pdf.applescript "$PWD/$OUT/Slide/Innate-slides.pptx" "$PWD/$OUT/Slide/Innate-slides.pdf"
mkdir -p $OUT/Slide/fonts && cp tools/fonts/*.ttf $OUT/Slide/fonts/   # Sora + Manrope (SIL OFL): install before editing the PPTX
# 3) Document: mã nguồn .zip (chỉ file đã commit, bỏ papers/, .env, db) + README
S=$T/src/Innate_Odylytics; mkdir -p $S
git ls-files -co --exclude-standard -z | grep -z -v -E '^(papers/|submission/|docs/brand/Brand-identity-kit.pdf|\.claude/)|\.env' | xargs -0 -I{} cp --parents "{}" $S 2>/dev/null || \
  git ls-files -co --exclude-standard | grep -v -E '^(papers/|submission/|docs/brand/Brand-identity-kit.pdf|\.claude/)|\.env' | rsync -a --files-from=- . $S
sed -e '/^> \*\*KHUNG README/d' docs/submission/README.submission.md | sed -e "s|\`TODO: tên đội\`|$TEAM|" -e "s|\`TODO\` · \*\*Chủ đề|$MEMBERS · **Chủ đề|" > $S/README.md
cp $S/README.md $OUT/Document/README.md
(cd $T/src && zip -qr "$OLDPWD/$OUT/Document/Innate-source-code.zip" Innate_Odylytics -x '*/__pycache__/*' '*.pyc' '*/node_modules/*')
rm -rf $T
for f in $OUT/*/*; do echo "$f  $(du -h "$f" | cut -f1)"; done
for p in $OUT/Product/*.pdf $OUT/Slide/*.pdf; do echo "$p: $(python3 -c "import re,sys;print(len(re.findall(rb'/Type\s*/Page[^s]',open(sys.argv[1],'rb').read())))" "$p") trang"; done
