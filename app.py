#! /usr/local/bin/python3
import os
from openai import AzureOpenAI
import pandas as pd
import numpy as np
from tqdm import tqdm

client = AzureOpenAI(
    api_key = os.getenv("AZURE_OPENAI_KEY"),
    api_version = os.getenv("AZURE_OPENAI_APIVERSION","2023-05-15"),
    azure_endpoint = os.getenv("AZURE_OPENAI_APIENDPOINT") # example: "https://deployment-name.openai.azure.com/"
)

threshold = .90 # set how similar the two columns should be for it to match. Default set to 90%
mainFile = "First-File.csv" # the first file you want to walk through
mainFileHeader="First-File-Column-Name" # the column's header name in the first file you want to compare
secondFile = "Second-File.csv" # the second file you want to walk through
secondFileHeader="Second-File-Column-Name" # the column's header name in the second file you want to compare
filename="Compared.csv" # the name of the file the script will create
azureDeploymentName="text-embedding-ada-002" # the Azure OpenAI's deployment name

MEfileName=mainFile[:len(mainFile)-4]+"-embeddings.csv" # The mainFile's embeddings file name.
SEfileName=secondFile[:len(secondFile)-4]+"-embeddings.csv" # The secondFile's embeddings file name.
mf = pd.read_csv(mainFile,index_col=0, nrows=0).columns.tolist() # grab the header names
sf= pd.read_csv(secondFile,index_col=0, nrows=0).columns.tolist() # grab the header names

# The new file's header names is mainFile + secondFile headers
# Note: if there are blanks in the source files you will see "unnamed" and will need to manually remove
# Note2: The very first row will have numbers in it. You can delete this row.
colum_names = mf + sf

def generate_embeddings(text, total): # model = "deployment_name"
    global count
    print(f"..{count}/{total} ({count/total:.0%}) | {text}")
    count += 1
    return client.embeddings.create(input = [text], model=azureDeploymentName).data[0].embedding

def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def gen_embed(file,header,emb_header, emb_file):
    # Print out where we are
    print(f"Generate {file} embeddings")
    print(f"Opening {file}")

    # Read the file
    main_df = pd.read_csv(file)

    # Apply embeddings to each row
    print("applying the embeddings")
    main_df[emb_header] = main_df[header].apply(lambda x: generate_embeddings(text=x, total=len(main_df)))
    print(f"writing to file: {emb_file}")
    main_df.to_csv(emb_file, index=False)

def compare():
    # Read PL and TA data
    main_embeddings_df = pd.read_csv(MEfileName)
    second_embeddings_df = pd.read_csv(SEfileName)

    # Convert string representations of arrays to numpy arrays
    main_embeddings_df['Membedding'] = main_embeddings_df['Membedding'].apply(eval).apply(np.array)
    second_embeddings_df['Sembedding'] = second_embeddings_df['Sembedding'].apply(eval).apply(np.array)

    # Initialize the list with specified column names
    compared_data = [colum_names]

    # Counter for the number of matches found
    match_counter = 0

    # Iterate through each row in MainFile with tqdm for progress bar
    for mindex, row_mf in tqdm(main_embeddings_df.iterrows(), total=len(main_embeddings_df), desc='Comparing Record'):
        # Iterate through each row in TA
        for sindex, row_sf in second_embeddings_df.iterrows():
            # Calculate cosine similarity between embeddings
            similarity = cosine_similarity(row_mf['Membedding'], row_sf['Sembedding'])
            # Check if similarity meets threshold
            if similarity >= threshold:
                # Concatenate MainFile and SecondFile data, excluding embedding and index columns
                compared_row = pd.concat([row_mf.drop('Membedding'), row_sf.drop('Sembedding')], ignore_index=True)
                # Append compared data to list
                compared_data.append(compared_row)
                # Increment match counter
                match_counter += 1
                print(f"Found {match_counter} matches!")


    # Create DataFrame from compared data
    compared_df = pd.DataFrame(compared_data)

    # Save compared data to compared.csv
    compared_df.to_csv(filename, index=False)

count = 1
gen_embed(file=mainFile, header=mainFileHeader, emb_header="Membedding",emb_file=MEfileName)
count = 1
gen_embed(file=secondFile, header=secondFileHeader, emb_header="Sembedding",emb_file=SEfileName)
compare()