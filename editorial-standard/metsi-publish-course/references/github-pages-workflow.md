# GitHub Pages workflow

## Authentication and owner

Use GitHub CLI. The configured email is not a GitHub owner identifier.

```bash
gh auth status
gh auth login --web --git-protocol https
gh api user --jq .login
```

Never accept a personal access token in chat or commit one to the repository.

## Repository creation

After preparing, verifying, initializing, and committing the local repository:

```bash
gh repo create OWNER/UBA-metsi --public --source REPO_DIR --remote origin
git -C REPO_DIR push -u origin main
```

If the repository already exists, use `gh repo view OWNER/UBA-metsi` and verify `git remote get-url origin`; never recreate it or replace a mismatched remote.

## Pages configuration

Use a custom GitHub Actions workflow. The included workflow follows the current official static-site pattern:

- `actions/checkout@v6`
- `actions/configure-pages@v5`
- `actions/upload-pages-artifact@v4`
- `actions/deploy-pages@v4`
- `pages: write` and `id-token: write`
- `github-pages` environment

Create or update the Pages site through the REST API:

```bash
gh api --method POST repos/OWNER/UBA-metsi/pages -f build_type=workflow
gh api --method PUT repos/OWNER/UBA-metsi/pages -f build_type=workflow
```

Use POST only when Pages does not exist and PUT when it already exists.

## Verification

```bash
gh run list --repo OWNER/UBA-metsi --workflow deploy-pages.yml --limit 1
gh run watch RUN_ID --repo OWNER/UBA-metsi --exit-status
gh api repos/OWNER/UBA-metsi/pages --jq .html_url
```

Then request the returned HTTPS URL and the class URL. A pushed commit without a successful deployment is not complete.

Official references:

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/rest/pages/pages
- https://cli.github.com/manual/gh_repo_create
