PHONY: clean all

build-and-push-base-image:
	docker build -t my-spaces:base -f ./dockerfiles/Dockerfile.base .
	docker tag my-spaces:base zuppif/my-spaces:base
	docker push zuppif/my-spaces:base