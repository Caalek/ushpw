import random, string, re
from ushpw.models import Random, Custom
from ushpw.forms import RandomShorten, CustomShorten, ClickCounter
from ushpw import app, db, is_url
from flask import render_template, redirect, url_for, request, jsonify, session, flash
    
@app.route('/', methods = ['GET', 'POST'])
def home():
    random_shorten = RandomShorten()
    custom_shorten = CustomShorten()

    # random
    if 'long_url' in request.form and random_shorten.validate_on_submit():
        if re.match(is_url, random_shorten.long_url.data):
            long_url = random_shorten.long_url.data
            long_url_in_db = Random.query.filter_by(long_url = long_url).first()

            if not long_url_in_db:
                short_id = ''.join(random.choices(string.ascii_letters + string.digits, k = 3))
                clicks = 0
                db_entry = Random(short_id = short_id, long_url = long_url, clicks = clicks)
                db.session.add(db_entry)
                db.session.commit()
            else:
                short_id = long_url_in_db.short_id
                long_url = long_url_in_db.long_url
            return redirect(url_for('shortened', short_id = short_id))
        
        else:
            flash('Please enter a valid URL.')
            return(render_template('home.html', random_shorten = random_shorten, custom_shorten = custom_shorten))

    # custom
    if 'url' in request.form and custom_shorten.validate_on_submit():
        if re.match(is_url, custom_shorten.url.data) and custom_shorten.text.data != '':
            custom_long_url = custom_shorten.url.data
            text = custom_shorten.text.data
            text_exists = Custom.query.filter_by(short_id = text).first()

            if not text_exists:
                custom_short_id = text
                custom_clicks = 0
                db_entry = Custom(short_id = custom_short_id, long_url = custom_long_url, clicks = custom_clicks)
                db.session.add(db_entry)
                db.session.commit()

                return redirect(url_for('shortened', short_id = custom_short_id))
            else:
                flash("We're sorry, but that word is already taken. Try a different word.")
                return(render_template('home.html', random_shorten = random_shorten, custom_shorten = custom_shorten))
        
        else:
            flash('Please enter a valid URL and all fill in all the required fields.')
            return(render_template('home.html', random_shorten = random_shorten, custom_shorten = custom_shorten))
        
    return(render_template('home.html', random_shorten = random_shorten, custom_shorten = custom_shorten))


@app.route('/<string:short_id>')
def short_url(short_id):
    random_checked_id = Random.query.filter_by(short_id = short_id).first()
    custom_checked_id = Custom.query.filter_by(short_id = short_id).first()
    if random_checked_id:
        random_checked_id.clicks += 1
        db.session.commit()
        return redirect(random_checked_id.long_url)
    elif custom_checked_id:
        custom_checked_id.clicks += 1
        db.session.commit()
        return redirect(custom_checked_id.long_url)
    
    else:
        return render_template('404.html'), 404

@app.route('/shortened/<string:short_id>', methods= ['GET', 'POST'])
def shortened(short_id):
    random_id_exists = Random.query.filter_by(short_id = short_id).first()
    custom_id_exists = Custom.query.filter_by(short_id = short_id).first()
    if random_id_exists:
        long_url = random_id_exists.long_url
        return render_template('shortened.html', long_url = long_url, short_id = short_id)
    
    elif custom_id_exists:
        long_url = custom_id_exists.long_url
        return render_template('shortened.html', long_url = long_url, short_id = short_id)
    
    else:
        return redirect((url_for('home')))

@app.route('/api-page')
def api_page():
    return render_template('api.html')

@app.route('/stats', methods = ['GET', 'POST'])
def stats():
    counter = ClickCounter()
    if counter.is_submitted():
        if re.match(is_url, counter.short_url.data):
            short_id = counter.short_url.datareplace('https://www.ush.pw/', '')
            random_id_exists = Random.query.filter_by(short_id = short_id).first()
            custom_id_exists = Custom.query.filter_by(short_id = short_id).first()
            if random_id_exists is not None:
                clicks = random_id_exists.clicks
                return render_template('stats.html', show_clicks = True, counter = counter, clicks = clicks, short_url = counter.short_url.data)
            elif custom_id_exists is not None:
                clicks = custom_id_exists.clicks  
                return render_template('stats.html', show_clicks = True, counter = counter, clicks = clicks, short_url = counter.short_url.data)
            else:
                flash('The URL you typed in does not exist in our system. Please try again.')
                return render_template('stats.html', counter = counter)
        else:
            flash('Please enter a valid URL.')
            return render_template('stats.html', counter = counter)
    
    return render_template('stats.html', counter = counter)


@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/api/random/')
def api_random():
    if 'url' in request.args and re.match(is_url, request.args['url']):
        long_url = request.args['url']
        
        long_url_in_db = Random.query.filter_by(long_url = long_url).first()
        if not long_url_in_db:
            short_id = ''.join(random.choices(string.ascii_letters + string.digits, k = 3))
            clicks = 0
            db_entry = Random(short_id = short_id, long_url = long_url, clicks = clicks)
            db.session.add(db_entry)
            db.session.commit()
        else:
            short_id = long_url_in_db.short_id
            long_url = long_url_in_db.long_url
            clicks = long_url_in_db.clicks
        api_response = {
            'long_url': long_url,
            'short_url': f'https://www.ush.pw/{short_id}',
            'clicks': clicks,
            'status': 'success',
            'code': 200
        }
        return jsonify(api_response)

    else:
        api_response = {
            'message': 'error',
            'status_code': 404
        }
        return jsonify(api_response), 404

@app.route('/api/custom/')
def api_custom():
    if 'url' in request.args and 'text' in request.args and re.match(is_url, request.args['url']):
        long_url = request.args['url']
        text = request.args['text']
        text_exists = Custom.query.filter_by(short_id = text).first()

        if not text_exists:
            clicks = 0
            db_entry = Custom(short_id = text, long_url = long_url, clicks = clicks)
            db.session.add(db_entry)
            db.session.commit()

        else:
            api_response = {
                'message': 'error',
                'status_code': 404
            }
            return jsonify(api_response), 404

        api_response = {
                'long_url': long_url,
                'short_url': f'https://www.ush.pw/{text}',
                'clicks': clicks,
                'status': 'success',
                'code': 200
            }
        return jsonify(api_response)
    else:
        api_response = {
            'message': 'error',
            'status_code': 404
        }
        return jsonify(api_response), 404

@app.route('/easteregg')
def easteregg():
    return render_template('easteregg.html')
