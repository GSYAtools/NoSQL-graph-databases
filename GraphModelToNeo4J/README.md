## NAME

GraphModel2Neo4J

## TAG

1.0.0

## AUTHOR
Carlos Blanco

## DATE

02-03-2022

## DESCRIPTION
Transform a graph-oriented database model into security policies for Neo4J

# DOCKER

## Build

```
docker build -t graph_model_to_neo4j -f GraphModelToNeo4J.dockerfile .
```

## Run

```
docker run -v $(pwd)/data:/usr/local/src/data/ graph_model_to_neo4j --database "NoSQL-Hospital" --outputfile "securityConfiguration.txt"
```

```
The name of the database
--database "NoSQL-Hospital" 
The name of the outpunt file where to write the security policies
--outputfile "securityConfiguration.txt"
```

## Run in windows

```
docker run -v data:/usr/local/src/data/ graph_model_to_neo4j --database "NoSQL-Hospital" --outputfile "securityConfiguration.txt"
```

The "data" volume is mount here "\\wsl.localhost\docker-desktop-data\version-pack-data\community\docker\volumes\data\_data"


## Submit

```
docker ... --tag 1.0.0
```

