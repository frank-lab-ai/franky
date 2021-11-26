# FRANK

**_Functional Reasoning for Acquiring Novel Knowledge_**

FRANK is a question answering framework that combines multiple forms of reasoning, including deductive, statistical and arithmetic to answer questions.

# Demo

A demo of this reference implementation of FRANK can be found at http://app.frank.nuamah.com/

# Installation

## Requirements

- Requires Python 3.5 to 3.8. **Note: Python 3.9 is not supported.** Python dependencies can be found in _`requirements.txt`_. To create and install them into a virtual environment:

```
$ python3 -m venv venv
$ source venv/bin/activate  # or 'source venv/bin/activate.fish' if using fish-shell
$ pip install -r requirements.txt
```

## External Dependencies

FRANK requires the following third-party tools to run. For the **FRANK API**, the following are required:

- spaCy: [Install](https://spacy.io/usage#installation) the [en_core_web_sm](https://spacy.io/models/en#en_core_web_sm) model.

- To download the spaCy language model:

```
$ python -m spacy download en_core_web_sm
```

The configuration file `config.py` contains settings for running FRANK on your local computer and for running FRANK on the server.

While running FRANK locally, we advice that you set up the database endpoints to use the databases on remote FRANK server. Alternatively, you can install FRANK and the DBs locally.

`TODO:` Instructions for installing DBs locally will be added soon.

# Running FRANK

## Launching the API

The FRANK API can be launched from the terminal with the command:

```
python frank_api.py
```

## Using FRANK in the CLI

FRANK can be used as a CLI application.

```
python frank_cli.py
```

# Reference Papers

Here are links to our academic papers on FRANK. Please reference these papers when you use or extend FRANK.
1. Nuamah, K.; Bundy, A. and Yantao, J., 2021. A Context Mechanism for an Inference-based Question Answering System. AAAI Workshop on Commonsense Knowledge Graphs (CSKG). [[Link]](https://www.research.ed.ac.uk/en/publications/a-context-mechanism-for-an-inference-based-question-answering-sys)

2. Nuamah, K.; and Bundy, A. 2020. Explainable Inference in the FRANK Query Answering System. In Proceedings of the 24th European Conference on Artificial Intelligence (ECAI 2020). [[Link]](https://www.research.ed.ac.uk/portal/files/141996163/ECAI20_nuamah_paper17.pdf)

3. Nuamah, K. and Bundy, A., 2018, September. Calculating error bars on inferences from web data. In Proceedings of SAI Intelligent Systems Conference (pp. 618-640). Springer, Cham. [[Link]](https://www.research.ed.ac.uk/portal/files/58152744/rif_uncertainty_IS2018_sNack.pdf)

4. Bundy, A., Nuamah, K. and Lucas, C., 2018, September. Automated Reasoning in the Age of the Internet. In International Conference on Artificial Intelligence and Symbolic Computation (pp. 3-18). Springer, Cham. [[Link]](https://link.springer.com/chapter/10.1007/978-3-319-99957-9_1)

5. Nuamah, K., Bundy, A. and Lucas, C., 2016, September. Functional inferences over heterogeneous data. In International Conference on Web Reasoning and Rule Systems (pp. 159-166). Springer, Cham. [[Link]](https://www.research.ed.ac.uk/portal/files/26530704/rif_rr_short_final_1.pdf)






