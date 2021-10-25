FROM python:latest

# Add a user in the containre
RUN useradd -rm -d /home/user user
USER user
WORKDIR /home/user/app
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user:user requirements.txt requirements.txt
RUN python -m pip install --upgrade --force-reinstall pip
RUN pip install -r requirements.txt
COPY --chown=user:user . .

ENTRYPOINT ["python"]
CMD ["src/main.py"]