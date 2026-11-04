# Module 00: Course setup

Read the chapter first: [online](https://claude.ai/artifact/QaCn2vyZC1yRk8qNPC2rzB) or `chapter.html` in this folder. This module installs nothing into DocuMind yet. It gets your machine (or Colab) and your accounts ready, so Module 01 just works.

## Goals
- Tools installed: Python 3.12+, uv, git (and make on Mac).
- Accounts ready: Anthropic API key, OpenAI API key, a free hosted Postgres.
- A filled-in `.env` file that is **never** committed.
- You know the course rhythm: read the chapter → run the lessons → break it → checkpoint.

## Steps (Mac)

```bash
# 1. Get the code
git clone https://github.com/panwars87/sha-genai-learning.git && cd sha-genai-learning

# 2. Tools (Homebrew): uv for Python, make and git usually come with Xcode tools
brew install uv            # or: curl -LsSf https://astral.sh/uv/install.sh | sh
xcode-select --install     # if git/make are missing

# 3. Secrets file
cp .env.example .env       # then open .env and fill it in (chapter section 3)
```

Then run the checks:

| Chapter section | File | What it checks |
|---|---|---|
| 1. How this course works | *(chapter only)* | |
| 2. Tools | `lessons/L01_check_tools.py` | Python version, uv, git, make |
| 3. Keys and accounts | `lessons/L02_check_env_file.py` | Each `.env` name has a value (values are never printed) |
| 4. The documents | `lessons/L03_tour_sample_data.py` | A preview of the made-up invoices and receipts |

```bash
python3 modules/00-course-setup/lessons/L01_check_tools.py
python3 modules/00-course-setup/lessons/L02_check_env_file.py
python3 modules/00-course-setup/lessons/L03_tour_sample_data.py
```

These checks use only the Python standard library, so nothing needs installing first.

## Steps (Google Colab)
Open `colab.ipynb` in Colab (File → Open notebook → GitHub). It walks through the same checks, using **Colab Secrets** (the key icon in the left sidebar) instead of `.env`.

## Checkpoint

<details><summary>1. Why does .env exist, and why is it in .gitignore?</summary>
It keeps secrets out of code and out of git. Once a key is pushed to a repo, treat it as leaked and rotate it.
</details>

<details><summary>2. Which program will read ANTHROPIC_API_KEY and OPENAI_API_KEY?</summary>
Only the LiteLLM gateway. DocuMind itself never sees them (Module 01).
</details>

<details><summary>3. Why do we need Postgres before writing any AI code?</summary>
The gateway stores virtual keys, budgets and spend in it. Later modules also store documents and vectors there.
</details>
