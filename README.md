# CI/CD with Airflow, dbt, GitHub Actions, and Pytest

This project demonstrates a small end-to-end CI/CD workflow for a data engineering project using Apache Airflow, dbt, PostgreSQL, Docker, GitHub Actions, Pytest, GitHub Environments, and a self-hosted GitHub runner.

The focus of the project is not a complex data pipeline. Instead, it demonstrates how data engineering code can be automatically tested and promoted through development environments.

## Project Goals

This project was created to practice:

- Running Airflow and dbt with Docker
- Orchestrating dbt commands with Airflow
- Testing an Airflow DAG with Pytest
- Validating dbt models during CI
- Running CI with GitHub Actions
- Running CD with GitHub Actions
- Deploying with a self-hosted GitHub runner
- Automatically deploying to DEV
- Promoting the same tested code to UAT
- Requiring manual approval before UAT deployment
- Keeping credentials and runtime configuration out of Git
- Deploying the exact Git commit that passed CI

## Architecture

```text
Developer
    |
    v
Git Push
    |
    v
GitHub
    |
    v
CI Workflow
    |
    +--> Build Airflow Docker image
    |
    +--> Run Airflow DAG tests
    |
    +--> Start PostgreSQL test warehouse
    |
    +--> Run dbt build
    |
    v
CI Passes
    |
    v
DEV Deployment
    |
    v
UAT Approval
    |
    v
UAT Deployment
```

## Repository Structure

```text
CI-CD-Airflow-dbt/
│
├── airflow/
│   ├── dags/
│   │   └── dbt_pipeline.py
│   ├── dbt_profiles/
│   ├── logs/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── dbt_project/
│   ├── models/
│   │   ├── example_model.sql
│   │   └── schema.yml
│   └── dbt_project.yml
│
├── tests/
│   └── test_dbt_pipeline.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── .gitignore
└── README.md
```

## Airflow

Airflow is used as the orchestration layer.

The project contains one DAG:

```text
dbt_ci_cd_pipeline
```

The DAG runs three dbt commands:

```text
dbt_debug
    |
    v
dbt_test
    |
    v
dbt_run
```

This demonstrates the separation of responsibilities between the two tools:

```text
Airflow = orchestration
dbt     = transformation and testing
```

## Airflow DAG Testing

The Airflow DAG is tested with Pytest.

The tests verify that:

- The DAG imports without errors
- The expected DAG exists
- The DAG contains the expected number of tasks
- Task dependencies are correct

The expected dependency structure is:

```text
dbt_debug
    ↓
dbt_test
    ↓
dbt_run
```

Airflow's `DagBag` is used to load the DAG definition directly.

This allows the DAG structure to be tested without actually scheduling or executing the pipeline.

## dbt

The dbt project is intentionally small so that the project can focus on CI/CD behavior.

It contains a simple model:

```text
example_model.sql
```

and model tests defined in:

```text
schema.yml
```

The model is tested with:

- `not_null`
- `unique`

The CI workflow runs:

```bash
dbt build
```

This validates both model execution and dbt tests.

## Docker

Airflow and dbt run inside Docker containers.

The Airflow image is based on:

```text
apache/airflow:3.3.0
```

Additional Python dependencies include:

```text
dbt-core
dbt-postgres
pytest
```

Important dependency versions are pinned so that a new package release does not unexpectedly break the CI pipeline.

## PostgreSQL

The Docker environment contains two PostgreSQL databases with different responsibilities:

```text
PostgreSQL #1
└── Airflow metadata database

PostgreSQL #2
└── dbt test warehouse
```

The dbt warehouse provides a real database against which the CI workflow can execute `dbt build`.

## Continuous Integration

The CI workflow is defined in:

```text
.github/workflows/ci.yml
```

It runs automatically on:

```text
push
pull_request
```

The CI process is:

```text
Checkout repository
        ↓
Create runtime directories
        ↓
Build Airflow Docker image
        ↓
Run Airflow DAG tests
        ↓
Start PostgreSQL warehouse
        ↓
Create temporary dbt profile
        ↓
Run dbt build
```

If any test or validation step fails, CI fails.

## Runtime dbt Configuration

The local dbt `profiles.yml` file is not committed to Git because it may contain environment-specific configuration or credentials.

Instead, GitHub Actions creates a temporary profile during the CI run.

Conceptually:

```text
Git Repository
     X
profiles.yml

GitHub Actions
     |
     v
Create profiles.yml at runtime
```

This keeps runtime configuration separate from source code.

## Continuous Deployment

The CD workflow is defined in:

