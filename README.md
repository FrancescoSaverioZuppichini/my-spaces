# My Spaces: self hosting 🤗 spaces

![alt](header.png)

My Spaces allows you to quickly self-host almost any [hugging face space](https://huggingface.co/spaces) wherever you want!

Under the hood we are using docker and [nvidia pytorch containers](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch)
## Getting Started

You can also install the latest version on GitHub

```bash
pip install git+https://github.com/FrancescoSaverioZuppichini/my-spaces
```

TODO

## Run a space!

```bash
my-spaces run https://huggingface.co/spaces/sabre-code/Flower-Classification
```

**The generated Dockerfiles will be inside `~/.my-spaces`**


For each space, we create an docker image, build and run a container