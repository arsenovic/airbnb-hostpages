
from os import path
import os
import pandas as pd
import yaml
from distutils import dir_util
import shutil


from scrape import scrape_it



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
    



def create_sites(output_path, template='nuetral'):
    module_path = path.dirname(path.abspath(__file__))+'/'
    
    if output_path is None:
        output_path=module_path
    
    # site-wide paths
    scraped_csv = path.join(output_path,'items.csv')
    jekylls = path.join(output_path, '_jekylls')
    static_sites = path.join(output_path, '_sites')
    template_path = path.join(module_path,'templates/', template)

    # paths relative to each hosts's sub-site
    relative_paths = {'root':'',
                      'posts':'_posts',
                     'site_config':'_config.yml',
                     'index':'index.html'}

    ## use pandas to count #listings and sort 
    print(scraped_csv)
    df = pd.read_csv(scraped_csv)
    df['count']=df.groupby(['userid'])['name'].transform(len)
    df = df.sort('count', ascending=False)
    df = df[df['count']>2]



    shutil.rmtree(static_sites)
    # For each user, create a site
    for userid in df['userid'].unique():
        df_user = df[df['userid']==userid]
        
        ## site values
        user = df_user['user'].values[0]
        user_img = df_user['user_img'].values[0]
        
        # TODO: values to be gotten
        email = 'me@my.com'
        twitter = ''
        facebook = ''
        about_host = 'This is a host-submitted description of their listings. What do they do, how long have they operated, what additional services they provide, etc.   pulling from a host\'s  bio would make a sensible default, or perhaps we just blow this away. '
        
        yamls = {}
        
        
        yamls['site_config'] = \
            {'author': user,
             'copyright': 'Copyright &copy; 2016 %s. All Rights Reserved.'%user,
             'description': 'You can edit this line in _config.yml. It will appear in your document head meta (for Google search results) and in your feed.xml site description.\n',
             'email': 'your-email@domain.com',
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
              'title':  '%s\'s Listings'%user,
              'about_host':about_host,
              'subTitle':'A subtitle to describe this place.',
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
        paths = {k:path.join(jekylls, str(userid), relative_paths[k]) for k in relative_paths}
        print paths['root']
        # remove existing site
        if 0:
            try:
                shutil.rmtree(paths['root'])
            except(OSError):
                pass
        
        # make paths if they dont exist
        [try_to_mkdir(paths[k]) for k in ['root','posts']]
            
        # copy template
        dir_util.copy_tree(template_path, paths['root'])
        
        # write jekyl files
        with open(paths['site_config'],'wb') as yamlfile:
            yaml.dump(yamls['site_config'], yamlfile,default_flow_style=False)
            
        write_jekyl_frontmatter(yamls['index'], paths['index'])
        
        for k in listings_yamls:
            filename = path.join(paths['posts'],'2016-01-01-listing-'+str(k)+'.markdown')
            write_jekyl_frontmatter(listings_yamls[k], filename)
        
        source = paths['root']
        dest = path.join(static_sites,user )
        os.system('jekyll build -s \"%s\" -d \"%s\"'%(source, dest))
    
    
def scrape_and_create_sites(output_path=None,template='nuetral'):
    module_path = path.dirname(path.abspath(__file__))+'/'
    if output_path is None:
        output_path=module_path
    print module_path
    scrape_it(output_path=output_path)
    create_sites(output_path=output_path, template=template)
    
    
