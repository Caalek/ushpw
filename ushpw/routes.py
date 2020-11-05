import random, string, re, os
from datetime import datetime
from ushpw import app, is_url, is_url_no_http, Random, Custom, Snippets
from flask import render_template, redirect, url_for, request, flash

def create_id(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = length))

@app.route('/', methods = ['GET', 'POST'])
def home():
    if 'longUrlRandom' in request.form:
        long_url = request.form['longUrlRandom']
        if re.match(is_url, long_url):
            long_url_in_db = Random.find_one({'long_url': long_url})

            if not long_url_in_db:
                short_id = create_id(3)
                db_entry = {
                    'short_id': short_id,
                    'long_url': long_url,
                    'clicks': 0,
                    'created_on': datetime.utcnow()
                }
                Random.insert_one(db_entry)
            else:
                short_id = long_url_in_db['short_id']
                long_url = long_url_in_db['long_url']
            return redirect(url_for('shortened', short_id = short_id))
        
        else:
            flash('Please enter a valid URL.')
            return(render_template('home.html'))

    if 'longUrlCustom' in request.form:
        custom_long_url = request.form['longUrlCustom']
        if re.match(is_url, custom_long_url) and custom_long_url != '':
            text = request.form['textCustom']
            text_exists = Custom.find_one({'long_url': long_url})

            if not text_exists:
                custom_clicks = 0
                db_entry = {
                    'short_id': text,
                    'long_url': long_url,
                    'clicks': 0,
                    'created_on': datetime.utcnow(),
                }
                Custom.insert_one(db_entry)

                return redirect(url_for('shortened', short_id = text))
            else:
                flash("We're sorry, but that word is already taken. Try a different word.")
                return(render_template('home.html'))
        
        else:
            flash('Please enter a valid URL and all fill in all the required fields.')
            return(render_template('home.html'))
        
    return(render_template('home.html'))


@app.route('/<string:short_id>')
def short_url(short_id):
    random_checked_id = Random.find_one({'short_id': short_id})
    custom_checked_id = Custom.find_one({'short_id': short_id})
    snippet_checked_id = Snippets.find_one({'short_id': short_id})
    if random_checked_id:
        Random.update_one({'short_id': random_checked_id}, {'$inc': {'clicks': 1}})
        return redirect(random_checked_id['long_url'])
    elif custom_checked_id:
        Custom.update_one({'short_id': random_checked_id}, {'$inc': {'clicks': 1}})
        return redirect(custom_checked_id['long_url'])
    elif snippet_checked_id:
        Snippets.update_one({'short_id': random_checked_id}, {'$inc': {'views': 1}})
        return render_template('snippet.html', text = snippet_checked_id['text'])
    else:
        return render_template('404.html'), 404

@app.route('/shortened/<string:short_id>')
def shortened(short_id):
    random_id_exists = Random.find_one({'short_id': short_id})
    custom_id_exists = Custom.find_one({'short_id': short_id})
    if random_id_exists:
        long_url = random_id_exists['long_url']
        return render_template('shortened.html', long_url = long_url, short_id = short_id)
    
    elif custom_id_exists:
        long_url = custom_id_exists['long_url']
        return render_template('shortened.html', long_url = long_url, short_id = short_id)
    
    else:
        return redirect((url_for('home')))

@app.route('/stats', methods = ['GET', 'POST'])
def stats():
    if 'UrlCounter' in request.form:
        url = request.form['UrlCounter']
        if re.match(is_url_no_http, url) or re.match(is_url, url):
            short_id = url.split('pw/')[1]
            random_id_exists = Random.find_one({'short_id': short_id})
            custom_id_exists = Custom.find_one({'short_id': short_id})
            if random_id_exists is not None:
                clicks = random_id_exists['clicks']
                return render_template('stats.html', show_clicks = True, clicks = clicks, short_url = url)
            elif custom_id_exists is not None:
                clicks = custom_id_exists['clicks']
                return render_template('stats.html', show_clicks = True, clicks = clicks, short_url = url)
            else:
                flash('The URL you typed in does not exist. Please try again.')
                return render_template('stats.html')
        else:
            flash('Please enter a valid URL.')
            return render_template('stats.html')
    
    return render_template('stats.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/snippet-created/<string:short_id>')
def snippet_created(short_id):
    snippet_id_exists = Snippets.find_one({'short_id': short_id})
    if snippet_id_exists:
        short_id = snippet_id_exists['short_id']
        return render_template('snippet-created.html', short_id = short_id)
    else:
        return redirect((url_for('home')))

@app.route('/snippets', methods = ['GET', 'POST'])
def snippets():
    if request.method == 'POST':

        if 'snippetTextArea' in request.form and request.form['snippetTitle'] != '' and request.form['snippetTextArea'] != '':
            snippet = request.form['snippetTextArea']
            short_id = request.form['snippetCustomName']
            log(short_id)
            if short_id == '':
                short_id = None
            
            custom_id_exists = Snippets.find_one({'short_id': short_id})
            log(custom_id_exists)
            if not custom_id_exists:
                db_entry = {
                    'text': snippet,
                    'short_id': short_id,
                    'views': 0,
                    'title': request.form['snippetTitle'],
                    'created_on': datetime.utcnow()
                }
                Snippets.insert_one(db_entry)
                return redirect(url_for('snippet_created', short_id = short_id))
            else:
                flash("We're sorry, but that word is already taken. Try a different word.")
                return render_template('snippets.html')
        else:
            flash('Give your snippet a title and some text.')
            return render_template('snippets.html')
    
    return render_template('snippets.html')

@app.route('/easteregg')
def easteregg():
    return render_template('easteregg.html')