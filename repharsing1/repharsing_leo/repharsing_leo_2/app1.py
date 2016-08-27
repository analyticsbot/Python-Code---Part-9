# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3, requests, feedparser 
from newspaper import Article 
import urllib2, json, shutil, requests, wordpresslib, time
from PIL import Image
from datetime import datetime
from threading import Thread

time = datetime.now()

h = str(time.strftime('%H'))
m = str(time.strftime('%M'))
s = str(time.strftime('%S'))
mo = str(time.strftime('%m'))
yr = str(time.strftime('%Y'))

keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
searchString = '%27Xbox+One%27'
top = 20
offset = 0

url_bing = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)

def customSpin(articleText):
    headers = {'content-type':'application/x-www-form-urlencoded'}
    url = 'http://62.210.102.218:8080/spin?email=test@account.com&pass=P@ssw0rd&keywords=spolice&quality=20&y=4&s='+articleText
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)['spinnedText']

def getGoodURLs(include, exclude, urls):
    return_urls = []
    if len(include)>0 and len(exclude)>0:    
        for url in urls:
            if ((any(word in url for word in include)) or (not (any(word in url for word in exclude)))):
                return_urls.append(url)
    elif len(include)>0 and len(exclude)==0:
        for url in urls:
            if ((any(word in url for word in include))):
                return_urls.append(url)
    elif len(include)==0 and len(exclude)>0:
        for url in urls:
            if (not (any(word in url for word in exclude))):
                return_urls.append(url)

    return return_urls

def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    text = article.text
    title = article.title
    return text, title

def getURLs4mFeed(feedurls):
    goodUrls = []
    for url in feedurls:
        response = requests.get(url)
        d = feedparser.parse(response.text.encode('ascii', 'ignore'))
        for i in range(len(d.entries)):
            goodUrls.append( d.entries[i].link)
    return goodUrls

