import base64
import gmpy2
import hashlib
import os
from random_words import RandomWords
import sqlite3

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(12)
app.config["DEBUG"] = True

@app.route('/', methods=['GET', 'POST'])
def front():
    if request.method == 'POST':
        rc = [session['rw'][0].upper(), session['rw'][1], session['rw'][2]]
        # Ensure CSRF token is set
        if (request.form.get('csrf_token') != session['csrf_token']) or \
                (request.form.get('hp')):
            flash('You look like a bot', category='error')

        # Ensure reality check passes
        elif request.form.get('reality_check').split() != rc:
            flash(
                'bad reality check {} != {}'.format(
                    request.form.get('reality_check').split(), rc),
                category='error')
        else:
            # Open DB
            db = sqlite3.connect('shorturls.db')

            # If asked for a custom source, check if it exists
            source = None
            exists = 0
            if request.form.get('custom'):
                source = request.form.get('custom_path')
                exists = db.execute('select count(*) from shorturls where shorturl = ?',
                                    (request.form.get('custom_path'),)).fetchone()[0]

            # Bail if the source exists
            if exists != 0:
                flash('custom path exists', category='error')

            # Set source if not
            else:
                # Create a short URL without a source
                cur = db.cursor()
                result = cur.execute('''
                insert into shorturls (destination) values (?)
                ''', (request.form.get('destination'),))
                db.commit()

                # Set source to id if no source was given
                if not source:
                    source = gmpy2.digits(result.lastrowid, 62)
                cur.execute('''
                update shorturls set shorturl = ? where id = ?
                ''', (source,result.lastrowid))
                db.commit()
                flash('''
                Your domain is <a href="{base}{path}"">{base}{path}</a>'''.format(base=request.base_url, path=source),
                      category='success')
    session['csrf_token'] = hashlib.sha1(os.urandom(40)).hexdigest()
    session['rw'] = RandomWords().random_words(count=3)
    return render_template('front.html',
                           csrf_token=session['csrf_token'],
                           rw=session['rw'])

@app.route('/<shorturl>')
def serve(shorturl):
    # Attempt to retrieve the url from the db
    db = sqlite3.connect('shorturls.db')
    result = db.execute('select destination from shorturls where shorturl = ?',
                        (shorturl,)).fetchone()

    # If it doesn't exist, abort; otherwise, redirect
    if result is None:
        abort(404)
    return redirect(result[0])

if __name__ == '__main__':
    app.run()
