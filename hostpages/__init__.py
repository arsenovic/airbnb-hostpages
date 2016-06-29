
from os import path
import os
import pandas as pd
import yaml
from distutils import dir_util
import shutil
import git
import github


import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging


from scrape import  ListingSpider


import logging

## turn off github logging noise
log = logging.getLogger('github')
log.setLevel(logging.ERROR)
log2 = logging.getLogger('scrapy')
log2.setLevel(logging.ERROR)



def write_jekyl_frontmatter(yml,filepath):
    with open(filepath,'wb') as f:
        f.write('---\n')
        yaml.dump(yml,f,default_flow_style=False)
        f.write('---\n')
        
def try_to_mkdir(d):
    try:
        os.mkdir(d)
    except(OSError):
        pass
    
class HostPageMaker(object):
    '''
    Makes a jekyll website for a airbnb Host, and deploy to git 
    
    Parameters
    --------------
    userid : int
        airbnb user id 
    gh_token : str
        a github oauth token. see below for info
    output_path: str
        path to store output website and scraping results
    template: ['nuetral']
        name of website template. 
        
            
    See Also
    ----------
    whats a token?
    https://help.github.com/articles/creating-an-access-token-for-command-line-use/
    '''
    def __init__(self, userid, gh_token=None, 
                 output_path='/tmp/hostpages', template='nuetral'):
        
        self.userid=userid
        self.gh_token=gh_token
        self.template = template
        
        self.output_path=output_path
        self.module_path = path.dirname(path.abspath(__file__))+'/'
        
        self.scraped_csv = path.join(output_path,'items.csv')

        self.jekylls = path.join(output_path, '_jekylls')
        self.sites = path.join(output_path, '_sites')
        self.template_path = path.join(self.module_path,'templates/', template)

        # paths relative to each hosts's sub-site
        self.relative_paths = {'root':'',
                              'posts':'_posts',
                             'site_config':'_config.yml',
                             'index':'index.html'}
        
        for k in [self.output_path, self.jekylls, self.sites]:
            try_to_mkdir(k) 
    
    def remove_output(self):
        try:
            shutil.rmtree(self.output_path)
        except:
            pass
    
    @property
    def df(self):
        return  pd.read_csv(self.scraped_csv)
    
    def scrape(self):
        '''
        create a scrapy spider and scrape this users start_url
        '''
        start_urls = ['http://airbnb.com/s?host_id=%i'%(self.userid)]
        # TODO fix cantrestartreactor problem
        settings = Settings(dict(FEED_FORMAT='csv',
                                FEED_URI=self.scraped_csv,
                                ))


        
        process = CrawlerProcess( settings)
        process.crawl(ListingSpider, start_urls=start_urls )
        configure_logging({'LOG_ENABLED':False,'LOG_LEVEL':'CRITICAL'})
        process.start()#stop_after_crawl=False)
            
    def create(self):
        '''
        Create a jekyll site from scraped results
        '''
        userid=self.userid    
        df = self.df
        df_user = df[df['userid']==userid]
       
        
        ## site values
        user = df_user['user'].values[0]
        user_img = df_user['user_img'].values[0]
        
        # TODO: values to be gotten
        email = 'me@my.com'
        twitter = 'twitterid'
        facebook = 'facebookid'
        about_host = 'This is a host-submitted description of their listings. What do they do, how long have they operated, what additional services they provide, etc.   pulling from a host\'s  bio would make a sensible default, or perhaps we just blow this away. '
        
        yamls = {}
        
        
        yamls['site_config'] = \
            {'author': user,
             'copyright': 'Copyright &copy; 2016 %s. All Rights Reserved.'%user,
             'description': 'This will appear in your document head meta (for Google search results) and in your feed.xml site description.\n',
            
             'markdown': 'kramdown',
             'permalink': 'pretty',
             'title': '%s\'s Listings'%user,
             'url': 'http://yoursite.com',
             'social': [{'title': 'facebook',
                         'url': 'https://www.facebook.com/'},
                         {'title': 'twitter',
                         'url': 'https://www.twitter.com/'},
                         {'title': 'email',
                         'url': 'mailto:%s'%email}],
                      
                     }
        yamls['index'] = \
            {'layout': 'default',
              'user':user,
              'about_host':about_host,
              'title':  '%s\'s Listings'%user,
              'subTitle':'Catchy subtitle to describe this place.',
              'user_img':user_img, 
              'bug':[-1]
                     }

        
        listings_yamls = {}
        for lid,img,name, summary in df_user[['listingid','listing_img','name','summary']].values:
            listings_yamls[lid] =\
                {'layout': 'default',
                'img': img,
                'category': 'listing',
                'title': name,
                'listing_id': lid,
                'description': summary, 
                'bug':[-1]
                }
            
        ## write junk  
        # localize paths to this userid
        paths = {k:path.join(self.jekylls, str(userid), self.relative_paths[k]) for k in self.relative_paths}
        print 'generated %s'%paths['root']
        
        # make paths if they dont exist
        [try_to_mkdir(paths[k]) for k in ['root','posts']]
            
        # copy template
        dir_util.copy_tree(self.template_path, paths['root'])
        
        # write jekyl files
        with open(paths['site_config'],'wb') as yamlfile:
            yaml.dump(yamls['site_config'], yamlfile,default_flow_style=False)
            
        write_jekyl_frontmatter(yamls['index'], paths['index'])
        
        for k in listings_yamls:
            filename = path.join(paths['posts'],'2016-01-01-listing-'+str(k)+'.markdown')
            write_jekyl_frontmatter(listings_yamls[k], filename)
        
    def build(self):
        '''
        Calls `jekyll build` for this website
        '''
        userid=self.userid
        userid=str(userid)
        source = path.join(self.jekylls, userid)
        dest = path.join(self.sites,userid )
        os.system('jekyll build -s \"%s\" -d \"%s\"'%(source, dest))
        print('built %s'%dest)
        
    def deploy(self):
        '''
        Create git repo named `self.userid` with `gh-pages` branch and push
        
        
        If the repo exists, it will be deleted
        
        
        '''
        if self.gh_token is None:
            raise ValueError('you need to set self.gh_token` to use deploy')
        userid=str(self.userid)
        gh=github.Github(self.gh_token)
        user = gh.get_user()
        
        try: 
            gh_repo = user.get_repo(userid)
            gh_repo.delete()
        except:
            pass
        gh_repo = user.create_repo(name=userid, private=True)
        
        
        jekyll_path= path.join(self.jekylls, userid)
        local_repo = git.Repo.init(jekyll_path)
        try:
            local_repo.git.checkout('-b' ,'gh-pages')
        except:
            local_repo.git.checkout('gh-pages')
        local_repo.git.add('*')
        commit_log=local_repo.git.commit('-m','inital commit')
        origin = local_repo.create_remote('origin',gh_repo.ssh_url)
        local_repo.git.push('--set-upstream','origin','gh-pages')
        print ('http://%s.github.io/%s'%(user.login,userid))
    
    def make(self):
        '''
        scrape, create, build, deploy
        '''
        self.remove_output()
        self.scrape()
        self.create()
        self.build()
        self.deploy()
        return 1
  
