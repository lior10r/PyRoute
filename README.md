# pyroute

<a name="about"/>

## About
`pyroute` is an exercise that combines networks and python development.

The exercise is separated into stages. Each stage simulates a network of clients that are connected to your computer. Your goal is to write a python script that connects those clients to one another.


<a name="toc"/>

## Table of Contents
- [About](#about)
- [Table of Contents](#toc)
- [Installation](#installation)
- [Run the Exercise](#run)
  - [Start a Stage](#start-a-stage)
  - [Stop a Stage](#stop-a-stage)
  - [Connect to a Client](#connect-to-a-client)
  - [Run Code on the Client](#run-code-on-the-client)
  - [Example Usage](#example-usage)
- [Contribute](#contribute)


<a name="installation"/>

## Installation
Run `install.sh` to install the required dependencies. Before running, make sure you have access to `/mnt/shared/Installs`.

The following steps are performed to makes sure the clients are **not** connected by default:
1. `docker` will be configured with `iptables: false` to prevent new iptables rules. To restore the default `docker` configuration remove that line from `/etc/docker/daemon.json` and restart the `docker` service.
2. Your computer's ip forwarding will be disabled. To enable it use `sudo sysctl net.ipv4.ip_forward=1`.


<a name="run"/>

## Run the Exercise
In order to run the exercise, you first need to `source env.sh`. This will create various useful commands in your environment. This will only change your current terminal. You will have to use it in each shell separately.

You should write your code under `src/`.

<a name="start-a-stage"/>

#### Start a Stage
Use `pyroute-stage-start <stage-name>` to perform the necessary setup to run a stage.
Each stage is a directory in `stages/` and the given `stage-name` should be the name of directory in that path.

The command will:
* Create the **clients** (client1, client2, etc.) that make up the network. Each client is a `docker` container.
* Create the **interfaces** (net1, net2, etc.) through which you will communicate with the clients.

If you have a stage already running, there's no need to worry! The command will stop the old stage before running the new stage's setup.

Notice that the setup process is not instantaneous and might take a while.

<a name="stop-a-stage"/>

#### Stop a Stage
Use `pyroute-stage-stop` to tear down the running stage. The command already knows which stage is running, so no parameter is needed.

<a name="connect-to-a-client"/>

#### Connect to a Client
Use `pyroute-connect <client>` to open the shell of a client. The client names follow this pattern: *client\<n\>* (*client* and then a serial 1-based number). Since each client is a `docker` container, you can also see the available clients using `docker ps`.

<a name="run-code_on_the_client"/>

#### Run Code on the Client
Some stages may require running your own code on the clients. For that purpose, your `src/` directory is accessible inside the clients under `/~/src/`. Notice that it is mounted with both *read* and *write* permissions, so you can edit the code from the client as well.

<a name="example-usage"/>

#### Example Usage
```bash
source env.sh

# Start stage1
$ pyroute-stage-start stage1

# Show the available clients
$ docker ps
      Name          Command    State   Ports
--------------------------------------------
stage1_client1_1   /bin/bash   Up
stage1_client2_1   /bin/bash   Up

# Connect to a client and do stuff
$ pyroute-connect client1
client1$ ping ...
client1$ ...

# Disconnect from client
client1$ exit

# Stop stage1
$ pyroute-stage-stop stage1
```


<a name="contribute"/>

## Contribute
Do you have a great idea for a new stage? Did you find a bug and want to do some maintenance? Or do you just want to know what goes on under the hood?

**This section is for you!**

Each stage is a directory inside `stages/`. Each stage must create multiple scripts:
* `up.sh` - Performs the setup of the stage.
* `down.sh` - Performs the teardown of the stage.
* `connect.sh <client>` - Connects to a client.

All stages (right now, at least) work with `docker-compose` - A docker extension tool to create multi-container applications. The containers and networks are described in a file called `docker-compose.yml`.
Each container uses the latest *pyroute* image. To change it, edit the `Dockerfile` and run:
```bash
docker build . --network host --tag="pyroute"
docker image tag pyroute jaro:1700/pyroute
docker image push jaro:1700/pyroute
```

While the current stage is running, its name is saved in `.stage`. This file is used by all the `pyroute-*` commands. For example, `pyroute-connect` will call the `./stages/<current-stage>/connect.sh`.
