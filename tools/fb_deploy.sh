#!/bin/sh
# Ship the staged tree of this worktree to ~/poker-ai-lab-fb on gb10-d (never touches ~/poker-ai-lab-rl).
set -e
git add -A
git -c core.autocrlf=false archive --format=tar "$(git write-tree)" > /tmp/fb.tar
ssh gb10-d 'mkdir -p ~/poker-ai-lab-fb'
scp -q /tmp/fb.tar gb10-d:/tmp/fb.tar
ssh gb10-d 'cd ~/poker-ai-lab-fb && tar xf /tmp/fb.tar && echo deployed'
