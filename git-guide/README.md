# A guide to `git` use

## General use

#### Create a new repository

#### Add and change remotes

#### Add files and commit your work

#### Commit in patches

## Work with branches

#### Create a new branch

Pull the changes from upstream and checkout the branch you want to branch from
```bash
git pull
git checkout master
```

Create the new branch
```bash
git branch new-branch
git checkout new-branch
```

Or directly create and switch to the new branch with
```bash
git checkout -b new-branch
```

List all the branches created with
```bash
git branch -a
```

#### Merge the branch in master

Checkout the branch you want to merge into
```bash
git checkout master
```

Merge the feature branch to master
```bash
git merge new-branch
```

This might create conflicts in master. I have no idea on proper git workflow, but at this point you could merge master into your branch, solve the conflitcs and then merge yours into master. No differences in the final result, but this way you can check if the merge created problems on your end without messing up master.

#### Update a feature branch

Taken from [this](https://gist.github.com/santisbon/a1a60db1fb8eecd1beeacd986ae5d3ca) gist, thank you!

First we'll update your local master branch. Go to your local project and check out the branch you want to merge into (your local master branch)
```bash
$ git checkout master
```

Fetch the remote, bringing the branches and their commits from the remote repository.
You can use the -p, --prune option to delete any remote-tracking references that no longer exist in the remote. Commits to master will be stored in a local branch, remotes/origin/master
```bash
$ git fetch -p origin
```

Merge the changes from origin/master into your local master branch. This brings your master branch in sync with the remote repository, without losing your local changes. If your local branch didn't have any unique commits, Git will instead perform a "fast-forward".
```bash
$ git merge origin/master
```

Check out the branch you want to merge into
```bash
$ git checkout <feature-branch>
```

Merge your (now updated) master branch into your feature branch to update it with the latest changes from your team.
```bash
$ git merge master
```

This only updates your local feature branch. To update it on GitHub, push your changes.
```bash
$ git push origin <feature-branch>
```

## Useful commands

### `diff`

Official [documentation](https://git-scm.com/docs/git-diff)

Show which files are changed in two branches, use `--stat` for a concise result
```bash
git diff --stat master..branchName
```

<!-- TODO: notes on the order of the branches -->

## Fork a repository

#### Update the forked repository

#### Pull request

