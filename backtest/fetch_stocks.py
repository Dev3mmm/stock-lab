import yfinance as yf, pandas as pd, sys
T="AAPL MSFT AMZN GOOGL NVDA JPM JNJ XOM PG KO PEP WMT HD MRK CVX BAC WFC CSCO ORCL INTC IBM MCD DIS NKE TSCO COST UNH ABT TXN QCOM CAT GE BA MMM HON LMT T VZ PFE AMGN GILD LOW SBUX MO MDLZ ADBE CRM NFLX TSLA SPY QQQ IWM".split()
df=yf.download(T,start='2008-01-01',auto_adjust=True,progress=False,group_by='ticker',threads=True)
ok=0
for s in T:
    try:
        d=df[s].dropna(how='all').reset_index(); d.columns=[str(c).lower() for c in d.columns]
        d=d.rename(columns={'date':'dt','open':'o','high':'h','low':'l','close':'c','volume':'v'})[['dt','o','h','l','c','v']].dropna()
        if len(d)>1000: d.to_csv(f'../data/{s}_1d.csv',index=False); ok+=1; print(s,len(d),str(d.dt.iloc[0])[:10],'->',str(d.dt.iloc[-1])[:10])
    except Exception as e: print(s,'FAILED',e)
print('saved',ok,'of',len(T))
