# hostpages 

its like github pages for airbnb hosts

`hostpages` generates a jekyll-based website for an airbnb host displaying all of their listings and optionally deploys it on github through github pages.

[See Example](https://arsenovic.github.io/41657617/)

## Usage
```
from hostpages import HostPageMaker

gh_token = 'hippity1234hoppity1234bippity123boppity' # your github token
userid = 41657617                                    # your airbnb userid

hp = HostPageMaker(userid=userid, gh_token=gh_token)
hp.make() # makes a repo titled userid with a jekyll pages
```

You will want to edit site to add contact information, and text about the 
hosts.

## How It Works

`HostPageMaker.make()` calls the following:

1. `HostPageMaker.scrape()`
    makes a scrapy spider and crawls the hosts listings airbnb page 
2. `HostPageMaker.create()`
    creates a jekyll-based website based on a template
3. `HostPageMaker.build()`
    builds the jekyll site locally
4. `HostPageMaker.deploy()` 
    creates a github repo called `userid` with `gh-pages` branch, and prints url.

you may wish to call these invidually. 

## Requires

* scrapy
* pyyaml
* pandas
* distutils
 
optionally for github deployment
 
* PyGithub
* gitpython
