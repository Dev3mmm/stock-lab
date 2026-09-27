// ST07 RSI(2) overlay paper trader (Alpaca). node trader.js run [--dry]
// Universe: 10 large caps + SPY/QQQ/IWM (kept small so a run stays fast and legible).
// Rule (frozen in ../strategies/ST07_rsi2_overlay.md): decided at today's close using ONLY data through today, applied tomorrow.
//   base = 1.0 if close > 200d SMA else 0.5 (defensive half-size in a downtrend)
//   overlay = 1.5x (instead of base) while RSI(2) < 10 and above the 200d SMA, until RSI(2) > 70
// Equal capital split across the universe. Run once per trading day, ideally in the last hour before the 4pm ET close
// (so "today's close" used for the signal is effectively final) or first thing in the morning using yesterday's close.
const fs = require('fs'); const path = require('path');
const { api, data } = require('./lib');
const UNIVERSE = ['AAPL','MSFT','JNJ','KO','WMT','JPM','PG','XOM','HD','MCD','SPY','QQQ','IWM'];
const JN = path.join(__dirname, 'journal.jsonl');
const log = o => fs.appendFileSync(JN, JSON.stringify({ t: new Date().toISOString(), ...o }) + '\n');

function rsi2(closes) {
  // Wilder RSI(2) on an array of closes, returns array same length (NaN until warmed up)
  const n = 2; const out = new Array(closes.length).fill(NaN);
  let ru = null, rd = null;
  for (let i = 1; i < closes.length; i++) {
    const d = closes[i] - closes[i - 1]; const up = Math.max(d, 0); const dn = Math.max(-d, 0);
    if (ru === null) { ru = up; rd = dn; } else { ru = (ru * (n - 1) + up) / n; rd = (rd * (n - 1) + dn) / n; }
    if (i >= n) out[i] = rd === 0 ? 100 : 100 - 100 / (1 + ru / rd);
  }
  return out;
}
const sma = (a, n) => a.map((_, i) => i < n - 1 ? NaN : a.slice(i - n + 1, i + 1).reduce((x, y) => x + y, 0) / n);

async function bars(sym, days = 400) {
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  const r = await data(`/v2/stocks/${sym}/bars`, { timeframe: '1Day', start, feed: 'iex', adjustment: 'split', limit: 1000 });
  if (!r.bars || !r.bars.length) throw new Error('no bars for ' + sym + ': ' + JSON.stringify(r).slice(0, 200));
  return r.bars.map(b => ({ t: b.t, c: b.c }));
}

async function decide(sym) {
  const b = await bars(sym); const closes = b.map(x => x.c);
  const r = rsi2(closes); const ma = sma(closes, 200);
  const i = closes.length - 1; // today (most recent close)
  if (isNaN(ma[i])) return { sym, weight: 1.0, why: 'warming up (<200 bars)' };
  const above = closes[i] > ma[i];
  const base = above ? 1.0 : 0.5;
  const overlay = above && r[i] < 10;
  return { sym, weight: overlay ? 1.5 : base, rsi2: +r[i].toFixed(1), above_200sma: above, close: closes[i], why: overlay ? 'RSI(2)<10 dip, above 200SMA -> 1.5x' : (above ? 'above 200SMA -> base 1.0x' : 'below 200SMA -> defensive 0.5x') };
}

async function run(dry) {
  const acct = await api('GET', '/v2/account');
  if (acct.httpStatus) { log({ act: 'error', where: 'account', acct }); console.log('account error', acct); return; }
  const equity = +acct.equity; const perSlot = equity / UNIVERSE.length;
  const decisions = [];
  for (const sym of UNIVERSE) { try { decisions.push(await decide(sym)); } catch (e) { log({ act: 'error', sym, msg: e.message }); console.log(sym, 'ERROR', e.message); } }
  console.log(decisions.map(d => `${d.sym.padEnd(5)} w=${d.weight}  ${d.why}`).join('\n'));
  const pos = await api('GET', '/v2/positions'); const have = Object.fromEntries((Array.isArray(pos) ? pos : []).map(p => [p.symbol, +p.qty]));
  for (const d of decisions) {
    const targetQty = Math.floor((perSlot * d.weight) / d.close);
    const curQty = have[d.sym] || 0; const diff = targetQty - curQty;
    if (Math.abs(diff) < 1) continue;
    const side = diff > 0 ? 'buy' : 'sell'; const qty = Math.abs(diff);
    console.log(`${d.sym}: ${curQty} -> ${targetQty} (${side} ${qty})`);
    if (dry) continue;
    const o = await api('POST', '/v2/orders', { symbol: d.sym, qty: String(qty), side, type: 'market', time_in_force: 'day' });
    log({ act: 'order', sym: d.sym, side, qty, weight: d.weight, rsi2: d.rsi2, above_200sma: d.above_200sma, why: d.why, order: o.id ? { id: o.id, status: o.status } : o });
    console.log('  ->', o.id ? `order ${o.id} ${o.status}` : JSON.stringify(o).slice(0, 200));
  }
  log({ act: 'run', dry: !!dry, equity, decisions });
}

const dry = process.argv.includes('--dry');
run(dry).catch(e => { console.error(e); log({ act: 'fatal', msg: e.message }); });
