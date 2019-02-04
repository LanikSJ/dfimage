# Dockerfile From Image (dfimage)
[![Build Status](https://travis-ci.org/LanikSJ/dfimage.svg?branch=master)](https://travis-ci.org/LanikSJ/dfimage)[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=LanikSJ/dfimage)](https://dependabot.com)

Reverse-engineers a Dockerfile from a Docker image.

See my [Inspiration](https://github.com/CenturyLinkLabs/dockerfile-from-image) and [Container Source](https://hub.docker.com/r/chenzj/dfimage/) for more information.

Similar to how the `docker history` command works, the Python script is able to re-create the Dockerfile ([approximately](#limitations)) that was used to generate an image using the metadata that Docker stores alongside each image layer.

## Usage
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5bc4537290504435bce6a3e3ed83101b)](https://app.codacy.com/app/LanikSJ/dfimage?utm_source=github.com&utm_medium=referral&utm_content=LanikSJ/dfimage&utm_campaign=Badge_Grade_Dashboard)[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/60355d4f69bd426689fa6917fc3b8409)](https://www.codacy.com/app/Lanik/dfimage?utm_source=github.com&utm_medium=referral&utm_content=LanikSJ/dfimage&utm_campaign=Badge_Coverage)[![codecov](https://codecov.io/gh/LanikSJ/dfimage/branch/master/graph/badge.svg)](https://codecov.io/gh/LanikSJ/dfimage)

The Python script is itself packaged as a Docker image so it can easily be executed with the Docker _run_ command:

    docker run -v /var/run/docker.sock:/var/run/docker.sock dfimage imageID

The `imageID` parameter is the image ID (either the truncated form or the complete image ID).

Since the script interacts with the Docker API in order to query the metadata for the various image layers it needs access to the Docker API socket.  The `-v` flag shown above makes the Docker socket available inside the container running the script.

Note that the script only works against images that exist in your local image repository (the stuff you see when you type `docker images`). If you want to generate a Dockerfile for an image that doesn't exist in your local repo you'll first need to `docker pull` it.

## Docker Example
[![Docker Repository on Docker Hub](https://img.shields.io/docker/automated/laniksj/dfimage.svg?style=flat)](https://hub.docker.com/r/laniksj/dfimage)[![Docker Repository on Quay](https://quay.io/repository/laniksj/dfimage/status "Docker Repository on Quay")](https://quay.io/repository/laniksj/dfimage)[![Docker Pulls](https://badgen.net/docker/pulls/laniksj/dfimage)](https://hub.docker.com/r/laniksj/dfimage)[![](https://images.microbadger.com/badges/image/laniksj/dfimage.svg)](https://microbadger.com/images/laniksj/dfimage "Get your own image badge on microbadger.com")

Here's an example that shows the official Docker ruby image being pulled and the Dockerfile for that image being generated.

    $ docker pull laniksj/dfimage
    Using default tag: latest
    latest: Pulling from dfimage

    $ alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm laniksj/dfimage"

    $ dfimage imageID
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

## How Does It Work?

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

The output above has been truncated, but nested within the *ContainerConfig* data you'll find the Dockerfile command that generated this layer (in this case it was an `ONBUILD` instruction).

The *entrypoint.py* script works by simply walking backward through the layer tree and collecting the commands stored with each layer. When the script reaches the first tagged layer (or the root of the tree) it stops and displays the (reversed) list of commands. If you want to generate the commands going all the way back to the root image layer you can use the `-f` flag to walk the entire tree.

## Limitations

As the Python script walks the list of layers contained in the image it stops when it reaches the first tagged layer. It is assumed that a layer which has been tagged represents a distinct image with its own Dockerfile so the script will output a `FROM` directive with the tag name.

In the example above, the _ruby_ image contained a layer in the local image repository which had been tagged with _buildpack-deps_ (though it wasn't shown in the example, this likely means that _buildpack-deps:latest_ was also pulled at some point). If the _buildpack-deps_ layer had not been tagged, the Python script would have continued outputting Dockerfile directives until it reached the root layer.

Also note that the output generated by the script won't match exactly the original Dockerfile if either the `COPY` or `ADD` directives (like the example above) are used. Since we no longer have access to the build context that was present when the original `docker build` command was executed all we can see is that some directory or file was copied to the image's filesystem (you'll see the file/directory checksum and the destination it was copied to).

## Extract

If you want to extract a file from a container run this:

    docker run --rm --entrypoint cat imageName /path/to/file > filename

## License
[![GPLv3 license](https://badgen.net/github/license/LanikSJ/dfimage)](http://perso.crans.org/besson/LICENSE.html)
