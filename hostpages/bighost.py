
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


from scrape import scrape_it, ListingSpider


class BigHost(object):
    def __init__(self, output_path='/tmp/', template='nuetral'):
        self.output_path=output_path
    
        self.module_path = path.dirname(path.abspath(__file__))+'/'
        self.template = 'nuetral'
        self.scraped_csv = path.join(output_path,'items.csv')

        self.jekylls = path.join(output_path, '_jekylls')
        self.sites = path.join(output_path, '_sites')
        self.template_path = path.join(self.module_path,'templates/', template)

        # paths relative to each hosts's sub-site
        self.relative_paths = {'root':'',
                              'posts':'_posts',
                             'site_config':'_config.yml',
                             'index':'index.html'}
        
        [try_to_mkdir(k) for k in self.jekylls, self.sites]
    
    def remove_output(self):
        try:
            shutil.rmtree(self.sites)
            shutil.rmtree(self.jekylls)
            [try_to_mkdir(k) for k in self.jekylls, self.sites]
        except:
            pass
    
    @property
    def df(self):
        return  pd.read_csv(self.scraped_csv)

    def first_userid(self, big=True):
        df = self.df
        if big:
            for userid in df['userid'].unique():
                if  len(df[df['userid']==userid]) > 3:
                    return userid
        
        return df['userid'].values[0]
            
    def create_site(self, userid):    
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
        
    def build_site(self,userid):
        userid=str(userid)
        source = path.join(self.jekylls, userid)
        dest = path.join(self.sites,userid )
        os.system('jekyll build -s \"%s\" -d \"%s\"'%(source, dest))
        print('built %s'%dest)
        
    def deplay_to_git(self,userid,  token):
        userid=str(userid)
        gh=github.Github(token)
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
        local_repo.git.commit('-m','inital commit')
        origin = local_repo.create_remote('origin',gh_repo.ssh_url)
        local_repo.git.push('--set-upstream','origin','gh-pages')
        print ('http://%s.github.io/%s'%(user.login,userid))
    
    def list_bighosts(self,  listings_thres=3):
        df = self.df
        # For each bighost
        out = []
        for userid in df['userid'].unique():
            n_listings = len(df[df['userid']==userid])
            if   n_listings ==3:
                out.append(userid)
                print 'https://www.airbnb.com/users/show/%i http://airbnb.com/s?host_id=%i'%(userid,userid)
        return out
                
    
    def create_sites_for_bighosts(self,  listings_thres=3):
        df = self.df
        # For each bighost
        for userid in df['userid'].unique():
            if  len(df[df['userid']]) > listings_thres:
                self.create_site(userid=userid)    
        
'''
def scrape_and_create_sites(output_path='/tmp/',template='nuetral'):
    scrape_it(output_path=output_path)
    create_sites(output_path=output_path, template=template)
'''
    
