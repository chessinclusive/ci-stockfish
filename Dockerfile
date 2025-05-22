FROM public.ecr.aws/lambda/python:3.11

# Install dependencies to Lambda task root
COPY requirements.txt .

RUN yum install -y gcc python3-devel stockfish && yum clean all

RUN pip install --upgrade pip && \
    pip install -r requirements.txt -t "${LAMBDA_TASK_ROOT}" --no-cache-dir

# Copy your app
COPY ./app ${LAMBDA_TASK_ROOT}

# Lambda will look for 'handler' in app.py
CMD ["app.handler"]


# FROM public.ecr.aws/lambda/python:3.12

# COPY ./app ${LAMBDA_TASK_ROOT}

# COPY requirements.txt .

# RUN apt-get update && \
#     apt-get install -y gcc python3-dev stockfish && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt -t "${LAMBDA_TASK_ROOT}" --upgrade --no-cache-dir && \


# CMD [ "app.handler" ]


# FROM python:3.12-slim

# WORKDIR /var/task

# COPY requirements.txt .
# RUN apt-get update && apt-get install -y gcc python3-dev stockfish && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt -t /var/task --no-cache-dir

# COPY ./app .

# # CMD ["app.handler"]
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
