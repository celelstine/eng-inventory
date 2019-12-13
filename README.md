# eng-inventory
Python app to create an inventory of engineering work 

## Description
The project uses the github graphQl Api https://developer.github.com/v4/ to get insight about PRs, pre-process the data and store it in a CSV.

## How to setup
- ensure to have pipenv https://pipenv-fork.readthedocs.io/en/latest/
- clone the repo and `cd` to the directory
- activate your working environment `pipenv shell`
- install dep `pip install `
- your token should the scope described here https://developer.github.com/v4/guides/forming-calls/#authenticating-with-graphql
- use the app like so `python app.py pymetrics pymetrics pr.csv 3000 --token <token> `
