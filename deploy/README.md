Chipzen image for Distill1Bot: stage the context with `git archive HEAD rl chipzen_bot/nlhe deploy | tar -x -C ctx`, then `docker buildx build --platform linux/amd64 --load -f ctx/deploy/Dockerfile -t holdem-rl-distill1 ctx`.

Local protocol test (needs the staged repo on the box): `deploy/run_local_match.sh OPP SEED` runs `deploy/localmatch.py` as a scripted server and plays the image through one full match under the platform limits.
