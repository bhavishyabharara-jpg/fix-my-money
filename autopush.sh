#!/bin/bash
# Fix My Money — ship whatever Claude has prepared.
#
# Claude writes the day's post into this repo (media/ and queue/) from the cloud, but it
# cannot push: pushing needs your GitHub credential, which lives in your macOS keychain and
# nowhere else. This script is the courier. Run it from cron every few minutes and the
# hand-off happens without anyone watching.
#
# Install (once):
#   chmod +x ~/Documents/Money\ X-Ray/publisher-repo/autopush.sh
#   ~/Documents/Money\ X-Ray/publisher-repo/autopush.sh      # first run caches the token
#   (crontab -l 2>/dev/null; echo "*/10 * * * * $HOME/Documents/Money\ X-Ray/publisher-repo/autopush.sh >> /tmp/fmm-autopush.log 2>&1") | crontab -

set -u
cd "$HOME/Documents/Money X-Ray/publisher-repo" || exit 1

# Nothing new? Say nothing and stop — this runs every ten minutes and should be silent.
git add -A
if git diff --cached --quiet; then
  exit 0
fi

STAMP=$(date -u +%Y-%m-%dT%H:%MZ)
git -c user.name="Bhavishay" -c user.email="bhavishyabharara@gmail.com" \
    commit -q -m "Queue update $STAMP" || exit 1

if git push -q; then
  echo "$STAMP pushed"
else
  # Most likely the credential has lapsed. Leave the commit in place; the next run retries.
  echo "$STAMP PUSH FAILED — run this script by hand once to re-enter your GitHub token"
  exit 1
fi
