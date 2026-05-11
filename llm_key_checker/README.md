# llm-keys

A no-dependency Python script that tells you, at a glance, which LLM provider
API keys are configured on this machine — and what's behind each one.

Useful when you sit down at a computer (or your own) and think "I don't know
what's set up here." It looks in every plausible hiding spot, recognizes keys
by both env-var name and value shape, and (optionally) probes a free metadata
endpoint per provider to confirm the key actually works and report the account
behind it.

## What it finds

For each of these providers:

Anthropic, OpenAI, OpenRouter, xAI (Grok), Google Gemini, Groq, Mistral,
DeepSeek, Together, Hugging Face, Replicate, Cohere, Perplexity, Fireworks.

…it reports:

- whether a key is present
- where it was found (env, which rc/.env file, which provider config dir, or
  macOS Keychain service name)
- a masked preview of the value (first 8 + last 4 chars)
- any comments you wrote above the export line as a **note** (e.g. if your
  `~/.credentials` has `# AE Studio Alignment Team key` above an `export
  ANTHROPIC_API_KEY=…`, that line shows up as the key's note)
- a warning if multiple distinct keys exist for the same provider
- if probing is on: whether the key authenticates, plus whatever the provider
  exposes for free — number of accessible models, account/org/user name,
  OpenRouter usage/limit, Hugging Face username + orgs + token role, etc.
  Perplexity is intentionally not probed (no free metadata endpoint, and
  every authenticated call is billable).

## Where it looks

- The current shell environment (`os.environ`)
- Shell rc files: `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, `~/.zlogin`,
  `~/.bashrc`, `~/.bash_profile`, `~/.profile`,
  `~/.config/fish/config.fish`
- Curated "secrets-style" dotfiles at `$HOME`: `.env`, `.envrc`,
  `.credentials`, `.api_keys`, `.apikeys`, `.secrets`, `.tokens`,
  `.env.local`, `.env.secrets`
- `.env` / `.envrc` / `.env.local` one level deep under `~/git`,
  `~/Documents`, `~/Projects`, `~/src`, `~/code`, `~/work`, `~/Developer`
  (skip hidden dirs; don't recurse further)
- Per-provider config files (e.g. `~/.cache/huggingface/token`,
  `~/.config/openai/`, `~/.anthropic/`)
- macOS Keychain — best-effort lookup of known service names
- Any extra path you pass via `--paths` (file or directory)

Keys are recognized by **both** value pattern (`sk-ant-…`, `sk-or-v1-…`,
`xai-…`, `AIza…`, `hf_…`, `gsk_…`, etc.) **and** env-var name
(`*_API_KEY`, `*_TOKEN`). Patterns are tried most-specific first so `sk-ant-`
doesn't get misclassified as OpenAI.

## What it doesn't find

- OAuth session tokens (e.g. the credential Claude Code stores under the
  `Claude Code-credentials` Keychain entry) — those aren't raw API keys.
- Keys stashed in password managers (1Password, Bitwarden, etc.) that aren't
  also synced to the macOS Keychain.
- Non-LLM API keys — AWS, GitHub, Stripe, Slack, etc. are deliberately
  filtered out to keep the report focused.

## Install

The script is a single self-contained Python 3 file (stdlib only).

**Run it in place:**

```sh
./llm_key_checker/llm-keys
```

**Symlink onto your PATH:**

```sh
ln -s "$PWD/llm_key_checker/llm-keys" ~/.local/bin/llm-keys
```

## Usage

```sh
llm-keys                  # discover + probe (hits ~14 metadata endpoints)
llm-keys --no-probe       # discover only; no network
llm-keys --json           # JSON output for scripting
llm-keys --paths ~/work ~/.my-secrets   # also scan extra dirs / files
llm-keys --no-keychain    # skip macOS Keychain lookups
llm-keys --no-color       # disable ANSI color
```

The default run takes ~1–2 seconds. Probes run concurrently with a 6-second
timeout each.

## Output safety

Key values are always masked in the output. Full values are never printed,
logged, or written anywhere. The script also exits cleanly (status 0) — it's
a discovery tool, not a check.

## Requirements

- Python 3.9+ (uses `tuple[str, ...]` typing)
- `security` CLI on macOS (built in) — only needed for Keychain lookups
