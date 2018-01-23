import time
import hashlib
import requests
import urllib
import urllib2

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode
 
class BinanceAPI:
    
    BASE_URL = "https://www.binance.com/api/v1"
    BASE_URL_V3 = "https://api.binance.com/api/v3/"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"
    LINE_URL = "https://plg.herokuapp.com/BTBoT_post.php"
    Line_notify_url="https://notify-api.line.me/api/notify"

       
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_history(self, market, limit=50):
        path = "%s/historicalTrades" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)
        
    def get_trades(self, market, limit=50):
        path = "%s/trades" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)
        
    def get_kline(self, market):
        path = "%s/klines" % self.BASE_URL
        params = {"symbol": market}
        return self._get_no_sign(path, params)
    def get_ticker(self, market):
        path = "%s/ticker/24hr" % self.BASE_URL
        params = {"symbol": market}
        return self._get_no_sign(path, params)     
    def get_ticker2(self):
        path = "%s/ticker/24hr" % self.BASE_URL
        return self._get_no_sign(path)
    def get_orderbooks(self, market, limit=50):
        path = "%s/depth" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)

    def get_account(self):
        path = "%s/account" % self.BASE_URL
        return self._get(path, {})

    def get_products(self):
        return requests.get(self.PUBLIC_URL, timeout=30, verify=True).json()
        
    def get_exchance_info(self):
        path = "%s/exchangeInfo" % self.BASE_URL
        return requests.get(path, timeout=30, verify=True).json()

    def get_open_orders(self, market, limit = 100):
        path = "%s/openOrders" % self.BASE_URL
        params = {"symbol": market}
        return self._get(path, params)
    def get_open_orders2(self, limit = 100):
        path = "%s/openOrders" % self.BASE_URL
        return self._get(path,{})
    def buy_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    def sell_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL
        params = self._order(market, quantity, "SELL", rate)
        return self._post(path, params)

    def buy_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL
        params = self._order(market, quantity, "BUY")
        return self._post(path, params)

    def sell_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL
        params = self._order(market, quantity, "SELL")
        return self._post(path, params)

    def query_order(self, market, orderId):
        path = "%s/order" % self.BASE_URL
        params = {"symbol": market, "orderId": orderId}
        return self._get(path, params)

    def cancel(self, market, order_id):
        path = "%s/order" % self.BASE_URL
        params = {"symbol": market, "orderId": order_id}
        return self._delete(path, params)

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=30, verify=True).json()
    def _get_no_sign2(self, path):
        url = "%s" % (path)
        return requests.get(url, timeout=30, verify=True).json()
    def _sign(self, params={}):
        data = params.copy()

        ts = str(int(1000 * time.time()))
        data.update({"timestamp": ts})

        h = self.secret + "|" + urlencode(data)
        signature = hashlib.sha256(h.encode('utf-8')).hexdigest()
        data.update({"signature": signature})
        return data

    def _get(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.get(url, headers=header, \
            timeout=30, verify=True).json()

    def _post(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, \
            timeout=30, verify=True).json()

    def _order(self, market, quantity, side, rate=None):
        params = {}
         
        if rate is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(rate)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity
        
        return params

    def _format(self, price):
        return "{:.8f}".format(price)
            
    def _delete(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.delete(url, headers=header, \
            timeout=30, verify=True).json()
            
    def SendLine(self, to, stext):
        url = self.LINE_URL
        values = {"to": to, "text": stext}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req) 
        the_page = response.read()
        print the_page

    def send_notify(self, to,msg):
        try:
            url = self.Line_notify_url
            headers = {
                'Authorization' : 'Bearer '+to,
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
            line_dat = urllib.urlencode({'message' : msg})
            line_req = requests.post(url, headers=headers, data=line_dat, timeout=180)
            line_res = line_req.json()
            return line_res
        except Exception, err:
            return err