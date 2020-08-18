import requests
import json
import time
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

if len(sys.argv) != 6 :
    print("Usage:")
    print(sys.argv[0], "site_url sitemap_url token username repo_name")

site_url = sys.argv[1]
sitemap_url = sys.argv[2]
token = sys.argv[3]
username = sys.argv[4]
repo_name = sys.argv[5]

def get_comments(session):
    issues = []
    url = 'https://api.github.com/repos/' + username + '/' + repo_name + '/issues?q=is&labels=Gitalk&sort=created'
    r = session.get(url=url)
    data = json.loads(r.text)
    for issue in data:
        issues.append(issue['body'].split('?')[0])
    
    return issues
    

def get_posts():
    post_urls = []
    r = requests.get(sitemap_url)
    root = ET.fromstring(r.text)

    for child in root:
        if 'post' in child[0].text:
            post_urls.append(child[0].text)

    if len(post_urls) > 0:
         post_urls.remove('https://www.lshell.com/post/')
    return post_urls
    

def get_post_title(url):
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.title.string.split(' - ')[0]

def init_gitalk(session, not_initialized):
    github_url = "https://api.github.com/repos/" + username + "/" + repo_name + "/issues"
    for url in not_initialized:
        title = get_post_title(url=url)
        issue = {
            'title': title,
            'body': url,
            'labels': ['Gitalk', url.split(site_url)[-1]]
        }
        print('[{}] initializing...'.format(title))
        resp = session.post(url=github_url, data=json.dumps(issue))
        if resp.status_code == 201:
            print('Created')
        else:
            print('failed: ', resp.text)
            break

def main():
    print('sleep 300s for waiting hugo build...')
    time.sleep(300)
    session = requests.Session()
    session.auth = (username, token)
    session.headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.59 Safari/537.36 Edg/85.0.564.30'
    }

    existing_comments = get_comments(session=session)
    post_urls = get_posts()
    not_initialized = list(set(post_urls) ^ set(existing_comments))

    init_gitalk(session=session, not_initialized=not_initialized)


main()