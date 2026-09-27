@echo off
cd /d C:\Users\Martin\Documents\stock_lab\paper_trader
echo [%date% %time%] daily ST07 run >> runner.log
node trader.js >> runner.log 2>&1
