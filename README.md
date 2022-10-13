# Tazı Project

Objective is to simulate 2 concurrent tasks:

+ Continuosly Growing Datasource, simulating a client's input to our database
+ Confusion Matrix calculations based on sliding window over 1000 predictions from 3 different models

Note: Please check (non-docker branch)[https://github.com/TuanSSM/tazi-project/tree/non-docker] as it is better performing for now.

## Backend

Both tasks run on different threads. Confusion Matrix calculations starts immediately as datastorege gets populated. Confusion Matrix calculation are done whenever it is possible

![endpoints](media/endpoints.png)

Also there is an API support both for new inputs and User Interface. Docs are located at `localhost:8000/docs`
Calculation thread waits for new inputs on Database even after the fixed input (CSV data) has finished 

## UI

On `localhost:8501` there is an interface for visualisation of the given matrix id, and information for the upcoming matrix.

![UI](media/ui.gif)

# How to use it

```console
docker-compose up -d
```

Open your browser and check
+ [localhost:8000](localhost:8000) for backend
+ [localhost:8501](localhost:8501) for frontend

# Todo

+ Docker memory & cpu optimization (especially for postgres)
+ Unit testing
+ Logging
