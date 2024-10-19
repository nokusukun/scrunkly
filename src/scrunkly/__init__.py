import contextvars
import os
import subprocess
import sys

def cmd():
    print("Scrunkly")

__env = contextvars.ContextVar("env", default={})
def with_env(envs: dict):
    __env.set(envs)
    return lambda : ...

def __get_envs():
    env = os.environ.copy()
    try:
        return env | __env.get()
    except LookupError:
        return env

def scripts(script_map: dict):
    if len(sys.argv) < 2:
        print("Please provide a script to run")
        for k in script_map.keys():
            print(f"  {k}")
        return
    tool = sys.argv[1]

    def run_script(name, script):
        print(f"Running script: {script}")
        if isinstance(script, str) or callable(script):
            script = [script]
        for s in script:
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