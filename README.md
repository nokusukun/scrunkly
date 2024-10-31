# Scrunkly

Scrunkly is a lightweight Python utility for defining and running scripts through a flexible command-line interface. It allows users to organize commonly used scripts into an easily maintainable dictionary, making script execution and management simpler.

## Features
- **Script Management**: Define scripts in a dictionary and run them via command line.
- **Sub-Scripts**: Chain scripts together and run them in sequence.
- **Error Handling**: Detect self-referencing scripts and prevent infinite loops.
- **Flexible Scripting**: Supports both string-based and callable scripts.

## Installation

You can install the required dependencies with `pipenv`:

```bash
pip install scrunkly
```

## Usage

Define your scripts in a dictionary and pass it to `scrunkly.scripts`. You can map script names to shell commands or Python functions. Sub-scripts are supported, allowing a script to trigger other scripts in the map.

Here's an example usage:

```python
# run.py
from scrunkly import scripts, py

def get_available_port() -> int:
    ...

def instructions():
    ...

scripts({
    "api:prod": f"{py} -m uvicorn api:app --host 0.0.0.0 --port {get_available_port()}",
    "api:dev": f"{py} -m uvicorn api:app --reload",
    "worker": f"{py} worker-runner.py",
    "install": f"{py} -m pipenv install",
    "mongo:dev": "docker run -d --name api-dev -p 27017:27017 mongo",
    "data-import": f"{py} ./scripts/part_data_import.py",
    "setup:dev": ["mongo:dev", "data-import", instructions],
})
```

### Running a Script

You can run a script by providing its name as a command-line argument:

```bash
scrunkly api:dev
-- or --
python run.py api:dev
```

This will execute the corresponding script, such as starting the API in development mode using Uvicorn.

### Chaining Scripts

You can chain multiple scripts together using a list of script names. For example, the `setup:dev` script runs two scripts: `mongo:dev` and `data-import`:

```bash
scrunkly setup:dev
-- or --
python run.py setup:dev
```

### Environment Variables

Environment variables can be loaded in through the `with_env` method. It will check for environment variables in the following order:

* os.environ
* .env
* with_env

```python
import scrunkly
from scrunkly import with_env, py

dev_env = with_env({
    "DEBUG": "1",
    "MONGO_DB_URI": "mongodb://localhost:27017",
    "MESSAGING_URL": "mongodb://localhost:27017",
    "MONGO_DB_NAME": "test",
    "AWS_REGION": "ap-southeast-2",
    "AWS_S3_BUCKET_NAME": "test-...",
    "AWS_ACCESS_KEY_ID": "AKI...",  # these only have access to test buckets
    "AWS_SECRET_ACCESS_KEY": "eyFi7...",
})

prod_env = with_env({
    "DEBUG": "0",
    "MONGO_DB_NAME": "prod",
    "AWS_REGION": "ap-southeast-2",
    "AWS_S3_BUCKET_NAME": "prod-...",
})

scrunkly.scripts({
    "api:dev": [dev_env, f"""{py} -m watchfiles --filter python "uvicorn api.api:app --port 8001" ."""],
    "api:prod": [prod_env, f"{py} -m uvicorn api.api:app --host 0.0.0.0 --port 8080"],
    "reqs:generate": f"{py} -m  pipreqs.pipreqs . --force",
    "worker": f"{py} ./run_worker.py",
    "install:dev": f"{py} -m pip install -r dev-requirements.txt",
    "install:app": f"{py} -m pip install -r requirements.txt",
    "load-data": f"{py} ./scripts/part_data_import.py --force",
    "install": ["install:dev", "install:app", "load-data"],
    "api:compose:rebuild": "docker-compose up -d --no-deps --build api",
    "worker:compose:rebuild": "docker-compose up -d --no-deps --build worker",
    "up:prod": "docker-compose up -d --scale worker=10",
    "up:prod:full": "docker-compose up -d --scale worker=10 --build",
})

```

## Contributing

Feel free to fork this repository and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License.

---

Happy scripting with Scrunkly!
