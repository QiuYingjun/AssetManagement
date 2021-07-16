from py.model import session, Account, Asset, FXRate, engine
import pandas as pd

df = pd.read_excel('../data/资产统计.xlsx', )


def write_account():
    session.query(Account).delete()
    session.commit()
    i = df.columns.tolist().index('汇率（日元/元）')
    for name in df.columns[3:i]:
        account = Account(name=name, currency='RMB')
        session.add(account)
    for name in df.columns[i+1:]:
        account = Account(name=name, currency='JPY')
        session.add(account)
    session.commit()


def write_fxrate():
    session.query(FXRate).delete()
    session.commit()
    for i in df.index:
        date = df.at[i, '日期']
        rate = df.at[i, '汇率（日元/元）']
        if not pd.isna(rate):
            fx = FXRate(date=date, rate=rate, currency='JPY')
            session.add(fx)
    session.commit()


def write_asset():
    session.query(Asset).delete()
    session.commit()
    accounts = {a.name: a.id for a in session.query(Account).all()}
    for i in df.index:
        for account in accounts:
            amount = df.at[i, account]
            if not pd.isna(amount) and abs(amount) > 0:
                asset = Asset(
                    date=df.at[i, '日期'], accountId=accounts[account], amount=amount)
                session.add(asset)
    session.commit()


if __name__ == '__main__':
    write_account()
    write_fxrate()
    write_asset()
