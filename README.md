# FTX-Arbitrage-Bot
 This is a trangular arbitrage bot trading on FTX exchange

To deploy:
- Input your API key & secret from FTX
- Look at their [sample code](https://github.com/ftexchange/ftx) for REST API and official documentation at https://docs.ftx.com/#overview
- Run the command
```shell
python3 app.py
```

## Notes to self (update: 26-06-2021)
- This trading bot was built at the time I knew nothing about OOP
- Trading logic of the bot is working but lots of improvements are needed for the code (e.g. style, structure, logging)
- Strategy is rather simple and direct, profitability is limited
