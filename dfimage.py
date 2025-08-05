#!/usr/bin/env python3

import argparse
import logging
import sys
from typing import Any, Dict, List, Optional

import docker
from docker import client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class ImageNotFound(Exception):
    """Custom exception raised when a Docker image is not found."""

    pass


class DockerfileGenerator:
    """
    Generates a Dockerfile-like representation of a Docker image's history.
    """

    def __init__(self, image_name: str, docker_client: client.DockerClient):
        """
        Initializes the DockerfileGenerator with an image name and Docker client.

        Args:
            image_name: The name or ID of the Docker image.
            docker_client: An initialized Docker client instance.
        """
        self.image_name = image_name
        self.cli = docker_client
        self.commands: List[str] = []
        self.layers_with_images: Dict[str, str] = {}
        self.from_img: Optional[str] = None
        self.image_info: Optional[Dict[str, Any]] = None
        self.history_info: Optional[List[Dict[str, Any]]] = None

    def run(self) -> None:
        """
        Executes the steps to generate and print the Dockerfile commands.
        """
        try:
            self._get_image_info()
            self._get_all_layers_with_images()
            self._determine_base_image()
            self._parse_image_history()
            self._print_commands()
        except ImageNotFound as e:
            logging.error(e)
            sys.exit(1)
        except docker.errors.APIError as e:
            logging.error(f"Docker API Error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def _get_image_info(self) -> None:
        """
        Retrieves detailed information about the specified Docker image.

        Raises:
            ImageNotFound: If the image cannot be found locally.
        """
        repo_tag = (
            self.image_name if ":" in self.image_name else f"{self.image_name}:latest"
        )
        image_id_prefix = self.image_name.lower()

        all_images = self.cli.api.images()
        for img in all_images:
            # Check by full image ID prefix
            if img["Id"].split(":")[1].lower().startswith(image_id_prefix):
                self.image_info = img
                break
            # Check by RepoTags
            if img["RepoTags"] and repo_tag in img["RepoTags"]:
                self.image_info = img
                break

        if not self.image_info:
            raise ImageNotFound(
                f"Image '{repo_tag}' or ID '{self.image_name}' not found locally. "
                f"Please ensure you run 'docker pull {repo_tag}' beforehand."
            )

        self.history_info = self.cli.api.history(
            self.image_info["RepoTags"][0]
            if self.image_info["RepoTags"]
            else self.image_info["Id"]
        )

    def _get_all_layers_with_images(self) -> None:
        """
        Populates a dictionary mapping layer IDs to their corresponding image tags.
        This helps in identifying base images.
        """
        all_images = self.cli.api.images()
        for img in all_images:
            try:
                inspect_data = self.cli.api.inspect_image(img["Id"])
                layers = inspect_data.get("RootFS", {}).get("Layers")
                if layers:
                    last_layer_id = layers[-1]
                    if img["RepoTags"]:
                        self.layers_with_images[last_layer_id] = img["RepoTags"][0]
            except docker.errors.APIError as e:
                logging.warning(f"Could not inspect image {img.get('Id', 'N/A')}: {e}")
            except KeyError:
                # RootFS or Layers might be missing for some image types
                continue

    def _determine_base_image(self) -> None:
        """
        Determines the base image (FROM instruction) for the current image
        by inspecting its layers and comparing them with known image layers.
        """
        if not self.image_info:
            return

        inspect_data = self.cli.api.inspect_image(self.image_info["Id"])
        layers = inspect_data.get("RootFS", {}).get("Layers")

        if layers:
            for layer_id in layers:
                if layer_id in self.layers_with_images:
                    possible_from_img = self.layers_with_images[layer_id]
                    # Ensure the found image is not the image itself
                    if (
                        self.image_info["RepoTags"]
                        and possible_from_img == self.image_info["RepoTags"][0]
                    ):
                        continue
                    self.from_img = possible_from_img
                    break

    def _insert_command_step(self, step_content: str) -> None:
        """
        Formats and adds a command step to the list of Dockerfile commands.

        Args:
            step_content: The raw 'CreatedBy' string from image history.
        """
        if "#(nop)" in step_content:
            # Extract the actual command from '#(nop) CMD ["/bin/sh", "-c", "..."]'
            to_add = step_content.split("#(nop) ", 1)[1]
        else:
            to_add = step_content

        # Format '&&' for multi-line commands in Dockerfile
        to_add = to_add.replace("&&", "\\\n    &&")
        self.commands.append(to_add.strip())

    def _parse_image_history(self) -> None:
        """
        Parses the image history to extract Dockerfile commands.
        """
        if not self.history_info:
            return

        # Find the 'CreatedBy' of the last layer of the base image
        base_image_last_created_by: Optional[str] = None
        if self.from_img:
            try:
                from_hist = self.cli.api.history(self.from_img)
                if from_hist:
                    base_image_last_created_by = from_hist[0]["CreatedBy"]
            except docker.errors.APIError as e:
                logging.warning(
                    f"Could not get history for base image {self.from_img}: {e}"
                )

        # Iterate through the current image's history
        for entry in self.history_info:
            if (
                base_image_last_created_by
                and entry["CreatedBy"] == base_image_last_created_by
            ):
                break  # Stop when we reach the base image's last layer
            self._insert_command_step(entry["CreatedBy"])

        # Add the FROM instruction
        if self.from_img:
            self.commands.append(f"FROM {self.from_img}")
        else:
            self.commands.append("FROM <base image not found locally>")

        self.commands.reverse()  # Commands are in reverse order from history

    def _print_commands(self) -> None:
        """
        Prints the generated Dockerfile commands to stdout.
        """
        for cmd in self.commands:
            print(cmd)


def entrypoint() -> None:
    """
    Main entry point for the dfimage script.
    Parses arguments and initiates the Dockerfile generation.
    """
    parser = argparse.ArgumentParser(
        description="Generate a Dockerfile-like representation from a Docker image."
    )
    parser.add_argument(
        "image",
        type=str,
        help="The name or ID of the Docker image (e.g., 'ubuntu:latest' or 'abcdef123456')",
    )
    args = parser.parse_args()

    try:
        # Initialize Docker client
        docker_client = client.DockerClient(base_url="unix:///var/run/docker.sock")
        # Test connection
        docker_client.ping()
    except docker.errors.APIError as e:
        logging.error(f"Could not connect to Docker daemon: {e}")
        logging.error("Please ensure Docker is running and accessible.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while connecting to Docker: {e}")
        sys.exit(1)

    generator = DockerfileGenerator(args.image, docker_client)
    generator.run()


if __name__ == "__main__":
    entrypoint()
