# Dockerfile From Image (dfimage)

![GitHub Repo Size](https://img.shields.io/github/repo-size/laniksj/dfimage)
![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/laniksj/dfimage)
![GitHub Last Commit](https://img.shields.io/github/last-commit/laniksj/dfimage)
![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/laniksj/dfimage)

-   [Purpose](#purpose)
-   [Usage](#usage)
-   [Docker Example](#docker-example)
-   [How Does It Work](#how-does-it-work)
-   [Limitations](#limitations)
-   [Extract](#extract)
-   [License](#license)
-   [Donate](#donate)

## Purpose

Reverse-engineers a Dockerfile from a Docker image.

See my [Inspiration](https://github.com/CenturyLinkLabs/dockerfile-from-image) and [Container Source](https://hub.docker.com/r/chenzj/dfimage/) for more information.

Similar to how the `docker history` command works, the Python script is able to re-create the Dockerfile ([approximately](#limitations)) that was used to generate an image using the metadata that Docker stores alongside each image layer.

## Usage

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e49393ee816646f28044e4d4f386f5ac)](https://www.codacy.com/gh/LanikSJ/dfimage/dashboard?utm_source=github.com&utm_medium=referral&utm_content=LanikSJ/dfimage&utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/LanikSJ/dfimage/branch/master/graph/badge.svg)](https://codecov.io/gh/LanikSJ/dfimage)

The Python script is itself packaged as a Docker image so it can easily be executed with the Docker _run_ command:

    docker run -v /var/run/docker.sock:/var/run/docker.sock dfimage ruby:latest

The `ruby:latest` parameter is the image name & tag (either the truncated form or the complete image name & tag).

Since the script interacts with the Docker API in order to query the metadata for the various image layers it needs access to the Docker API socket.  The `-v` flag shown above makes the Docker socket available inside the container running the script.

Note that the script only works against images that exist in your local image repository (the stuff you see when you type `docker images`). If you want to generate a Dockerfile for an image that doesn't exist in your local repo you'll first need to `docker pull` it.

## Docker Example

[![Actions Status](https://github.com/LanikSJ/dfimage/workflows/Docker%20Publish/badge.svg)](https://github.com/LanikSJ/dfimage/actions)

Here's an example that shows the official Docker ruby image being pulled and the Dockerfile for that image being generated. Note: A docker tag is required for correct functionality.

    $ docker pull ruby:latest
    latest: Pulling from library/ruby
    ...
    Status: Downloaded newer image for ruby:latest

    $ docker pull ghcr.io/laniksj/dfimage
    Using default tag: latest
    latest: Pulling from dfimage
    ...
    Status: Downloaded newer image for dfimage:latest

    $ alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm ghcr.io/laniksj/dfimage"

    $ dfimage ruby:latest
    FROM buildpack-deps:latest
    RUN useradd -g users user
    RUN apt-get update && apt-get install -y bison procps
    RUN apt-get update && apt-get install -y ruby
    ADD dir:03090a5fdc5feb8b4f1d6a69214c37b5f6d653f5185cddb6bf7fd71e6ded561c in /usr/src/ruby
    WORKDIR /usr/src/ruby
    RUN chown -R user:users .
    USER user
    RUN autoconf && ./configure --disable-install-doc
    RUN make -j"$(nproc)"
    RUN make check
    USER root
    RUN apt-get purge -y ruby
    RUN make install
    RUN echo 'gem: --no-rdoc --no-ri' >> /.gemrc
    RUN gem install bundler
    ONBUILD ADD . /usr/src/app
    ONBUILD WORKDIR /usr/src/app
    ONBUILD RUN [ ! -e Gemfile ] || bundle install --system

## How Does It Work

When an image is constructed from a Dockerfile, each instruction in the Dockerfile results in a new layer. You can see all of the image layers by using the `docker images` command with the (now deprecated) `--tree` flag.

    $ docker images --tree
    Warning: '--tree' is deprecated, it will be removed soon. See usage.
    └─511136ea3c5a Virtual Size: 0 B Tags: scratch:latest
      └─1e8abad02296 Virtual Size: 121.8 MB
        └─f106b5d7508a Virtual Size: 121.8 MB
          └─0ae4b97648db Virtual Size: 690.2 MB
            └─a2df34bb17f4 Virtual Size: 808.3 MB Tags: buildpack-deps:latest
              └─86258af941f7 Virtual Size: 808.6 MB
                └─1dc22fbdefef Virtual Size: 846.7 MB
                  └─00227c86ea87 Virtual Size: 863.7 MB
                    └─564e6df9f1e2 Virtual Size: 1.009 GB
                      └─55a2d383d743 Virtual Size: 1.009 GB
                        └─367e535883e4 Virtual Size: 1.154 GB
                          └─a47bb557ed2a Virtual Size: 1.154 GB
                            └─0d4496202bc0 Virtual Size: 1.157 GB
                              └─5db44b586412 Virtual Size: 1.446 GB
                                └─bef6f00c8d6d Virtual Size: 1.451 GB
                                  └─5f9bee597a47 Virtual Size: 1.451 GB
                                    └─bb98b84e0658 Virtual Size: 1.452 GB
                                      └─6556c531b6c1 Virtual Size: 1.552 GB
                                        └─569e14fd7575 Virtual Size: 1.552 GB
                                          └─fc3a205ba3de Virtual Size: 1.555 GB
                                            └─5fd3b530d269 Virtual Size: 1.555 GB
                                              └─6bdb3289ca8b Virtual Size: 1.555 GB
                                                └─011aa33ba92b Virtual Size: 1.555 GB Tags: ruby:2, ruby:2.1, ruby:2.1.1, ruby:latest

Each one of these layers is the result of executing an instruction in a Dockerfile. In fact, if you do a `docker inspect` on any one of these layers you can see the instruction that was used to generate that layer.

    $ docker inspect 011aa33ba92b
    [{
      . . .
      "ContainerConfig": {
        "Cmd": [
            "/bin/sh",
            "-c",
            "#(nop) ONBUILD RUN [ ! -e Gemfile ] || bundle install --system"
        ],
        . . .
    }]

The output above has been truncated, but nested within the _ContainerConfig_ data you'll find the Dockerfile command that generated this layer (in this case it was an `ONBUILD` instruction).

The _entrypoint.py_ script works by simply walking backward through the layer tree and collecting the commands stored with each layer. When the script reaches the first tagged layer (or the root of the tree) it stops and displays the (reversed) list of commands. If you want to generate the commands going all the way back to the root image layer you can use the `-f` flag to walk the entire tree.

## Limitations

As the Python script walks the list of layers contained in the image it stops when it reaches the first tagged layer. It is assumed that a layer which has been tagged represents a distinct image with its own Dockerfile so the script will output a `FROM` directive with the tag name.

In the example above, the _ruby_ image contained a layer in the local image repository which had been tagged with _buildpack-deps_ (though it wasn't shown in the example, this likely means that _buildpack-deps:latest_ was also pulled at some point). If the _buildpack-deps_ layer had not been tagged, the Python script would have continued outputting Dockerfile directives until it reached the root layer.

Also note that the output generated by the script won't match exactly the original Dockerfile if either the `COPY` or `ADD` directives (like the example above) are used. Since we no longer have access to the build context that was present when the original `docker build` command was executed all we can see is that some directory or file was copied to the image's filesystem (you'll see the file/directory checksum and the destination it was copied to).

## Extract

If you want to extract a file from a container run this:

    docker run --rm --entrypoint cat imageName /path/to/file > filename

## License

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://en.wikipedia.org/wiki/MIT_License)

## Donate

[![Patreon](https://img.shields.io/badge/patreon-donate-red.svg)](https://www.patreon.com/laniksj/overview)
