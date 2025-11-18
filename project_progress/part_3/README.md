# IR-WA Search Engine — Part 3: Ranking and Filtering

### Group Members
- **u215114** Albert Jané  
- **u215108** Jordi Esteve  
- **u198732** Marc de los Aires  


### Overview
This part of the project focuses on ranking and filtering for the fashion product search engine.  
The notebook **`Ranking_and_Filtering.ipynb`** builds on the preprocessing and index from Parts 1 and 2, and implements several ranking methods (TF–IDF + cosine, BM25, a custom e-commerce–oriented score, and a Word2Vec-based semantic ranker), together with basic candidate filtering and IR evaluation metrics.


### Dataset
As in Parts 1 and 2, the code is configured to load the products dataset from the `data/` folder located at the root of the repository.  
Please ensure the files **`fashion_products_dataset.json`** and **`validation_labels.csv`** are correctly placed in this folder before running the notebook locally.

