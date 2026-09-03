---
name: metsi-publish-course
description: Version, organize, verify, and publish complete METSI courseware in a public GitHub repository with automatic GitHub Pages deployment. Use when Codex must preserve every generated class and its editable sources in GitHub, add or update a class in the UBA-metsi course repository, generate the whole-course index, install the official Pages Actions workflow, authenticate GitHub safely, create or update the repository, push main, verify the deployment, or report the public course URL.
---

# METSI Publish Course

Publish complete courseware while preserving both editable sources and web artifacts. Default to the public repository `UBA-metsi`, the authenticated GitHub user as owner, branch `main`, and the standard GitHub Pages domain.

## Required workflow

1. Read `references/repository-contract.md` and `references/github-pages-workflow.md` completely.
2. Require a validated package from `$metsi-generate-courseware` or `$metsi-compose-document`. It must contain `index.html`, `metsi.css`, `document.json`, and any referenced media.
3. Prepare or update the course repository locally:

   `python3 scripts/prepare_course_repo.py PACKAGE REPO_DIR --slug CLASS_SLUG --title "CLASS TITLE" --replace`

   Use `--replace` only when intentionally publishing a new version of an existing class. The script archives the previous package instead of discarding it.
4. Run the publication gate:

   `python3 scripts/verify_publishable.py REPO_DIR`

   Stop on missing assets, suspicious credentials, symlinks, oversized files, broken local links, or a missing Pages workflow.
5. Check `gh auth status`. If unauthenticated, run `gh auth login --web --git-protocol https` and let the user complete GitHub's browser authorization. Never request, print, copy, or store a token.
6. Resolve the owner with `gh api user --jq .login`. Do not derive the username from an email address.
7. Inspect the exact repository target, staged files, and remote before the first push. The approved default target is `OWNER/UBA-metsi`, public, branch `main`.
8. Initialize or update Git without rewriting history. Commit the generated change with a specific message such as `Publish clase-03`.
9. If the remote repository does not exist, create it with GitHub CLI as public. If it exists, verify that `origin` points to the same owner and repository before pushing.
10. Enable GitHub Pages with `build_type=workflow`, push `main`, watch the Pages workflow, and verify the returned `html_url` over HTTPS.
11. Report the commit SHA, repository URL, Actions run URL, public course URL, published class URL, and whether the live HTTP check passed.

## Safety rules

- Publish only course artifacts the user authorized. Never add unrelated workspace files.
- Never commit `.env`, credentials, access tokens, private keys, browser state, or local configuration containing secrets.
- Never force-push, delete branches, rewrite history, or overwrite a different remote.
- Never add an open-source or Creative Commons license without an explicit licensing decision. Public visibility does not grant reuse rights.
- Keep image creator and license/terms metadata in the repository.
- Archive a replaced class under `archive/`; do not silently destroy the prior version.
- Treat publication as complete only after GitHub reports a successful Pages deployment and the live URL responds successfully.

## Default project configuration

- Repository: `UBA-metsi`
- Visibility: public
- Default branch: `main`
- Hosting: GitHub Pages through GitHub Actions
- Domain: standard `https://OWNER.github.io/UBA-metsi/`
- Deployment trigger: every push to `main`, plus manual dispatch
