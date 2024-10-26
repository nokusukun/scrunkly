import contextvars
import os
import subprocess
import sys

def if_file_exists(file: str):
    return os.path.isfile(file)

def cmd():
    sys.path.append(os.getcwd())
    try:
        import scripts
    except ImportError:
        ...

    try:
        import run
    except ImportError:
        print("No scripts.py or run.py found")
        sys.exit(1)


__env = contextvars.ContextVar("env", default={})
def with_env(envs: dict):
    return lambda : __env.set(envs)


def __get_envs():
    env = os.environ.copy()
    try:
        return env | __env.get()
    except LookupError:
        return env

def scripts(script_map: dict):
    if len(sys.argv) < 2:
        print("Please provide a script to run")
        for k, script in script_map.items():
            print(f"  {k}")
            print(f"    - {script}")
        return
    tool = sys.argv[1]

    def run_script(name, script_):
        print(f"Running script: {script_}")
        if isinstance(script_, str) or callable(script_):
            script_ = [script_]
        for s in script_:
            if s in script_map:
                if s == name:
                    raise Exception("Cannot call self-referencing script")
                print(f"Running sub-script: {s}")
                run_script(s, script_map[s])
                continue

            if len(sys.argv) - 2 > 0:
                if callable(s):
                    s(*sys.argv[2:])
                else:
                    subprocess.run(s.format(*sys.argv[2:]), env=__get_envs(), shell=True)
            else:
                if callable(s):
                    s()
                else:
                    subprocess.run(s, env=__get_envs(), shell=True)

    run_script(tool, script_map[tool])

py = sys.executable
args = sys.argv[1:]