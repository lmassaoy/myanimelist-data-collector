# Web Scrap & Analysis from [![mal-logo-README.png](devops/volume/images/myanimelist_logo.png)](devops/volume/images/myanimelist_logo.png)

## Scrap status:

### Anime

|Data|Status|
|-|-|
|Titles|OK|
|Synopsis|OK|
|Information|OK|
|Statistics|OK|
|Characters Data|Pending|
|Voice Actors Data|Pending|
|Episodes Data|Pending|

### Manga

|Data|Status|
|-|-|
|Titles|Pending|
|Synopsis|Pending|
|Information|Pending|
|Statistics|Pending|
|Characters Data|Pending|
|Charpters Data|Pending|

## Analysis

![jupy-docker-README.png](devops/volume/images/jupy-docker.png)

To start the analysis on your own, you'll need to have a Docker instance installed and running in your PC.

Once it's ready:
1) start the docker-compose
    ```
    $ docker-compose up -d
    ```
2) run & copy the token from the logs:
    ```
    $ docker logs jupy
    ```
3) open your favorite browser and type:
    ```
    htttp://localhost:10000
    ```
4) choose a notebook or create one for yourself and start the analysis

## Web scrap job

![python-docker-README.png](devops/volume/images/python-docker.png)


***Important:*** *Remember to interval the scraps to do not badly influence other users' experiences while navigating the website. Thank you!* ![blink-emoji-README.png](devops/volume/images/blink_emoji.png)

This job can be executed directly in your workstation or as a container.

To run it locally, you just need to run as a normal python job, passing the start and end ID as arguments:

```

$ python3 code/python/data-collector.py -s 1 -e 42000

```

To run it as a container, you'll need to have a Docker instance installed and running in your PC.

The steps are:

1) build the docker image
    ```
    $ docker build -t mal-data-collector:latest -f devops/Dockerfile.DataCollector
    ```
2) start the docker-compose
    ```
    $ docker-compose up -d
    ```