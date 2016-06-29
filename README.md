# hostpages 
generates a jekyll page for all an airbnb host's listings and optionally deploy it on github through github pages

## Usage
```
from hostpages import HostPageMaker

gh_token = 'fg7a65fga764a9s76f4afh764467ad4ad4afd4a' # your github token
userid = 41657617 # your airbnb userid

hp = HostPageMaker(userid=userid, gh_token=gh_token)
hp.make() # makes a repo titled userid with a jekyll pages
```
