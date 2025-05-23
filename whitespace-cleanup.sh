#!/usr/bin/env bash
# whitespace-cleanup.sh — Emacs‑style “M‑x whitespace‑cleanup” for shell users

set -euo pipefail
TABWIDTH=4            # change to 2, 8, … if you prefer a different tab width

cleanup_file() {
  local file=$1
  [[ -f $file ]] || { printf 'Not a regular file: %s\n' "$file" >&2; return 1; }

  local tmp
  tmp=$(mktemp)

  # 1) convert tabs → spaces; 2) strip trailing spaces/tabs; 3) tidy blank lines
  expand -t "$TABWIDTH" -- "$file" |           # 1. untabify
    sed -E 's/[[:space:]]+$//' |               # 2. drop trailing whitespace
    awk '
      # 3. remove leading blanks, collapse trailing blanks, add 1 final \n
      {
        if (!started) {                        # still in “leading blank zone”?
          if ($0 ~ /^[[:space:]]*$/) next      #   yes → skip blank
          started = 1                          #   no  → content starts
        }
        buf[++n] = $0                          # store the useful lines
      }
      END {
        while (n && buf[n] ~ /^[[:space:]]*$/) n--   # trim trailing blanks

        for (i = 1; i <= n; i++) print buf[i]        # emit real content

        if (n == 0) print ""                         # empty file → 1 newline
        # (print already ended the last real line with exactly one newline,
        # so we DO NOT add another here)
      }
    ' > "$tmp"

  mv -- "$tmp" "$file"
}

for f in "$@"; do
  cleanup_file "$f"
done
