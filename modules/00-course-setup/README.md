# Module 00: Course setup

1. Read the chapter: [online](https://claude.ai/artifact/QaCn2vyZC1yRk8qNPC2rzB), or `chapter.html` in this folder.
2. Run the notebook `00-course-setup.ipynb`. It checks your tools, your two API keys (names only, never values) and the sample documents.

## Mac
```bash
brew install uv                      # git comes with: xcode-select --install
git clone https://github.com/panwars87/sha-genai-learning.git && cd sha-genai-learning
cp .env.example .env                 # paste in your Anthropic and OpenAI keys
cd modules/00-course-setup && uvx --from jupyterlab jupyter lab
```

## Colab
File → Open notebook → GitHub → this repo → `00-course-setup.ipynb`. Add `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` as Colab Secrets (the key icon in the left sidebar).

All green? Go to Module 01.
