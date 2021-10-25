FROM python:latest

# Add a user in the containre
RUN useradd -rm -d /home/user user
USER user
WORKDIR /home/user/app

COPY --chown=user:user requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PATH="/home/user/.local/bin:${PATH}"
COPY --chown=user:user . .

ENTRYPOINT ["python"]
CMD ["src/main.py"]