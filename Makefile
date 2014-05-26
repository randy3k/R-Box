all:

push:
		git push

subtree-push:
		git subtree push --prefix=R-Extended syntax master

subtree-pull:
		git subtree pull --prefix=R-Extended syntax master --squash
