FROM zuppi/my-spaces:base
# clone user stuff
RUN git clone {{ repo_url }} .
RUN if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi;
RUN if [ -f "packages.txt" ]; then apt-get install $(grep -vE "^\s*#" packages.txt  | tr "\n" " "); fi;

ENTRYPOINT ["python", "app.py"]