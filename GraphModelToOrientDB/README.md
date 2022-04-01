## NAME

GraphModelToOrientDB

## TAG

1.0.0

## AUTHOR
Carlos Blanco

## DATE

31-03-2022

## DESCRIPTION
Transform a graph-oriented database model into security policies for OrientDB


## Run in python
```
python.exe .\graph_model_to_orientdb.py --database NoSQL-Hospital --outputfile securityConfiguration.txt
```

```
python3 graph_model_to_orientdb.py --database NoSQL-Hospital --outputfile securityConfiguration.txt
```


>--database   The name of the database 

>--outputfile   The name of the output file where to write the security policies. It is generated in "data" subfolder

# DOCKER

## Build

```
docker build -t graph_model_to_orientdb -f GraphModelToOrientDB.dockerfile .
```

## Run

```
docker run -v $(pwd)/data:/usr/local/src/data/ graph_model_to_orientdb --database "NoSQL-Hospital" --outputfile "securityConfiguration.txt"
```


## Run (in windows)

```
docker run -v data:/usr/local/src/data/ graph_model_to_orientdb --database "NoSQL-Hospital" --outputfile "securityConfiguration.txt"
```

The "data" volume is mount here "\\wsl.localhost\docker-desktop-data\version-pack-data\community\docker\volumes\data\_data"


## Submit

```
docker ... --tag 1.0.0
```

