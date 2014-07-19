all:

push:
		git push

subtree-push:
		git subtree push --prefix=R-Extended git@github.com:randy3k/R-Extended.git master

subtree-pull:
		git subtree pull --prefix=R-Extended git@github.com:randy3k/R-Extended.git master --squash
