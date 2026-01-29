"""
Dockerfile image parser - Extract Dockerfile commands from a Docker image.

This module provides functionality to reverse-engineer Dockerfile commands
from an existing Docker image by analyzing its layer history.
"""

import sys
from typing import Dict, List, Optional
from docker import DockerClient  # type: ignore
from docker.errors import DockerException  # type: ignore


class ImageNotFound(Exception):
    """Exception raised when a Docker image cannot be found."""
    pass


class DockerfileParser:
    """
    Parse Docker image history to reconstruct Dockerfile commands.
    
    This class analyzes a Docker image's layer history and attempts to
    reconstruct the Dockerfile commands that were used to build it.
    """

    def __init__(self, image_identifier: str):
        """
        Initialize the parser with a Docker image identifier.
        
        Args:
            image_identifier: Docker image name, tag, or ID
            
        Raises:
            ImageNotFound: If the specified image cannot be found
            DockerException: If there's an issue connecting to Docker
        """
        self.commands: List[str] = []
        self.layers_with_images: Dict[str, str] = {}
        self.from_img: Optional[str] = None
        self.image_identifier = image_identifier
        
        # Initialize Docker client
        try:
            self.cli = DockerClient(base_url="unix:///var/run/docker.sock")
        except DockerException as e:
            raise DockerException(f"Failed to connect to Docker daemon: {e}")
        
        # Get the target image
        self.img = self._get_image(image_identifier)
        
        # Get image history
        try:
            self.hist = self.cli.api.history(self.img["RepoTags"][0])
        except (KeyError, DockerException) as e:
            raise DockerException(f"Failed to get image history: {e}")
        
        # Build the command list
        self._get_layers_with_images()
        self._get_from_img()
        self._parse_history()
        self.commands.reverse()

    def print_commands(self) -> None:
        """Print the reconstructed Dockerfile commands."""
        for command in self.commands:
            print(command)

    def get_commands(self) -> List[str]:
        """
        Get the reconstructed Dockerfile commands.
        
        Returns:
            List of Dockerfile commands
        """
        return self.commands.copy()

    def _get_image(self, repo_tag_or_id: str) -> Dict:
        """
        Find and return Docker image information.
        
        Args:
            repo_tag_or_id: Image name, tag, or ID
            
        Returns:
            Dictionary containing image information
            
        Raises:
            ImageNotFound: If image cannot be found
        """
        # Handle default tag if none provided
        repo_tag = repo_tag_or_id if ":" in repo_tag_or_id else f"{repo_tag_or_id}:latest"
        image_id = repo_tag_or_id.lower()
        
        try:
            images = self.cli.api.images()
        except DockerException as e:
            raise DockerException(f"Failed to list Docker images: {e}")
        
        for image in images:
            # Check by image ID (short form)
            if image["Id"].split(":")[1].lower().startswith(image_id):
                return image
            
            # Check by repository tag
            repo_tags = image.get("RepoTags", [])
            if repo_tags and repo_tag in repo_tags:
                return image
        
        raise ImageNotFound(
            f"Image '{repo_tag}' not found! "
            f"Please ensure you run 'docker pull {repo_tag}' beforehand."
        )

    def _get_layers_with_images(self) -> None:
        """Map Docker layers to their corresponding images."""
        try:
            images = self.cli.api.images()
        except DockerException as e:
            raise DockerException(f"Failed to list Docker images: {e}")
        
        for image in images:
            try:
                inspect = self.cli.api.inspect_image(image["Id"])
                layers = inspect["RootFS"]["Layers"]
            except (DockerException, KeyError):
                continue
            
            if not layers:
                continue
            
            # Map the last layer to the image's repository tag
            last_layer_id = layers[-1]
            try:
                repo_tag = image["RepoTags"][0]
                self.layers_with_images[last_layer_id] = repo_tag
            except IndexError:
                pass

    def _insert_step(self, step: str) -> None:
        """
        Process and add a Dockerfile command step.
        
        Args:
            step: Raw command from Docker history
        """
        # Remove Docker's no-operation marker
        if "#(nop)" in step:
            to_add = step.split("#(nop) ", 1)[1]
        else:
            to_add = step
        
        # Format multi-line commands for readability
        to_add = to_add.replace("&&", " \\\n    &&")
        self.commands.append(to_add.strip())

    def _parse_history(self) -> None:
        """Parse the Docker image history and reconstruct commands."""
        # Find the base image's last command to avoid duplication
        from_last_created_by = None
        if self.from_img:
            try:
                from_hist = self.cli.api.history(self.from_img)
                for entry in from_hist:
                    from_last_created_by = entry["CreatedBy"]
                    break
            except DockerException:
                pass

        # Process each layer in the history
        for entry in self.hist:
            # Skip commands that belong to the base image
            if from_last_created_by and entry["CreatedBy"] == from_last_created_by:
                break
            
            self._insert_step(entry["CreatedBy"])

        # Add the FROM instruction
        if self.from_img:
            self.commands.append(f"FROM {self.from_img}")
        else:
            self.commands.append("FROM <base image not found locally>")

    def _get_from_img(self) -> None:
        """Determine the base image for the FROM instruction."""
        try:
            inspect = self.cli.api.inspect_image(self.img["Id"])
            layers = inspect["RootFS"]["Layers"]
        except (DockerException, KeyError):
            return
        
        if not layers:
            return
        
        # Find the first layer that corresponds to a known image
        for layer_id in layers:
            if layer_id in self.layers_with_images:
                possible_from_img = self.layers_with_images[layer_id]
                # Skip if this is the same as our target image
                if possible_from_img == self.img["RepoTags"][0]:
                    continue
                self.from_img = possible_from_img
                break


def entrypoint() -> None:
    """Main entry point for the dfimage tool."""
    if len(sys.argv) < 2:
        print("Usage: python dfimage.py <image_name|image_id>")
        sys.exit(1)
    
    try:
        parser = DockerfileParser(sys.argv[1])
        parser.print_commands()
    except (ImageNotFound, DockerException) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    entrypoint()
