from sys import argv

from docker import client


class ImageNotFound(Exception):
    """ """

    pass


class MainObj:
    """ """

    def __init__(self):
        super(MainObj, self).__init__()
        self.commands = []
        self.layers_with_images = {}
        self.from_img = None
        self.cli = client.DockerClient(base_url="unix:///var/run/docker.sock")
        self._get_image(argv[-1])
        self.hist = self.cli.api.history(self.img["RepoTags"][0])
        self._get_layers_with_images()
        self._get_from_img()
        self._parse_history()
        self.commands.reverse()
        self._print_commands()

    def _print_commands(self):
        """ """
        for i in self.commands:
            print(i)

    def _get_image(self, repo_tag_or_id):
        """

        :param repo_tag_or_id: 

        """
        repo_tag = (
            repo_tag_or_id if ":" in repo_tag_or_id else f"{repo_tag_or_id}:latest"
        )
        image_id = repo_tag_or_id.lower()
        images = self.cli.api.images()
        for i in images:
            if i["Id"].split(":")[1].lower().startswith(image_id):
                self.img = i
                return
            rt = i["RepoTags"]
            if rt and repo_tag in rt:
                self.img = i
                return
        raise ImageNotFound(
            f"Image {repo_tag} Not Found! "
            f"Please Make Sure You Run docker pull {repo_tag} Beforehand.\n"
        )

    def _get_layers_with_images(self):
        """ """
        images = self.cli.api.images()
        for i in images:
            inspect = self.cli.api.inspect_image(i["Id"])
            try:
                layers = inspect["RootFS"]["Layers"]
            except KeyError:
                continue
            if not layers:
                continue
            last_layer_id = layers[-1]
            try:
                self.layers_with_images[last_layer_id] = i["RepoTags"][0]
            except IndexError:
                pass

    def _insert_step(self, step):
        """

        :param step: 

        """
        if "#(nop)" in step:
            to_add = step.split("#(nop) ")[1]
        else:
            to_add = "RUN {}".format(step)
        to_add = to_add.replace("&&", "\\\n    &&")
        self.commands.append(to_add.strip(" "))

    def _parse_history(self):
        """

        :param rec: Default value = False)

        """
        from_last_created_by = False
        if self.from_img:
            from_hist = self.cli.api.history(self.from_img)
            for i in from_hist:
                from_last_created_by = i["CreatedBy"]
                break

        for i in self.hist:
            if from_last_created_by and i["CreatedBy"] == from_last_created_by:
                break
            self._insert_step(i["CreatedBy"])

        if self.from_img:
            self.commands.append("FROM {}".format(self.from_img))

    def _get_from_img(self):
        """ """
        inspect = self.cli.api.inspect_image(self.img["Id"])
        try:
            layers = inspect["RootFS"]["Layers"]
        except KeyError:
            return
        if layers:
            for layer_id in layers:
                if layer_id in self.layers_with_images:
                    self.from_img = self.layers_with_images[layer_id]
                    break


__main__ = MainObj()
