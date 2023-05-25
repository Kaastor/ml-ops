## Tutorial

[Continuous MLOps pipelines: A dive into continuous training automation](https://www.youtube.com/watch?v=p7XkKYvcFhw)

## Flyte Sandbox

The Flyte Sandbox is a fully standalone minimal environment for running Flyte. Basically, flytectl sandbox provides a 
simplified way of running `flyte-sandbox` as a single Docker container running locally.

flytectl sandbox starts a local sandbox environment for Flyte. This is mini-replica of an entire Flyte deployment, 
without the scalability and with minimal extensions. The idea for this environment originated from the desire of the 
core team to make it extremely simple for users of Flyte to try out the platform and get a feel for the user experience, 
without having to understand Kubernetes or dabble with configuration etc. 

#### Install `flytekit`

* `pip install flytekit`
* It will also install `pyflyte`

#### Install `flytectl`

* `curl -sL https://ctl.flyte.org/install | bash`
* `sudo flytectl upgrade`
* Test: `flytectl version`

#### `flytectl` vs `pyflyte`

**pyflyte**: pyflyte is the Python library that provides the core functionality for defining and executing workflows 
using the Flyte platform. It allows you to write workflows, tasks, and dependencies using Python code. 
Pyflyte is typically installed using pip in your Python environment, as mentioned earlier.

**flytectl**: flytectl is a command-line tool provided by Flyte to interact with the Flyte platform and perform 
various administrative tasks. It allows you to manage workflows, tasks, launches, and other operations. 
flytectl provides a convenient interface for interacting with the Flyte backend using commands in the terminal. 
It is separate from the Pyflyte library.

#### Running Flyte Sandbox

* Create sandbox cluster: `flytectl sandbox start`
* Wait for cluster to bootstrap
* You should see a message:
  ```
  👨‍💻 Flyte is ready! Flyte UI is available at http://localhost:30081/console 🚀 🚀 🎉 
  ❇️ Run the following command to export sandbox environment variables for accessing flytectl
  export FLYTECTL_CONFIG=/home/przemek/.flyte/config-sandbox.yaml
  ```

#### Use the Flyte Sandbox to
* Try out Flyte locally using a single Docker command or using flytectl sandbox
* Run regular integration tests for Flyte
* Provide snapshot environments for various Flyte versions, to identify regressions

## Workflows

* Run test workflow: `pyflyte run --remote core/flyte_basics/hello_world.py my_wf`
  * `--remote` flag will run workflow on a cluster
* Run workflow with arguments: `pyflyte run --remote core/flyte_basics/basic_workflow.py my_wf --a 5 --b hello`

### How to know on which project my workflow will run?

Flyte uses the current context to determine the project under which the workflow should be executed.


## [Create Flyte Project](https://docs.flyte.org/projects/cookbook/en/latest/getting_started/creating_flyte_project.html)

* `pyflyte init machine_learning_project`
* Project structure:
  ```
  my_project
  ├── Dockerfile        # Docker image
  ├── LICENSE
  ├── README.md
  ├── docker_build.sh   # Docker build helper script
  ├── requirements.txt  # Python dependencies
  └── workflows
  ├── __init__.py
  └── example.py    # Example Flyte workflows
  ```
* Remove entries from `./workflows/__init__.py` as it can make problems.

### Running workflow locally

```python
if __name__ == "__main__":
    # Execute the workflow, simply by invoking it like a function and passing in the necessary parameters
    print(f"Running wf() { workflow(hyperparameters={}) }")
```

### Running workflow on cluster

* Update `requirements.txt` if needed
* Add changes to `Dockerfile` if needed

#### [Register Workflow](https://docs.flyte.org/projects/cookbook/en/latest/getting_started/package_register.html#iterating-on-a-flyte-project)

* Register all the tasks and workflows contained in the specified directory:
  - `pyflyte register workflows` - [**fast** registration](https://docs.flyte.org/projects/cookbook/en/latest/getting_started/package_register.html#fast-registration)
  - this workflow will be registered under currently used project!

#### [Productionizing your Workflows](https://docs.flyte.org/projects/cookbook/en/latest/getting_started/package_register.html#productionizing-your-workflows)

* `pyflyte package`: packages your tasks and workflows into protobuf format.
* `flytectl register`: registers the Flyte package to the configured cluster.
* Package your Project with pyflyte package: `pyflyte --pkgs workflows package --image ghcr.io/flyteorg/flytekit:py3.9-latest`
* Register with flytectl register: 
 ```
 flytectl register files \
  --project flytesnacks \
  --domain development \
  --archive flyte-package.tgz \
  --version "$(git rev-parse HEAD)"
 ```
