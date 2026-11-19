#!/usr/bin/env bash
# Run before every commit. Fails if anything private looks like it's about to go public.
# Checks every tracked or staged file, plus any untracked file that isn't ignored.
set -u
cd "$(git rev-parse --show-toplevel)"
files=$( { git ls-files; git ls-files --others --exclude-standard; } | sort -u | grep -v -E '^(scripts/check\.sh|LICENSE)$')
fail=0
hit() { echo "STOP: $1"; echo "$2" | head -5; echo; fail=1; }

scan() { # label, extended regex, extra grep flags
  local out; out=$(echo "$files" | xargs -r grep -n -I -E $3 -- "$2" 2>/dev/null)
  [ -n "$out" ] && hit "$1" "$out"
}
scan "looks like an API key or token" '(Bearer [A-Za-z0-9._-]{20,}|sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}|api[_-]?key"?[[:space:]]*[:=][[:space:]]*"?[A-Za-z0-9]{16,})' "-i"
scan "email address" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "-i"
scan "phone number" '\(?[0-9]{3}\)?[ .-][0-9]{3}[ .-][0-9]{4}' ""
scan "Google Sheet or Drive ID" '[A-Za-z0-9_-]{40,46}' ""
scan "n8n instance URL" '[a-z0-9-]+\.app\.n8n\.cloud' "-i"

if [ -f .blocklist ]; then
  while IFS= read -r term; do
    [ -z "$term" ] || [ "${term#\#}" != "$term" ] && continue
    out=$(echo "$files" | xargs -r grep -n -I -i -F -- "$term" 2>/dev/null)
    [ -n "$out" ] && hit "blocked name: $term" "$out"
  done < .blocklist
else
  echo "Note: no .blocklist file. Make one with your real brand, store and strain names, one per line."
fi

if [ $fail -eq 0 ]; then echo "CLEAN: safe to commit."; else echo "Fix the lines above before you commit."; exit 1; fi
