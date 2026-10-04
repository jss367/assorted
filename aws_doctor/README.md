# aws-doctor

A no-dependency bash script that tells you, at a glance, whether your AWS
environment is set up correctly — and if not, what's likely fighting with what.

## What it checks

- **Every AWS-related env var** I'm aware of: `AWS_PROFILE`,
  `AWS_DEFAULT_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`,
  `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`,
  `AWS_CREDENTIAL_EXPIRATION`, `AWS_CONFIG_FILE`,
  `AWS_SHARED_CREDENTIALS_FILE`, `AWS_ROLE_ARN`,
  `AWS_WEB_IDENTITY_TOKEN_FILE`, `AWS_ENDPOINT_URL`, `AWS_CA_BUNDLE`,
  `AWS_VAULT`, retry/metadata settings, etc. Secrets are masked.
- **Config files**: `~/.aws/config` and `~/.aws/credentials` (plus any
  `AWS_CONFIG_FILE` / `AWS_SHARED_CREDENTIALS_FILE` overrides), with profile
  listings.
- **Active profile resolution**: which profile wins and why, the resolved
  region and where it came from, SSO config, and any
  `role_arn` / `source_profile` chain.
- **Conflicts and gotchas**:
  - Env credentials set alongside a profile (env wins, profile silently ignored)
  - Half-set credential triplets (key without secret, session token without key)
  - `AWS_PROFILE` vs `AWS_DEFAULT_PROFILE` disagreement
  - `AWS_REGION` vs `AWS_DEFAULT_REGION` disagreement
  - Profile referenced but not defined
  - `AWS_CREDENTIAL_EXPIRATION` in the past
  - Expired SSO cache tokens
  - `AWS_ENDPOINT_URL` redirecting to LocalStack/MinIO
  - Custom config/creds files set but missing
- **Identity check**: runs `aws sts get-caller-identity` if the AWS CLI is
  installed.

Errors / warnings / notes are summarized at the end. Exits non-zero on errors
so it's usable in scripts.

## Install

The script is a single self-contained bash file. Pick whichever install style
you like:

**Run it in place** (no install):

```sh
./aws_doctor/aws-doctor
```

**Make it runnable from anywhere via a symlink:**

```sh
ln -s "$PWD/aws_doctor/aws-doctor" ~/.local/bin/aws-doctor
# or any directory on your PATH
```

(If `~/.local/bin` isn't on your `PATH`, add it to your shell rc:
`export PATH="$HOME/.local/bin:$PATH"`.)

## Usage

```sh
aws-doctor
```

That's it. No flags, no arguments. It prints a structured report and exits
non-zero if there are real errors (so you can wire it into other scripts).

## Requirements

- bash (works on macOS's bash 3.2)
- Optional: AWS CLI (`brew install awscli`) — only needed for the
  `sts get-caller-identity` identity check at the end. Everything else
  works without it.
