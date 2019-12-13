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
parser.add_argument('number',  nargs=1,help='name of the csv file to write data to')
parser.add_argument('--token', required=True, help="Github access token")

args = parser.parse_args()

repo = args.repo[0]
owner = args.owner[0]
filename = args.filename[0]
number = int(args.number[0])
token = args.token


headers = {"Authorization": "bearer %s" % token}

def fetch_pr_stat(count=20, cursor=None):
    """
    get details of PR for a repo from github
    """
    query = """
    { 
        repository (name: "%s", owner: "%s") { 
            pullRequests(last: %d %s) {
                edges {
                    cursor
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
                        timelineItems(itemTypes:[REVIEW_REQUESTED_EVENT], first: 1) {
                            nodes {
                                __typename
                                ... on ReviewRequestedEvent{
                                    createdAt
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (repo, owner, count, ', before: "%s"' % cursor  if cursor else '')
    print('running query......', query)

    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    print('request', request)
    if request.status_code == 200:
        print('done')
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        


def main():

    def get_first_review_request(pr):
        if len(pr['pullRequest']['timelineItems']['nodes']) > 0:
            return pr['pullRequest']['timelineItems']['nodes'][0]['createdAt']
        else:
            return ''

    def get_first_commit_date(pr):
        if pr['pullRequest']['commits']['totalCount'] > 0 :
            return pr['pullRequest']['commits']['edges'][0]['node']['commit']['committedDate']
        else:
            return ''

    count = 0
    cursor = None

    PR_data  = []

    while (count < number):
        result = fetch_pr_stat(100, cursor=cursor) # Execute the query
        prs = result['data']['repository']['pullRequests']['edges']
        count += len(prs)
        cursor = prs[0]['cursor'] if len(prs) > 0 else None
        print('count', count)
        
    

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
                "first_commit_date": get_first_commit_date(pr),
                "no_commits": pr['pullRequest']['commits']['totalCount'],
                "first_review_request": get_first_review_request(pr)
            } for pr in prs
        ]
    
        PR_data.extend(pre_processed_data)

    csv_columns = ['id','title','createdAt','mergedAt', 'closedAt', 'state', 'baseRefName', 'headRefName','first_commit_date', 'no_commits', 'first_review_request']
    file_exist = os.path.exists(filename)
    try:
        with open(filename, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            # create header when we have a new file
            if file_exist is False:
                print('writting body.................')
                writer.writeheader()
            
            print('writting data to body.......')
            for data in reversed(PR_data):
                writer.writerow(data)
    except IOError:
        print("I/O error")

 
if __name__ == "__main__":
    main()