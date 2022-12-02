import logging
import sys
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from typing import List, Optional, Set

import docker
import typer
from docker.models.containers import Container
from docker.models.images import Image
from docker.types import DeviceRequest
from jinja2 import Template

logging.basicConfig(level=logging.INFO)

app = typer.Typer()
ORGANIZATION = "zuppif"


@dataclass
class LocalSpaceFolder:
    root: Path = Path.home() / ".my-spaces"

    def __post_init__(self):
        self.root.mkdir(exist_ok=True)
        self.dockerfiles_root = self.root / "dockerfiles"
        self.dockerfiles_root.mkdir(exist_ok=True)


@dataclass
class LocalSpace:
    client: docker.DockerClient
    image: str
    tag: str

    def __post_init__(self):
        self.container = self.maybe_find_container()

    def maybe_find_container(self) -> Optional[Container]:
        containers: List[Container] = self.client.containers.list(all=True)
        for container in containers:
            tags = container.image.tags
            for tag in tags:
                if tag == f"{self.image}:{self.tag}":
                    return container

    def build_dockerfile(
        self, repo_url: str, template_path: Path, out_dir: Path
    ) -> Path:
        with template_path.open("r") as f:
            template = Template(f.read())
            template_out_path = out_dir / f"Dockerfile.{self.tag}"
            template_out_path.write_text(template.render(dict(repo_url=repo_url)))
        return template_out_path

    def build(self, repo_url: str, template_path: Path, out_dir: Path):
        dockerfile_path = self.build_dockerfile(repo_url, template_path, out_dir)
        with dockerfile_path.open("rb") as f:
            image, logs = self.client.images.build(
                path=str(out_dir), fileobj=f, tag=f"{self.image}:{self.tag}"
            )
        return logs

    def run(self):
        container: Container = self.client.containers.run(
            f"{self.image}:{self.tag}",
            detach=True,
            environment={"HUGGING_FACE_HUB_TOKEN": environ["HUGGING_FACE_HUB_TOKEN"]},
            ipc_mode="host",
            network_mode="host",
            device_requests=[DeviceRequest(capabilities=[["gpu"]])],
            stop_signal="SIGINT",
        )
        return container

    def stop(self):
        if self.container:
            self.container.stop()

    def start(self, force_run: bool = False):
        if force_run:
            if self.container:
                self.container.remove()
            self.container = None
        if self.container:
            self.container.start()
        else:
            self.container = self.run()
        return self.container

    @classmethod
    def from_repo_url(cls, repo_url: str, client: docker.DockerClient):
        tag = Path(repo_url).parts[-1]
        image = f"my-spaces"
        return cls(client, image, tag)


@dataclass
class LocalSpaces:
    folder: Optional[LocalSpaceFolder] = None
    template_path: Optional[Path] = None
    spaces: List[LocalSpace] = field(default_factory=list)

    def __post_init__(self):
        self.folder = LocalSpaceFolder() if self.folder is None else self.folder
        self.template_path = (
            Path(__file__).parent / "templates" / "Dockerfile"
            if self.template_path is None
            else self.template_path
        )
        self.client = docker.from_env()

    def run(self, idenfitier: str, force_run: bool = False):
        is_image_link = f"{ORGANIZATION}/" in idenfitier
        if is_image_link:
            # in this case, we just pull it
            image, tag = idenfitier.split(":")
            self.client.images.pull(image, tag=tag)
            self.space = LocalSpace(self.client, image, tag)
        else:
            # identifier must be a link to a girhub repo, so we create the image
            self.space = LocalSpace.from_repo_url(idenfitier, self.client)
            images: Set = set()
            # let's check if we had build it before
            for image in self.client.images.list():
                for tag in image.tags:
                    images.add(tag)
            if not f"{self.space.image}:{self.space.tag}" in images:
                logging.info(f"🔨 Building {self.space.image}:{self.space.tag} ...")
                logs = self.space.build(
                    idenfitier, self.template_path, self.folder.dockerfiles_root
                )
                for chunk in logs:
                    if "stream" in chunk:
                        for line in chunk["stream"].splitlines():
                            logging.info(f"\t{line}")
                logging.info("🔨 Done! ")
        logging.info("🚀 Running ...")
        container = self.space.start(force_run)
        logging.info("🐋 Log from container: ")
        for line in container.logs(stream=True):
            logging.info(f"\t{line.strip().decode('utf-8')}")

    def stop(self):
        logging.info("🛑 Stopping container ... ")
        self.space.stop()
        logging.info("👋 Done! ")

    def list(self) -> List[str]:
        images: List[Image] = self.client.images.list(name=f"{ORGANIZATION}/my-spaces")
        local_images: List[Image] = self.client.images.list(name=f"my-spaces")
        images += local_images
        # tags is my-space:asdsadsadas
        return [image.tags[0].split(":")[-1] for image in images]


@app.command()
def list():
    local_spaces = LocalSpaces(LocalSpaceFolder(root=Path("./my-spaces")))
    logging.info("👇 Current spaces:")
    logging.info("- \n".join(local_spaces.list()))


@app.command()
def run(
    identifier: str,
    force_run: bool = typer.Option(
        default=False,
        help="Will remove the previous container and re-run it from scratch. Useful if something went wrong (e.g. you hit ctrl+c while it was downloading stuff.",
    ),
):
    try:
        local_spaces = LocalSpaces(LocalSpaceFolder())
        local_spaces.run(identifier, force_run)
    except KeyboardInterrupt:
        local_spaces.stop()
        sys.exit()


def main():
    app()


if __name__ == "__main__":
    main()
