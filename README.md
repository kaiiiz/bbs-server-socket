# bbs-server-socket

This is the course project of Intro. to Network Programming at NCTU in Spring 2020.

In these labs, you'll mainly learn the detail about socket programming. Also, you'll be asked to interact with different services such as Amazon S3, Apache Kafka and database.

## Brief Introduction

Lab1 and Lab2 are basically doing same thing. Just follow the spec and implement related commands.

Lab3: The content of post will be asked to store on client side (Amazon S3 Bucket), only metadata will be stored in database.

Lab4: Implement the subscription features based on Apache Kafka.

## Environment

The following commands are only tested on Linux. Windows or MacOS may need revision.

### Database

Create database on localhost, it's optional if you has database on other machine:

```
$ docker-compose up -d
```

### Amazon

Store your credential in `~/.aws/credentials`.

```
[default]
aws_access_key_id=
aws_secret_access_key=
aws_session_token=
```

### Apache Kafka

Visit [Apache Kafka](https://kafka.apache.org/intro) for more details.

I ran the service on Amazon EC2. Don't forget to allow inbound connections on port 9092 by changing the policy of Amazon Security Groups.

### Python environment

In order to keep my global python environment clean, I use poetry to maintain package dependency. The detail of package dependency, see [pyproject.toml](https://github.com/kaiiiz/bbs-server-socket/blob/master/pyproject.toml).

Start virtual environment:

```
$ poetry shell
```

Install python dependency:

```
$ poetry install
```

### .env

Change the content of [.env](https://github.com/kaiiiz/bbs-server-socket/blob/master/.env) based on your environment.

## Run

Create DB schema and clean up all S3 bucket:

```
$ python bbs_db_schema.py
```

Start server, port has default value specified in `.env`:

```
$ python bbs_server.py {port}
```

Start client:

```
$ python bbs_client.py {server_ip} {server_port}
```

## Implementation

The master branch is the final version of the course project. The source code of different labs is tracked on different branch, checkout to [Lab1](https://github.com/kaiiiz/bbs-server-socket/tree/Lab1), [Lab2](https://github.com/kaiiiz/bbs-server-socket/tree/Lab2), [Lab3](https://github.com/kaiiiz/bbs-server-socket/tree/Lab3), [Lab4](https://github.com/kaiiiz/bbs-server-socket/tree/Lab4) for more details.

### Programming Language

No specific programming language is required in spec. I choose python, you can use C/C++, node.js... as well.

### Database

MariaDB + SQLAlchemy ORM. The schema is defined in [db](https://github.com/kaiiiz/bbs-server-socket/tree/master/db).

### Overall Structure

![](https://i.imgur.com/Rxr6gCv.png)

Server and Client both inherit to same command parser in order to maintain the state of socket.

BBS_Notifier (Producer) and BBS_Subscriber (Consumer) refers to TAs reference design at Lab4.

![](https://i.imgur.com/tX1vXm3.png)
