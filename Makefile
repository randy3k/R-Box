all:

subpush:
		git subtree push --prefix=syntax git@github.com:randy3k/R-Extended.git master

subpull:
		git subtree pull --prefix=syntax git@github.com:randy3k/R-Extended.git master --squash

syntax:
		Rscript syntax.R

packages:
		sh packages.sh

.PHONY: subpush subpull syntax packages