```text
.github/workflows/cd.yml
```

CD begins only after the CI workflow completes successfully on the `master` branch.

The workflow also checks out the exact commit that passed CI using the workflow run commit SHA.

Conceptually:

```text
Commit ABC123
     |
     v
CI tests ABC123
     |
     v
CI passes
     |
     v
CD deploys ABC123
```

This prevents CI from validating one version of the code while CD deploys another.

## DEV Environment

After CI succeeds, the project is automatically deployed to the DEV environment.

The self-hosted runner copies the Airflow DAG and dbt project to:

```text
C:\Deploy\CI-CD-Airflow-dbt\Dev
```

DEV does not require manual approval.

```text
CI Pass
   |
   v
DEV Deploy
```

## UAT Environment

After DEV deployment succeeds, the workflow proceeds to the GitHub `UAT` environment.

UAT requires manual approval before deployment can continue.

```text
CI
 |
 v
DEV
 |
 v
Wait for Approval
 |
 v
UAT
```

After approval, the same tested commit is deployed to:

```text
C:\Deploy\CI-CD-Airflow-dbt\UAT
```

This demonstrates a basic environment-promotion workflow.

## GitHub Environments

The project uses two GitHub environments:

### DEV

- Automatic deployment
- No approval required

### UAT

- Deployment occurs after DEV
- Manual approval required

GitHub Environments can also be used to manage:

- Environment-specific secrets
- Environment-specific variables
- Deployment protection rules
- Deployment history

## Self-Hosted Runner

Deployment is performed by a GitHub self-hosted runner installed on the Windows development machine.

```text
GitHub Actions
      |
      v
Self-Hosted Runner
      |
      v
C:\Deploy\
```

This allows GitHub Actions to deploy code to infrastructure that GitHub's hosted runners cannot directly access.

## Security and Configuration

Files containing local credentials or generated runtime data are excluded from Git.

Examples include:

```text
.venv/
.env
profiles.yml
Airflow logs
dbt target/
dbt packages
```

The project avoids storing database credentials directly in the repository.

## Important CI/CD Concepts Practiced

### Continuous Integration

Every code change is automatically validated.

```text
Code Change
    |
    v
Automated Tests
    |
    v
Pass / Fail
```

### Continuous Deployment

Code that successfully passes CI can automatically move into a deployment environment.

```text
CI Pass
   |
   v
Deploy
```

### Environment Promotion

The same tested code moves through multiple environments.

```text
DEV
 |
 v
UAT
```

### Approval Gates

Higher environments can require human approval.

```text
DEV
 |
 v
Approval
 |
 v
UAT
```

### Dependency Pinning

Important package versions are pinned so that changes to upstream dependencies do not unexpectedly break CI.

### Runtime Configuration

Environment-specific configuration is generated or injected when the workflow runs instead of being committed to source control.

### Deploying the Tested Commit

CD deploys the exact commit that passed CI rather than simply deploying whatever code happens to be newest.

## Local Commands

From the Airflow directory:

```powershell
cd airflow
```

Build the Docker image:

```powershell
docker compose build
```

Initialize Airflow:

```powershell
docker compose up airflow-init
```

Start the environment:

```powershell
docker compose up -d
```

Run DAG tests:

```powershell
docker compose run --rm --entrypoint pytest airflow-scheduler -v /opt/airflow/tests
```

Run dbt debug:

```powershell
docker compose run --rm --entrypoint bash airflow-scheduler -c "cd /opt/dbt/dbt_project && dbt debug"
```

Run dbt build:

```powershell
docker compose run --rm --entrypoint bash airflow-scheduler -c "cd /opt/dbt/dbt_project && dbt build"
```

## Key Takeaways

The completed project demonstrates this CI/CD flow:

```text
Git
 |
 v
GitHub Actions
 |
 v
CI
 ├── Airflow DAG tests
 └── dbt build validation
 |
 v
DEV
 |
 v
Manual Approval
 |
 v
UAT
```

The project demonstrates how Airflow, dbt, Docker, PostgreSQL, GitHub Actions, Pytest, and GitHub Environments can work together while maintaining clear separation between orchestration, transformation, testing, and deployment.

## Technologies

- Apache Airflow
- dbt Core
- dbt-postgres
- PostgreSQL
- Docker
- Docker Compose
- Git
- GitHub
- GitHub Actions
- GitHub Environments
- GitHub Self-Hosted Runner
- Pytest
- Python
- SQL
- YAML

## Author

**James Bova**

Data Engineering Portfolio

GitHub: https://github.com/JamesBova