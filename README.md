# FRANK
Frank is a question answering framework that combines multiple forms of reasoning, including deductive, statistical and arithmetic to answer question.


# Demo
A demo of this reference implementation of FRANK can be found at http://app.frank.nuamah.com/

# Installation

## Requirements
Requires Python 3.5 or higher. Python dependencies can be found in *`requirements.txt`*.

## External Dependencies
FRANK requires the following third-party tools to run. For the **FRANK API**, the following are required:
* MongoDB
* spaCy: [Install](https://spacy.io/usage#installation) the [en_core_web_md](https://spacy.io/models/en#en_core_web_md) model.

The configuration file `config.py` contains settings for running FRANK on your local computer and for running FRANK on the server.

While running FRANK locally, we advice that you set up the database endpoints to use the databases on remote FRANK server. Alternatively, you can install FRANK and the DBs locally.

`TODO:` Instructions for installing DBs locally will be added soon.

## Launching the API

The FRANK API can be launched from the terminal with the command:

```
python frank_api.py
```

# Launching the UI

The UI is a Javascript application built with `React` on `NodeJS`.
From within the UI source root directory, run this command in the terminal:

```
npm start
```

# Reference Papers
Here are links to our academic papers on FRANK. Please reference these papers when you use or extend FRANK.

1. Nuamah, K., Bundy, A. and Lucas, C., 2016, September. Functional inferences over heterogeneous data. In International Conference on Web Reasoning and Rule Systems (pp. 159-166). Springer, Cham.
https://www.research.ed.ac.uk/portal/files/26530704/rif_rr_short_final_1.pdf

2. Bundy, A., Nuamah, K. and Lucas, C., 2018, September. Automated Reasoning in the Age of the Internet. In International Conference on Artificial Intelligence and Symbolic Computation (pp. 3-18). Springer, Cham.
https://link.springer.com/chapter/10.1007/978-3-319-99957-9_1

3. Nuamah, K. and Bundy, A., 2018, September. Calculating error bars on inferences from web data. In Proceedings of SAI Intelligent Systems Conference (pp. 618-640). Springer, Cham.
https://www.research.ed.ac.uk/portal/files/58152744/rif_uncertainty_IS2018_sNack.pdf

4. Nuamah, K.; and Bundy, A. 2020. Explainable Inference in the FRANK Query Answering System. In Proceedings of the 24th European Conference on Artificial Intelligence (ECAI 2020).
https://www.research.ed.ac.uk/portal/files/141996163/ECAI20_nuamah_paper17.pdf






