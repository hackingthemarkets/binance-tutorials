# binance-tutorials
Real-Time Candlestick Charts and Crypto Trading Bot using Binance API and Websockets

This source code is explained and demonstrated in my YouTube channel:

https://youtube.com/parttimelarry

Binance API series for the webapp starts here (there are 10 videos):

https://www.youtube.com/watch?v=rvhnz1yBHgQ

If you are only interested in the RSI bot:

https://youtu.be/GdlFhF6gjKo

# Running in GCP

Push the local bot to GCP container registry:

```
./push_bot_gcp.sh <optionally add project, or specify project in .env>
```

Start a docker compute instance and ssh from console

Pull the pushed image: 
```
docker pull gcr.io/<project>/rsibot
```

Run the image:
```
docker run -d --name rsibot --restart unless-stopped -it gcr.io/<project>/rsibot 
```

To see the logs:
```
docker logs -f rsibot --tail 10
```