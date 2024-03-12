# Purpose

This Python script takes two csv files and uses Azure OpenAI (embeddings) to compare a column in each file against each other. This has been tested against Python 3.11.

# Requirements
Azure OpenAI (default deployment name assumed is `text-embedding-ada-002`)
Azure OpenAI API Key
2 csv files

# Install Instructions (Docker)
Assuming you have Docker installed...

Download this repo's files
```bash
git clone https://github.com/ryandotclair/embeddings.git
cd embeddings
```

Update `app.py`'s lines 14-20's values (threshold to azureDeploymentName)

Spin up a python docker container with below one liner from the same directory as this repo (NOTE: updated the `[key]` and `[DEPLOYMENTNAME]` values first before hitting enter)
```bosh
docker build -t emb-python . && docker run -it --rm -v .:/app -e AZURE_OPENAI_KEY=[key] -e AZURE_OPENAI_APIENDPOINT="https://[DEPLOYMENTNAME].openai.azure.com/" emb-python
```

Install required dependencies (run command inside the docker container)
```bosh
pip install -r requirements.txt
```

Run the python app (also insid ethe docker container)
```bosh
cd /app
python app.py
```

After embeddings file has been created, you can comment out (#) lines 96 and 98, and then play with the threashold value (line 14) and output file name (line 19), re-running the script to play with the threashild value.

# Known Behaviors
- If there's any blank columns in the source data, it can throw the alignment off
- If there's any missing values in the columns you are comparing, it can fail (TODO: error handling)
- The first row in the output file are numbers, just delete them (TODO: find out why)