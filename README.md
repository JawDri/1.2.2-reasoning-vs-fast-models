# Lesson 1.2.2 — Reasoning Models vs Fast Models

Demo code for **Lesson 1.2.2** of *AI Automation: From Scratch* (Module 1).

<!-- links:start -->
<!-- links:end -->

<!-- files:start -->
| File | What it shows | Needs |
|---|---|---|
| [`routing_cost_compare.py`](code/routing_cost_compare.py) | One model for everything ($2,600) vs 3-tier routing ($248.50). Change any assumption with options, `--help`. | nothing (free, offline) |
| [`thinking_tokens_demo.py`](code/thinking_tokens_demo.py) | Live: Haiku 5.5 (low effort) vs Opus 5.5 (high effort): billed vs visible tokens, waiting time, cost. `--dry-run` sends nothing. | API key, a few cents |
<!-- files:end -->

## Get the code
- **Download:** the green **Code** button → **Download ZIP**, then unzip it.
- **Or clone:** `git clone https://github.com/JawDri/1.2.2-reasoning-vs-fast-models.git`

Keep the folder's name as it is: `setup.ps1` and `run.ps1` read the lesson number (1.2.2) from it.

## Run it
Everything is in [`code/README.md`](code/README.md): set up once (`setup.ps1` on Windows, a virtual environment on
Mac / Linux), then run the demos from the `code` folder.

## Your API key stays on your computer
The scripts that call the API read your key from your own key file, outside this folder:
`%USERPROFILE%\.ai-automation-from-scratch\.env` on Windows, `~/.ai-automation-from-scratch/.env` on Mac / Linux.
`code/.env.example` is only the template: never put a real key in it. `.gitignore` keeps `.env` files out of git,
so a fork or a pull request can't carry a key by mistake.
