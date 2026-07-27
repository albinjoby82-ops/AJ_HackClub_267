---
title: Git and GitHub
layout: default
parent: 5. Software
nav_order: 4
---

# Git and GitHub

**Git** records versions of files on your computer. **GitHub** hosts Git repositories so people can collaborate.

## The basic workflow

```text
create branch → edit → review changes → commit → push → pull request
```

- **Branch:** an independent line of work
- **Commit:** a saved checkpoint with a message
- **Push:** upload local commits to the remote repository
- **Pull request:** ask to review and merge one branch into another
- **Merge:** accept the proposed changes

## Safe club workflow

1. Update your local copy.
2. Create a descriptively named branch.
3. Make one related group of changes.
4. Review the changed files.
5. Commit with a message explaining the outcome.
6. Push the branch.
7. Open a pull request and describe what changed and how it was checked.

Do not commit passwords, API keys, Wi-Fi credentials, personal data or large generated files unless the repository explicitly requires them.

## Useful commands

```text
git status
git switch -c docs/my-change
git add path/to/file.md
git commit -m "Improve Arduino setup guide"
git push -u origin docs/my-change
```

`origin` is the usual name for the remote repository. `main` or `master` is commonly the shared default branch, but the repository decides which name it uses.

{: .tip}
> A pull request is the normal way to let someone see your changes and choose whether to accept them.
