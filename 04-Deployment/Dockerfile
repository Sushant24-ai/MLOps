FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim
RUN pip install -U pip & pip install pipenv
COPY [ "Pipfile", "Pipfile.lock", "./" ]
RUN pipenv install --system --deploy
COPY [ "home.py", "home.py" ]
ENTRYPOINT [ "python", "home.py" ]

