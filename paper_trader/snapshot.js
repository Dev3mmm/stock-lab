// Appends one equity/positions snapshot per call to data_snapshots.jsonl (used by the dashboard for the equity curve).
const fs=require('fs'); const path=require('path');
const { api } = require('./lib');
(async()=>{
  const acct = await api('GET','/v2/account');
  const pos = await api('GET','/v2/positions');
  const line = { t:new Date().toISOString(), equity:+acct.equity, cash:+acct.cash, buying_power:+acct.buying_power,
    positions:(Array.isArray(pos)?pos:[]).map(p=>({sym:p.symbol,qty:+p.qty,avg_entry:+p.avg_entry_price,mkt_value:+p.market_value,unrl_pl:+p.unrealized_pl})) };
  fs.appendFileSync(path.join(__dirname,'equity.jsonl'), JSON.stringify(line)+'\n');
  console.log(line);
})().catch(e=>{console.error(e); process.exit(1)});
