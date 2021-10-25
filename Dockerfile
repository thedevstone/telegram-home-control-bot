FROM python:latest

# Add a user in the containre
RUN useradd -rm -d /home/user user
WORKDIR /home/user/app
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY --chown=user . .
RUN chmod 777 /home/user/app

USER user
CMD ["python", "src/main.py"]