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
STAMP=$(date -u +%Y-%m-%dT%H:%MZ)

# Commit local work first, so the rebase below has something to replay cleanly.
git add -A
if ! git diff --cached --quiet; then
  git -c user.name="Bhavishay" -c user.email="bhavishyabharara@gmail.com" \
      commit -q -m "Queue update $STAMP" || exit 1
fi

# The publisher Action commits published.json after every post, so the remote is routinely
# ahead of this machine. Catch up before pushing — without this, every push after a
# successful publish is rejected as non-fast-forward.
if ! PULL_OUT=$(git pull --rebase -q 2>&1); then
  git rebase --abort 2>/dev/null
  if echo "$PULL_OUT" | grep -qiE "resolve host|unable to access|timed out|network|connection"; then
    echo "$STAMP offline — couldn't reach GitHub. Nothing lost; will retry on the next run."
    exit 0
  fi
  echo "$PULL_OUT"
  echo "$STAMP PULL FAILED — remote and local have diverged in a way that needs a human."
  echo "  Try:  cd ~/Documents/Money\\ X-Ray/publisher-repo && git pull --rebase"
  exit 1
fi

# Nothing of our own to send? The pull may still have brought changes down; that's fine.
if git diff --quiet HEAD @{u} 2>/dev/null; then
  exit 0
fi

if git push -q; then
  echo "$STAMP pushed"
else
  echo "$STAMP PUSH FAILED. If it mentions authentication, run this script by hand once to"
  echo "  re-enter your GitHub token. If it mentions fast-forward, run: git pull --rebase"
  exit 1
fi
