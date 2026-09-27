const {api}=require('./lib');
(async()=>{
 const a=await api('GET','/v2/account');
 if(a.httpStatus) return console.log('ERROR',a);
 console.log('OK account', a.id, '| cash $'+a.cash, '| equity $'+a.equity, '| buying power $'+a.buying_power, '| status',a.status);
 const p=await api('GET','/v2/positions');
 console.log('positions:', Array.isArray(p)?(p.length?p.map(x=>x.symbol+' '+x.qty):'none'):p);
})();
