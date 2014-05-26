all: push push-subtree

push:
		git push

push-subtree:
		git subtree push --prefix=R-Extended syntax master

pull-subtree:
		git subtree pull --prefix=R-Extended syntax master --squash
