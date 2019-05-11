#!/usr/bin/python3

from sys import argv
from docker import Client


class ImageNotFound(Exception):
    pass


class MainObj:
    def __init__(self):
        super(MainObj, self).__init__()
        self.commands = []
        self.cli = Client(base_url='unix://var/run/docker.sock')
        self._get_image(argv[-1])
        self.hist = self.cli.history(self.img['RepoTags'][0])
        self._parse_history()
        self.commands.reverse()
        self._print_commands()

    def _print_commands(self):
        for i in self.commands:
            print(i)

    def _get_image(self, img_hash):
        images = self.cli.images()
        for i in images:
            if img_hash in i['Id']:
                self.img = i
                return
        raise ImageNotFound("Image {} not found\n".format(img_hash))

    def _insert_step(self, step):
        if "#(nop)" in step:
            to_add = step.split("#(nop) ")[1]
        else:
            to_add = ("RUN {}".format(step))
        to_add = to_add.replace("&&", "\\\n    &&")
        self.commands.append(to_add.strip(' '))

    def _parse_history(self, rec=False):
        first_tag = False
        actual_tag = False
        for i in self.hist:
            if i['Tags']:
                actual_tag = i['Tags'][0]
                if first_tag and not rec:
                    break
                first_tag = True
            self._insert_step(i['CreatedBy'])
        if not rec:
            self.commands.append("FROM {}".format(actual_tag))


__main__ = MainObj()
