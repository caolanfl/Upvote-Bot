import requests, json, warnings, time
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

session = requests.Session()

def login(username, proxy):
    url = 'https://reddit.com/api/login/' + username
    headerz = {'Host':'www.reddit.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
               'Accept':'application/json, text/javascript, */*; q=0.01',
               'Accept-Language':'en-US,en;q=0.5',
               'Accept-Encoding':'gzip, deflate, br',
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With':'XMLHttpRequest',
               'Referer':'https://www.reddit.com/',
               'Content-Length':'64'}
    values = {'op': 'login',
              'user': username,
              'passwd':'(password)',
              'rem':'yes',
              'api_type':'json'}
    proxies = {
        'http':proxy,
        'https':proxy}

    resp = session.post(url, data=values, headers=headerz)
    if resp.status_code == 200:
        print(username, 'logged in')
        return True
    else:
        print('error in logging in', username)
        return False

def upvote(post_url, proxy):
    post_sub = post_url.split('/r/')[1].split('/')[0]
    url = 'https://reddit.com/r/' + post_sub + '/new/'
    headerz = {'Host':'www.reddit.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language':'en-US,en;q=0.5',
               'Accept-Encoding':'gzip, deflate, br'}
    proxies = {
        'http':proxy,
        'https':proxy}
    
    resp = session.get(url, headers=headerz, proxies=proxies)

    html = BeautifulSoup(resp.content)

    # Getting json data of stuff like vote_hash and user_hash
    config = html.find('script', {'id':'config'}).text[8:]
    config = config[:len(config)-1]
    config = json.loads(config)

    vote_hash = config['vote_hash']
    user_hash = config['modhash']
    post_id, post_rank = get_post_info(post_url, html)

    url = 'https://www.reddit.com/api/vote?dir=1&id='+post_id+'&sr='+post_sub
    rank = '1'
    headerz = {'Host':'www.reddit.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language':'en-US,en;q=0.5',
               'Accept-Encoding':'gzip, deflate, br',
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With':'XMLHttpRequest',
               'Referer':'https://www.reddit.com',
               'Content-Length':'383'}
    values = {'id':post_id,
              'dir':post_rank,
              'vh':vote_hash,
              'isTrusted':'true',
              'vote_event_data':'%7B%22page_type%22%3A%22listing%22%2C%22sort%22%3A%22best%22%7D',
              'rank':rank,
              'r':post_sub,
              'uh':user_hash,
              'renderstyle':'html'}

    req = session.post(url, data=values, headers=headerz, proxies=proxies)
    print('Post upvoted')

def get_post_info(post_url, html):
    post_url = post_url.split('.com')[1]
    post_id = html.find('div', {'data-permalink':post_url})['id'][6:]

    post_rank = html.find('div', {'data-permalink':post_url})['data-rank']

    return post_id, post_rank

users = []
accounts = open('accounts.txt', 'r')
for account in accounts:
    users.append(account.split())

post_url = input('Post url > ')
desired_upvotes = int(input('Number of upvotes > '))
users = users[:desired_upvotes]

for user in users:
    session = requests.Session()
    if login(user[0], user[1]):
        upvote(post_url, user[1])
    time.sleep(100)
