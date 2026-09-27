const fs=require('fs');
let env={};
try{ env=Object.fromEntries(fs.readFileSync(__dirname+'/alpaca_keys.env','utf8').split(/\r?\n/).filter(Boolean).map(l=>l.split(/=(.*)/s).slice(0,2))); }catch(e){}
env.ALPACA_KEY = env.ALPACA_KEY || process.env.ALPACA_KEY;
env.ALPACA_SECRET = env.ALPACA_SECRET || process.env.ALPACA_SECRET;
const BASE='https://paper-api.alpaca.markets'; const DATA='https://data.alpaca.markets';
const H={'APCA-API-KEY-ID':env.ALPACA_KEY,'APCA-API-SECRET-KEY':env.ALPACA_SECRET,'Content-Type':'application/json'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function api(method,path,body){
  for(let a=0;a<4;a++){
    try{
      const r=await fetch(BASE+path,{method,headers:H,body:body?JSON.stringify(body):undefined});
      const t=await r.text(); let j; try{j=JSON.parse(t);}catch(e){j={raw:t};}
      if(!r.ok) j.httpStatus=r.status;
      return j;
    }catch(e){ await sleep(2000); }
  }
  throw new Error('alpaca api unreachable: '+method+' '+path);
}
async function data(path,params={}){
  for(let a=0;a<4;a++){
    try{ const r=await fetch(DATA+path+'?'+new URLSearchParams(params),{headers:H}); return await r.json(); }
    catch(e){ await sleep(2000); }
  }
  throw new Error('alpaca data unreachable: '+path);
}
module.exports={api,data};