def postToWP(title, article, url_bing):
    request = urllib2.Request(url_bing)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request) 

    results = json.load(response)
    image = results['d']['results'][0]['Thumbnail']['MediaUrl']
    response = requests.get(image, stream=True)
    with open('testimage'+h+m+s+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    url = "http://www.easyinjury.com/xmlrpc.php"
    ##URL: www.easyinjury.com
    ##username: James
    ##pwd: mUFmNPvaXefAlgVTaTE#B2ku

    wp = wordpresslib.WordPressClient(url, 'James', 'mUFmNPvaXefAlgVTaTE#B2ku')
    wp.selectBlog(0)
    imageSrc = wp.newMediaObject('testimage'+h+m+s+'.jpg') #Used this format so that if i post images with the same name its unlikely they will override eachother

    img = '/wp-content/uploads/'+yr+'/'+mo+'/testimage'+h+m+s+'.jpg'

    post = wordpresslib.WordPressPost()

    post.title = title
    post.description = '<img src="'+img+'"/> \n' + article
    #post.tags = ["wordpress", "lib", "python"]

    # Set to False to save as a draft
    idPost = wp.newPost(post, True)

def spinArticle(s):
    ## variables
    #s (Required) - The text that you would like WordAi to spin.
    s = s
    #quality (Required) - 'Regular', 'Readable', or 'Very Readable'
    #depending on how readable vs unique you want your spin to be
    quality ='Very Readable'

    #email (Required) - Your login email. Used to authenticate.
    email = 'swordai@butikmukena.com'

    #pass - Your password. You must either use this OR hash (see below)
    pwd = 'J8weODTYl7'

    #hash - md5(substr(md5("pass"),0,15)); is the algorithm to calculate your hash.
    #It is a more secure way to send your password if you don't
    #want to use your password.
    hash_='f18b772e558e834d526a6985d009b7fc'

    ##output - Set to "json" if you want json output. Otherwise do not set
    #and you will get plaintext.
    output = ''

    #nonested - Set to "on" to turn off nested spinning (will help
    #readability but hurt uniqueness).
    nonested ='on'

    #sentence - Set to "on" if you want paragraph editing, where WordAi
    #will add, remove, or switch around the order of sentences in a paragraph (recommended!)
    sentence = 'on'

    #paragraph - Set to "on" if you want WordAi to do paragraph spinning -
    #perfect for if you plan on using the same spintax many times
    paragraph = 'on'

    #title - Set to "on" if you want WordAi to automatically spin your title
    #if there is one or add one if there isn't one
    title= 'on'

    #returnspin - Set to "true" if you want to just receive a spun version of the
    #article you provided. Otherwise it will return spintax.
    returnspin = 'true'

    #nooriginal - Set to "on" if you do not want to include the original word in
    #spintax (if synonyms are found). This is the same thing as creating a
    #"Super Unique" spin.
    nooriginal = 'on'

    #protected - Comma separated protected words (do not put spaces inbetween the words)
    protected = ''

    #synonyms - Add your own synonyms (Syntax: word1|synonym1,word two|first synonym 2|2nd syn). (comma separate the synonym sets and | separate the individuals synonyms)
    synonyms = 'word1|synonym1'

    headers = {'content-type':'application/x-www-form-urlencoded'}
    data = {'s':s, 'quality':quality, 'email':email, 'pass':pwd,\
            'output':output, 'nonested':nonested, 'sentence':sentence,\
            'paragraph':paragraph, 'title':title,'returnspin':returnspin,\
            'nooriginal':nooriginal, 'protected':protected,'synonyms':synonyms}

    data = {'s':s, 'quality':quality, 'email':email, 'hash':hash_}

    response  = requests.post(url, data = data, headers=headers)
    return response.text

def intervalPost(xdaysNumPost):
    for i in range(xdaysNumPost):
        if len(urls_to_scrape) == 0:
            print 'no more articles to spin'
            break
        url = urls_to_scrape.pop(i)
        articleText, title = extractText(url)
        time.sleep(1)
        if spinner == 'wordai':
            spinText = spinArticle(articleText)
        elif spinner == 'custom':
            spinText = customSpin(articleText)
        posttoWP(title, spinText, url_bing)
        time.sleep(1)

def work(email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner):
    urls = [str(u.strip()) for u in urls]
    goodUrls = getURLs4mFeed(urls)
    urls_to_scrape = getGoodURLs(include, exclude, goodUrls)

    for i in range(atOnce):
        if len(urls_to_scrape) == 0:
            print 'no more articles to spin'
            break
        url = urls_to_scrape.pop(i)
        articleText, title = extractText(url)
        if spinner == 'wordai':
            spinText = spinArticle(articleText)
        elif spinner == 'custom':
            spinText = customSpin(articleText)
        postToWP(title, spinText, url_bing)

    ## initializing the scheduler class
    sched = BlockingScheduler()

    if running_style =='cronjob':
        sched.configure({'misfire_grace_time': 1000})
        @sched.scheduled_job('cron', year= year, month= month, day=day, week=week, day_of_week=day_of_week, hour=hour, minute=minute, second=second)
        def timed_job():
            logging.basicConfig()
            intervalPost(xdaysNumPost)
        sched.start()
        
    elif running_style == 'interval':
        @sched.scheduled_job('interval', id='my_job_id', seconds=10)
        def my_interval_job():
            intervalPost(xdaysNumPost)
        
        sched.start()

def createProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c):
    c.execute("INSERT INTO data profile = " + str(profile) + \
              ", email = " + str(email) +  \
              ", pwd = " + str(pwd) + ", hash_ = " + str(hash_) +\
              ", output = " + str(output) + ", nonested = " + str(nonested) +\
              ", sentence = " + str(sentence) + ", paragraph = " + str(paragraph) +\
              ", title = " + str(title) + ", returnspin = " + str(returnspin) +\
              ", nooriginal = " + str(nooriginal) + ", protected = " + str(protected) +\
              ", synonyms = '" + str(synonyms) + ", include = '" + str(include)+", exclude = '" + str(exclude)+\
              ", emailwp = '" + str(emailwp)+ ", pwdwp = '" + str(pwdwp)+ ", atonce = '" + str(atonce)\
              +", xdays = '" + str(xdays)+", xdaysNumPost = '" + str(xdaysNumPost)+", urls = '" + str(urls)\
              +"', spinner = '" + str(spinner) + "';")
    conn.commit()

def updateVariables(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c):
    """Function to update the variables"""
    c.execute("UPDATE data SET email = '" + str(email) + \
              "', pwd = " + str(pwd) + ", hash_ = " + str(hash_) +\
              ", output = " + str(output) + ", nonested = " + str(nonested) +\
              ", sentence = " + str(sentence) + ", paragraph = " + str(paragraph) +\
              ", title = " + str(title) + ", returnspin = " + str(returnspin) +\
              ", nooriginal = " + str(nooriginal) + ", protected = " + str(protected) +\
              "', synonyms = " + str(synonyms) + ", include = '" + str(include)+"', exclude = '" + str(exclude)+\
              ", emailwp = '" + str(emailwp)+"', pwdwp = " + str(pwdwp)+", atonce = " + str(atonce)\
              +", xdays = " + str(xdays)+", xdaysNumPost = " + str(xdaysNumPost)+", urls = '" + str(urls)\
              +"' , spinner = " + str(spinner) + " WHERE profile = '"+str(profile)+"';")
    conn.commit()
    
def createUpdateProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c):
    c.execute("SELECT * from data where profile = '" + str(profile) + "'")
    exists = c.fetchone()
    if exists == None:
        createProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c)
    else:
        updateVariables(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c)

def getDefaultProfile(conn, c):
    """Function to get the default profile"""
    c.execute("SELECT profile from data where defaultProfile = 1")
    profile = c.fetchone()
    return profile    

def getParams(c, conn, profile):
    """Function to get the parameter"""
    c.execute("SELECT email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner from data where profile ='" + str(profile)+"';")
    params = c.fetchone()
    return params
  
# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.WTF_CSRF_SECRET_KEY  = "spinningbot"
app.CSRF_ENABLED = True
app.debug = True

@app.route('/profile/<profile>', methods=['GET'])
@app.route('/', methods=['GET'])
def home(profile=None):
    """ flask view for the home page"""
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()

    if not profile:
        profile = getDefaultProfile(conn, c)[0]
        
    params = getParams(c, conn, profile)
    email, pwd, hash_, output, nonested, sentence, paragraph, title,\
    returnspin, nooriginal, protected, synonyms, include, exclude,\
    emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner = params[0],params[1],params[2],params[3],params[4],\
    params[5],params[6],params[7],params[8],params[9],params[10],params[11],params[12],params[13],params[14],\
    params[15],params[16],params[17],params[18],params[19],params[20]

    return render_template('index_2.html', urls = urls, message = "Please Wait...", profile=profile,\
                               email=email,pwd=pwd,hash=hash_,output=output,nonested=nonested,\
                               sentence=sentence,paragraph=paragraph,title=title,returnspin=returnspin,\
                               nooriginal=nooriginal,protected=protected,synonyms=synonyms,include=include,\
                               exclude=exclude,emailwp=emailwp,pwdwp=pwdwp,atonce=atonce,\
                               xdaysNumPost=xdaysNumPost, spinner=spinner, xdays=xdays)

@app.route('/go', methods=['POST'])
def postWP(numrows=10):
    """ flask view for the search page"""
    if request.method == "POST":
        errors = {}
        profile = request.form['profile']
        email = request.form['email']
        pwd = request.form['pwd']
        hash_ = request.form['hash']
        output = request.form['output']
        nonested = request.form['nonested']
        sentence = request.form['sentence']
        paragraph = request.form['paragraph']
        title = request.form['title']
        returnspin = request.form['returnspin']
        nooriginal = request.form['nooriginal']
        protected = request.form['protected']
        synonyms = request.form['synonyms']
        include = request.form['include']
        
        exclude = request.form['exclude']
        
        emailwp = request.form['emailwp']
        pwdwp = request.form['pwdwp']
        atonce = request.form['atonce']
        xdays = request.form['xdays']
        xdaysNumPost = request.form['xdaysNumPost']
        urls = request.form['urls']
        spinner = request.form['spinner']

        conn = sqlite3.connect('profile.db')
        c = conn.cursor()
        print profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner
        createUpdateProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, conn, c)
        
        include = [f.strip() for f in include.split(',')]
        exclude = [f.strip() for f in exclude.split(',')]
        t1 = Thread(target = work, args=(email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, xdays, xdaysNumPost, urls, spinner, ))
        t1.start()       
        
        return render_template('index_2.html', urls = urls, message = "Please Wait...", profile=profile,\
                               email=email,pwd=pwd,hash=hash,output=output,nonested=nonested,\
                               sentence=sentence,paragraph=paragraph,title=title,returnspin=returnspin,\
                               nooriginal=nooriginal,protected=protected,synonyms=synonyms,include=include,\
                               exclude=exclude,emailwp=emailwp,pwdwp=pwdwp,atonce=atonce,\
                               xdaysNumPost=xdaysNumPost, spinner=spinner)

## view for load all profiles
@app.route('/loadProfiles', methods=['GET'])
def loadProfiles():
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    c.execute("select profile, urls, defaultProfile from data")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

## view for making a profile default   
@app.route('/makedefault/<profile>', methods=['GET', 'POST'])
def makeDefault(profile):
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    c.execute("UPDATE data SET defaultProfile=0")
    conn.commit()
    c.execute("UPDATE data SET defaultProfile = 1 where profile = '" + str(profile) + "'")
    conn.commit()
    c.execute("select profile, urls, defaultProfile from data")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

if __name__ == '__main__':
        app.run(debug=True)
