# ci-stockfish
Chess.Inclusive Stockfish implementation

## FastAPI Application

A simple FastAPI application served by Uvicorn.

```bash
cd app/
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Docker & AWS ECR

Replace `<AWS_ACCOUNT_ID>`, `<AWS_REGION>`, and `<ECR_REPOSITORY_NAME>` with your AWS account details.

```bash
# Authenticate Docker to AWS ECR
aws ecr get-login-password --region <AWS_REGION> | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com

# Build the Docker image
docker build -t <ECR_REPOSITORY_NAME> .

# Tag the image with the full ECR repository URI
docker tag <ECR_REPOSITORY_NAME>:latest <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/<ECR_REPOSITORY_NAME>:latest

# Push to AWS ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/<ECR_REPOSITORY_NAME>:latest
```

