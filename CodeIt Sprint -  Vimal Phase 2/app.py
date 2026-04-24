from flask import Flask, render_template, request, redirect
import csv
import os
from datetime import date

app = Flask(__name__)

if not os.path.exists('acts.csv'):
    f = open('acts.csv', 'w')
    f.write('name,description,date\n')
    f.close()
if not os.path.exists('quotes.csv'):
    f = open('quotes.csv', 'w')
    f.write('author,quote_text,date\n')
    f.close()
if not os.path.exists('streaks.csv'):
    f = open('streaks.csv', 'w')
    f.write('name,streak_count,last_logged\n')
    f.close()


@app.route('/')
def home():
    f = open('acts.csv', 'r')
    total_acts = len(f.readlines()) - 1
    f.close()


    f = open('quotes.csv', 'r')
    total_quotes = len(f.readlines()) - 1
    f.close()


    f = open('streaks.csv', 'r')
    active_players = len(f.readlines()) - 1
    f.close()
    return render_template(
        'home.html',
        total_acts=total_acts,
        total_quotes=total_quotes,
        active_players=active_players
    )

@app.route('/chain', methods=['POST'])
def chain():
    name = request.form['name']
    description = request.form['description']
    if name == '':
        name = 'Anonymous'

    f = open('acts.csv', 'a', newline='')
    writer = csv.writer(f)

    writer.writerow([name, description, date.today().isoformat()])
    f.close()
    return redirect('/chain')

@app.route('/chain')
def chain_page():
    today = date.today().isoformat()

    today_acts = []

    older_acts = []

    f = open('acts.csv', 'r')
    reader = csv.DictReader(f)
    for row in reader:
        if row['date'] == today and len(today_acts) < 3:
            today_acts.append(row)
        else:
            older_acts.append(row)
    f.close()
    today_acts.reverse()
    older_acts.reverse()
    return render_template(
        'chain.html',
        today_acts=today_acts,
        older_acts=older_acts
    )

@app.route('/quotes', methods=['POST'])
def add_quote():
    author = request.form['author']
    quote_text = request.form['quote_text']
    if author == '':
        author = 'Anonymous'
    f = open('quotes.csv', 'a', newline='')
    writer = csv.writer(f)
    writer.writerow([author, quote_text, date.today().isoformat()])
    f.close()


    return redirect('/quotes')


@app.route('/quotes')
def quotes_page():
    all_quotes = []
    f = open('quotes.csv', 'r')
    reader = csv.DictReader(f)
    for row in reader:
        all_quotes.append(row)
    f.close()

    all_quotes.reverse()
    if len(all_quotes) > 0:
        daily_quote = all_quotes[0]
    else:
        daily_quote = None
    return render_template(
        'quotes.html',
        all_quotes=all_quotes,
        daily_quote=daily_quote
    )


@app.route('/streak', methods=['POST'])
def streak():
    name = request.form['name']
    today = date.today().isoformat()
    message = ''
    streak_count = 0
    streaks = []

    f = open('streaks.csv', 'r')
    reader = csv.DictReader(f)
    for row in reader:
        streaks.append(row)
    f.close()

    person = None
    for s in streaks:
        if s['name'] == name:
            person = s

    if person == None:
        f = open('streaks.csv', 'a', newline='')
        writer = csv.writer(f)
        writer.writerow([name, 1, today])
        f.close()
        message = 'Started your streak'
        streak_count = 1

    elif person['last_logged'] == today:
        message = 'Already logged today'
        streak_count = int(person['streak_count'])

    else:
        new_count = int(person['streak_count']) + 1
        for s in streaks:
            if s['name'] == name:
                s['streak_count'] = new_count
                s['last_logged'] = today
        f = open('streaks.csv', 'w', newline='')
        writer = csv.writer(f)
        writer.writerow(['name', 'streak_count', 'last_logged'])
        for s in streaks:
            writer.writerow([s['name'], s['streak_count'], s['last_logged']])
        f.close()
        message = 'Streak: ' + str(new_count)
        streak_count = new_count

    return redirect(f'/streak?name={name}&streak_count={streak_count}&message={message}')


@app.route('/streak')
def streak_page():
    name = request.args.get('name', '')
    streak_count = int(request.args.get('streak_count', 0))
    message = request.args.get('message', '')
    return render_template('streak.html', name=name, streak_count=streak_count, message=message)

app.run(debug = True)