from datetime import datetime

from flask import Flask, render_template, request
from py.model import session, Account, Asset, FXRate, engine
import pandas as pd

app = Flask(__name__, static_url_path='', static_folder='../static/', template_folder='../static/html/')


@app.route('/', methods=['GET'])
def index():
    df = pd.read_sql_query('''
    SELECT asset.date, account.name, amount,account.currency as account_currency,rate,fx_rate.currency as fx_currency
    FROM asset LEFT JOIN account ON asset.accountId = account.id
    LEFT JOIN fx_rate ON asset.date = fx_rate.date ORDER BY asset.date''', con=engine)
    df['rate'].fillna(method='backfill', inplace=True)
    df['fx_currency'].fillna('JPY', inplace=True)
    df['rmb'] = df['amount']
    a = df['account_currency'] == df['fx_currency']
    df.loc[a, 'rmb'] = df.loc[a, 'amount'] / df.loc[a, 'rate']

    df['jpy'] = df['amount']
    b = df['account_currency'] != df['fx_currency']
    df.loc[b, 'jpy'] = df.loc[b, 'amount'] * df.loc[b, 'rate']

    total_df = df.groupby('date').agg({'jpy': 'sum', 'rmb': 'sum', 'rate': 'mean'})

    echartsOption = {'title': '总资产',
                     'xAxis': total_df.index.tolist(),
                     'startValue': total_df.index[-10],
                     'data': total_df['rmb'].round(2).tolist(),
                     'data_jpy': total_df['jpy'].round(2).tolist(),
                     'fxrate': total_df['rate']
                     }
    return render_template('index.html', echartsOption=echartsOption)


@app.route('/edit_asset', methods=['GET', 'POST'])
def edit_asset():
    print(request.form)
    if request.method == 'POST':
        if request.form['method'] == 'save':
            id = int(request.form['id']) if request.form['id'] != '' else -1
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            accountId = int(request.form['accountId'])
            amount = float(eval(request.form['amount'])) if request.form['amount'] != '' else 0
            asset = Asset()
            asset_list = session.query(Asset).filter(Asset.id == id).limit(1).all()
            if asset_list:
                asset = asset_list[0]
            asset.date = date
            asset.accountId = accountId
            asset.amount = amount
            session.add(asset)
            session.commit()
        elif request.form['method'] == 'delete':
            id = request.form['id']
            if id != '':
                session.query(Asset).filter(Asset.id == int(id)).delete()
                session.commit()
    accounts = {a.id: (a.name.encode('utf8').decode('utf8'), a.is_active) for a in session.query(Account).all()}
    asset_list = [(a.id, a.date.strftime("%Y-%m-%d"), a.accountId, round(a.amount, 2)) for a in
                  session.query(Asset).order_by(Asset.date.desc(), Asset.id.desc()).all()]
    return render_template('edit_asset.html', asset_list=asset_list, accounts=accounts)


@app.route('/edit_fxrate', methods=['GET', 'POST'])
def edit_fxrate():
    print(request.form)
    if request.method == 'POST':
        if request.form['method'] == 'save':
            id = int(request.form['id']) if request.form['id'] != '' else -1
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            rate = float(request.form['rate']) if request.form['rate'] != '' else 0
            currency = request.form['currency']
            fx = FXRate()
            fx_list = session.query(FXRate).filter(FXRate.id == id).limit(1).all()
            if fx_list:
                fx = fx_list[0]
            fx.date = date
            fx.rate = rate
            fx.currency = currency
            session.add(fx)
            session.commit()
        elif request.form['method'] == 'delete':
            id = request.form['id']
            if id != '':
                session.query(FXRate).filter(FXRate.id == int(id)).delete()
                session.commit()
    fxrate_list = [(fx.id, fx.date, fx.rate, fx.currency) for fx in
                   session.query(FXRate).order_by(FXRate.date.desc()).all()]
    return render_template('edit_fxrate.html', fxrate_list=fxrate_list)


@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    print(request.form)
    if request.method == 'POST':
        id = int(request.form['id']) if request.form['id'] != '' else -1
        if request.form['method'] == 'save':
            name = request.form['name']
            is_active = 'is_active' in request.form
            currency = request.form['currency']
            account = Account()
            account_list = session.query(Account).filter(Account.id == id).all()
            if account_list:
                account = account_list[0]
            account.name = name
            account.is_active = is_active
            account.currency = currency
            session.add(account)
            session.commit()
        elif request.form['method'] == 'delete':
            if id > -1:
                session.query(Account).filter(Account.id == id).delete()
                session.commit()
    account_list = [(account.id, account.name, account.currency, account.is_active) for account in
                    session.query(Account).order_by(Account.id.asc()).all()]
    return render_template('edit_account.html', account_list=account_list)


if __name__ == "__main__":
    app.run(port=80, host='127.0.0.1', debug=True)
