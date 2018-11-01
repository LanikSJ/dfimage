# Dockerfile From Image (dfimage)
[![Build Status](https://travis-ci.org/LanikSJ/dfimage.svg?branch=master)](https://travis-ci.org/LanikSJ/dfimage) [![Docker Repository on Quay](https://quay.io/repository/laniksj/dfimage/status "Docker Repository on Quay")](https://quay.io/repository/laniksj/dfimage)

Inspiration: https://github.com/CenturyLinkLabs/dockerfile-from-image<br/>
Container Source: https://hub.docker.com/r/chenzj/dfimage/

Reverse-engineers a Dockerfile from a Docker image.

Similar to how the `docker history` command works, the Python script is able to re-create the Dockerfile ([approximately](#limitations)) that was used to generate an image using the metadata that Docker stores alongside each image layer.

## Prerequisites

You'll also need to authenticate against ECR as described [here](https://docs.aws.amazon.com/cli/latest/reference/ecr/get-login.html).

## Usage

The Python script is itself packaged as a Docker image so it can easily be executed with the Docker *run* command:

    docker run -v /var/run/docker.sock:/var/run/docker.sock dfimage imageID

The `imageID` parameter is the image ID (either the truncated form or the complete image ID).

Since the script interacts with the Docker API in order to query the metadata for the various image layers it needs access to the Docker API socket.  The `-v` flag shown above makes the Docker socket available inside the container running the script.

Note that the script only works against images that exist in your local image repository (the stuff you see when you type `docker images`). If you want to generate a Dockerfile for an image that doesn't exist in your local repo you'll first need to `docker pull` it.

## Example
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

When an image is constructed from a Dockerfile, each instruction in the Dockerfile results in a new layer. You can see all of the image layers by using the `docker images` command with the (soon-to-deprecated) `--tree` flag.

## Limitations
As the Python script walks the list of layers contained in the image it stops when it reaches the first tagged layer. It is assumed that a layer which has been tagged represents a distinct image with its own Dockerfile so the script will output a `FROM` directive with the tag name.

In the example above, the *ruby* image contained a layer in the local image repository which had been tagged with *buildpack-deps* (though it wasn't shown in the example, this likely means that *buildpack-deps:latest* was also pulled at some point). If the *buildpack-deps* layer had not been tagged, the Python script would have continued outputing Dockerfile directives until it reached the root layer.

Also note that the output generated by the script won't match exactly the original Dockerfile if either the `COPY` or `ADD` directives (like the example above) are used. Since we no longer have access to the build context that was present when the original `docker build` command was executed all we can see is that some directory or file was copied to the image's filesystem (you'll see the file/directory checksum and the destination it was copied to).

## Extract
If you want to extract a file from a container run this:

    docker run --rm --entrypoint cat imageName /path/to/file > filename
