FROM python:latest

# Add a user in the containre
RUN useradd -rm -d /home/user user
USER user
WORKDIR /home/user/app
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user:user requirements.txt requirements.txt
RUN python3.10 -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY --chown=user:user . .

ENTRYPOINT ["python"]
CMD ["src/main.py"]