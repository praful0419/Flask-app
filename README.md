# Flask CI/CD Pipeline — Jenkins, Docker, AWS ECR, EC2

An end-to-end CI/CD pipeline that automatically builds, tests, and deploys a containerized Flask application to AWS whenever code is pushed to GitHub.

## Architecture

```
GitHub (push to main)
        │
        ▼
   Jenkins Server (EC2)
        │
        ├─► Build Docker image
        ├─► Push image to Amazon ECR
        └─► SSH into Deploy EC2
                 │
                 ├─► Pull latest image from ECR
                 ├─► Stop & remove old container
                 └─► Run new container
```

## Tech Stack

- **Application**: Python (Flask), served via Gunicorn
- **Containerization**: Docker
- **CI/CD**: Jenkins (Declarative Pipeline)
- **Image Registry**: Amazon ECR
- **Compute**: AWS EC2 (Jenkins host + separate deployment host)
- **Version Control**: Git / GitHub (webhook-triggered builds)

## What This Project Demonstrates

- Writing a multi-stage Jenkins Declarative Pipeline (`Jenkinsfile`)
- Building and tagging Docker images with build-specific and `latest` tags
- Authenticating Docker with AWS ECR and pushing private images
- Automating remote deployment via SSH from Jenkins to a separate EC2 instance
- Zero-downtime-style container replacement (stop → remove → run new)
- Automated post-deploy health verification (pipeline fails if `/health` doesn't respond)
- Real-world troubleshooting: resolving Jenkins node disk-threshold failures (tmpfs sizing), Docker permission errors (`usermod -aG docker`), and SSH publickey authentication issues between Jenkins and EC2

## Pipeline Stages

| Stage | What it does |
|---|---|
| Checkout | Pulls latest code from GitHub `main` branch |
| Build Docker Image | Builds the Flask app into a Docker image |
| Login to ECR | Authenticates Docker with AWS ECR using AWS CLI |
| Tag & Push to ECR | Tags image with build number + `latest`, pushes both to ECR |
| Deploy to EC2 | SSHes into deployment EC2, pulls the new image, restarts the container |
| Verify Deployment | Curls `/health` endpoint to confirm the new container is serving traffic |

## Application Endpoints

- `GET /` — returns a JSON message, app version, and container hostname
- `GET /health` — returns `{"status": "healthy"}`, used for deployment verification

## Setup Notes

- Jenkins requires the **SSH Agent Plugin** for remote deployment
- The `jenkins` user must be a member of the `docker` group on the Jenkins host
- The deployment EC2's user (e.g. `ubuntu` or `ec2-user`) must also be in the `docker` group
- SSH credentials for the deploy EC2 are stored in Jenkins Credentials Manager (not hardcoded)
- Security groups: Jenkins host needs outbound access to GitHub/ECR; deploy EC2 needs inbound access on the app port (5000) and SSH (22) from the Jenkins host

## Future Improvements

- Migrate deployment target from single EC2 to Amazon EKS for scalability
- Provision infrastructure (EC2, ECR, security groups) via Terraform instead of manual setup
- Add automated tests as a pipeline stage before the Docker build
- Add Prometheus/Grafana monitoring for the running container
