# Purpose

This Python script takes two csv files and uses Azure OpenAI (embeddings) to compare a column in each file against each other and generates a third csv file that contains the matches (all columns, appended together). This has been tested against Python 3.11.

# Requirements
- Python 3.x
- OpenAI and Pandas Python modules
- Azure OpenAI (default deployment name assumed is `text-embedding-ada-002`)
    - Azure OpenAI API Key
    - Azure OpenAI endpoint
- 2 csv files you want to compare

# Install/Usage Instructions (Docker)
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
(Note: this exposes the current directory into the container under /app, so you can pass data in and out of the container. It will also delete the container when you exit the container via `exit` command)

Install required dependencies (run command inside the docker container)
```bosh
cd /app
pip install -r requirements.txt
```

Add the two csv files you want to compare into the embeddings folder.

Run the python app (also inside the docker container)
```bosh
python app.py
```

Within this same directory, a new csv file will be generated that contains only the matched rows that are similar to one another (based on threashold value and based on the two columns you are comparing), and in a given row you'll see all the values in the first file combined with all the values in the second file.

Using the below example:

File-1.csv:

    CompanyID, CompanyName, Price, Quantity
    202,ACME,12.23,4
    203,Foo,43,1

File-2.csv:

    LegalCompanyName, Address, CustomerContact
    ACME Corporation,123 Anvil, Roadrunner
    Bar, 456 lolz, John Smith

Hypothetically we wanted to compare CompanyName and LegalCompanyName. In the app.py we'd set mainFile="File-1.csv", mainFileHeader="CompanyName", secondFile="File-2.csv", secondFileHeader="LegalCompanyName". The new output file (against a single match) might look like:

Compared.csv:

    CompanyID, CompanyName, Price, Quantity, LegalCompanyName, Address, CustomerContact
    202,ACME,12.23,4,ACME Corporation,123 Anvil, Roadrunner

And there would be two other new files in the directory:
- File-1-embeddings.csv
- File-2-embeddings.csv

After the embeddings files have been created, you can comment out (#) lines 96 and 98 in the python script, and play with the threashold value (line 14, default .90) and possibly output file name (line 19), re-running the script repeatedly to find the right threashold value for your data set. I highly recommend having an index in your mainFile (in above example, CompanyID being unique). It allows you to load multiple "Compared.csv" versions (based on threashold) into Excel and use a simple if/isnumber/match (ex:`=IF(ISNUMBER(MATCH(B4, A4:A200, 0)), "Exists", "Doesn't Exist")`) lookup, against said unique index ID, comparing one threashold output against another, to see what's new/different, assuming you're working with large data sets and theres variability in the output files across different threasholds.

# Known Behaviors
- If there's any blank columns in the source data, it can throw the alignment off
- If there's any missing values in the columns you are comparing, it can fail (TODO: error handling)
- The first row in the output file are numbers, just delete them (TODO: find out why)