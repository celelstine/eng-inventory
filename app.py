import sys
import csv
import os.path
import requests

import argparse

parser = argparse.ArgumentParser(
    description='Extract, transform and save PR stat',
    usage='Example "python %(prog)s pymetrics pymetrics pr.csv --token <token> "',)
parser.add_argument('repo', nargs=1,help='title of github repo')
parser.add_argument('owner',  nargs=1,help='username of the owner of the repo')
parser.add_argument('filename',  nargs=1,help='name of the csv file to write data to')
parser.add_argument('--token', required=True, help="Github access token")

args = parser.parse_args()

repo = args.repo[0]
owner = args.owner[0]
filename = args.filename[0]
token = args.token


headers = {"Authorization": "bearer %s" % token}

def fetch_pr_stat(count=20):
    """
    get details of PR for a repo from github
    """
    query = """
    { 
        repository (name: "%s", owner: "%s") { 
            pullRequests(last: %d) {
                edges {
                    pullRequest:node {
                        number
                        title
                        createdAt
                        mergedAt
                        closedAt
                        state
                        baseRefName
                        headRefName
                        commits(first: 1) {
                            totalCount
                            edges {
                                node {
                                    commit {
                                        id
                                        committedDate
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (repo, owner, count)
    print('running query:\t', query)

    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        


def main():

    result = fetch_pr_stat() # Execute the query
    prs = result['data']['repository']['pullRequests']['edges']

    pre_processed_data = [ 
        {
            "id": pr['pullRequest']['number'],
            "title": pr['pullRequest']['title'],
            "createdAt": pr['pullRequest']['createdAt'],
            "mergedAt": pr['pullRequest']['mergedAt'],
            "closedAt": pr['pullRequest']['closedAt'],
            "state": pr['pullRequest']['state'],
            "baseRefName": pr['pullRequest']['baseRefName'],
            "headRefName": pr['pullRequest']['headRefName'],
            "first_commit_date": pr['pullRequest']['commits']['edges'][0]['node']['commit']['committedDate'],
            "no_commits": pr['pullRequest']['commits']['totalCount']
        } for pr in prs
    ]

    csv_file = filename
    csv_columns = ['id','title','createdAt','mergedAt', 'closedAt', 'state', 'baseRefName', 'headRefName','first_commit_date', 'no_commits']

    file_exist = os.path.exists(csv_file)
    try:
        with open(csv_file, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)

            # create header when we have a new file
            if file_exist is False:
                writer.writeheader()
            for data in pre_processed_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

 
if __name__ == "__main__":
    main()