# Data Model Compiler CLI

The data model compiler can be run in command line.

```shell
cd data_model_compiler
python compiler.py
```

# API Generator CLI

The API generator can be run in command line.

```shell
cd api_generator
python generator.py
```


# Web Server

The tools can also be run as web server.

1. Install requirements.

```shell
pip install -r requirements.txt
```

2. Run HTTP server.

```shell
cd web
flask run -h <host> -p <port>
```

3. Access the service via `http://<host>[:port]/`.
