# use an official Python image as base
FROM python:3.12-slim

# set environment variables for python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set the working dir inside the contrainer
WORKDIR /app

# copy only the dependency file first for better caching
COPY pyproject.toml ./

# install uv
RUN pip install uv

# installl dependencies usng uv and pyproject.toml
RUN uv pip install --system --deps develop

# copy source code and other files
COPY src/ ./src
COPY tests/ ./tests

# expose the port FASTAPI will use
EXPOSE 8000

# default command to run the app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]