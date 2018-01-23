# -*- coding: UTF-8 -*-
# @yasinkuyu

# Define Python imports
import os
import sys
import time
import config 
import threading
import math

from BinanceAPI import BinanceAPI


class CheckPrice():
    
    # Define trade vars  
    order_id = 0
    order_data = None
    
    buy_filled = True
    sell_filled = True
    
    buy_filled_qty = 0
    sell_filled_qty = 0
    
    # percent (When you drop 10%, sell panic.)
    stop_loss = 0
    
    # Buy/Sell qty
    quantity = 0
    
    # BTC amount
    amount = 0
    
    # float(step_size * math.floor(float(free)/step_size))
    step_size = 0
    
    # Define static vars
    WAIT_TIME_BUY_SELL = 1 # seconds
    WAIT_TIME_CHECK_BUY_SELL = 0.2 # seconds
    WAIT_TIME_CHECK_SELL = 5 # seconds
    WAIT_TIME_STOP_LOSS = 20 # seconds
    MAX_TRADE_SIZE = 7 # int

    
    
    def __init__(self, option):
        self.mylist = ['ETHBTC','XVGBTC','XVGETH','LTCBTC','BNBBTC','NEOBTC','BCCBTC','OMGBTC','DASHBTC','EVXBTC','REQBTC','TRXBTC','XRPBTC','NULSBTC','ADABTC','CNDBTC','NEBLBTC','TRIGBTC','BNBETH','OMGETH','NEOETH','DASHETH','EVXETH','REQETH','TRXETH','XRPETH','NULSETH','BCCETH','BCDETH','ADAETH','NEBLETH','TRIGETH','BTCUSDT','ETHUSDT','BNBUSDT','BCCUSDT','NEOUSDT','LTCUSDT']
        self._listResult=[]
        self._listOpenOrder=[]
        self.option = option
        self.option.loop = 0
        self.option.dl = option.dl
        self.option.dh = option.dh
        self.wait_time = self.option.wait_time
        self.client = BinanceAPI(config.api_key, config.api_secret)
                 
    def chkPrice(self, symbol):
        print 'Check price'
        self.chkPrice2(self.option.dl,self.option.dh)
    def chkOrder(self, symbol):
        print 'Check order'
        self.openorders2()
    def run(self):

        cycle = 0
        actions = []
        symbol = self.option.symbol
        n=0
        print ('Started... \n')
       
        while (cycle <= self.option.loop):
           n=n+1
           print 'loop'
           print n
           
           startTime = time.time()
           if n%2:
            cPrice = threading.Thread(target=self.chkPrice, args=(symbol,))
            cPrice.start()
           else:
            cOrder = threading.Thread(target=self.chkOrder, args=(symbol,))
            cOrder.start()
           
           endTime = time.time()
           if endTime - startTime < self.wait_time:
               print 'sleep'
               print self.wait_time - (endTime - startTime)
               time.sleep(self.wait_time - (endTime - startTime))

               # 0 = Unlimited loop
               if self.option.loop > 0:       
                   cycle = cycle + 1
                   print 'cycle'
                   print cycle
 
    def chkPrice2(self, dL='1',dH='1'):
        print time.ctime()
        obj = self.get_ticker()
        if len(obj)<5:
            return
        sResult = ''
        listBuy =[]
        listSell =[]
        listBuy_item =['BUY']
        listSell_item =['SELL']
        listResult =['']
        listNew_hi =['New High: (Sell)']
        listNew_lo =['New Low: (Buy)']
        for obj_24Hour in obj:
            if obj_24Hour['symbol'] not in self.mylist:
                #print obj_24Hour['symbol']+'x'
                continue
            else:
                #print obj_24Hour
                lastPrice = float(obj_24Hour['lastPrice']) #last buy price (bid)
                bidPrice = float(obj_24Hour['bidPrice']) #last buy price (bid)
                askPrice = float(obj_24Hour['askPrice']) #last buy price (bid)
                highPrice = float(obj_24Hour['highPrice']) #last buy price (bid)
                lowPrice = float(obj_24Hour['lowPrice']) #last buy price (bid)
                weightedAvgPrice = float(obj_24Hour['weightedAvgPrice']) #last buy price (bid)
                try:
                    difLow = (lastPrice - lowPrice) /  lowPrice * 100
                    difHight= (highPrice-lastPrice) /  highPrice * 100
                    profit = (askPrice - bidPrice) /  bidPrice * 100
                    difAvg =abs((lastPrice-weightedAvgPrice) /  weightedAvgPrice * 100)
                    if (lastPrice <= weightedAvgPrice  and difLow < dL  and difLow < difAvg ):           
                        #print ('BUY> %s avg:%.8f, Last:%.8f ,L[%.8f],H[%.8f] (dL:%.2f  dH:%.2f) P:%.2f' % (obj_24Hour['symbol'], weightedAvgPrice,lastPrice,lowPrice,highPrice,difLow, difHight,profit))
                        sResult = ('%s \n  Last: %.8f \n  Low: %.8f(%.2f)\n  High:%.8f(%.2f)\n  Avg: %.8f(%.2f)\n  P: %.2f' % (obj_24Hour['symbol'], lastPrice,lowPrice,difLow,highPrice,difHight,weightedAvgPrice,difAvg,profit)) + '\n'
                        if (lastPrice<=lowPrice):
                            sResult='* ' + sResult
                            listNew_lo.append(sResult)
                        listBuy_item.append(sResult)
                        listBuy.append("BUY:"+obj_24Hour['symbol'])
                        #print sResult
                        continue
                    if (lastPrice > weightedAvgPrice  and difHight < dH and difHight < difAvg ):           
                        #print ('SELL> %s avg:%.8f, Last:%.8f ,L[%.8f],H[%.8f] (dL:%.2f  dH:%.2f) P:%.2f' % (obj_24Hour['symbol'], weightedAvgPrice,lastPrice,lowPrice,highPrice,difLow, difHight,profit))
                        sResult = ('%s \n  Last: %.8f \n  Low: %.8f(%.2f)\n  High:%.8f(%.2f)\n  Avg: %.8f(%.2f)\n  P: %.2f' % (obj_24Hour['symbol'], lastPrice,lowPrice,difLow,highPrice,difHight,weightedAvgPrice,difAvg, profit)) + '\n'
                        if (lastPrice>=highPrice):
                            sResult='* ' + sResult
                            listNew_hi.append(sResult)
                        listSell_item.append(sResult)
                        listSell.append("SELL:"+obj_24Hour['symbol'])
                        continue
                except:
                    print ('#%s avg:%.8f, Last:%.8f ,L[%.8f] H[%.2f] H-L: %.2f' % (obj_24Hour['symbol'], weightedAvgPrice,lastPrice,lowPrice,highPrice, highPrice-lowPrice)) 
                    #time.sleep(0.2)
        listResult=list(set(listBuy+listSell)-set(self._listResult))
        print '---_listResult'
        print self._listResult
        print '---listResult'
        print listResult
        print '---END'
        self._listResult=listBuy+listSell
        if len(listResult)>0:
            listBuy_item[0]='BUY ' + str(len(listBuy)) 
            listSell_item[0]='SELL ' + str(len(listSell))
            listBuy_item.append("----------------")
            sResult='Price alert: '+ str(time.ctime()) +'\n'
            sResult=sResult+'----------------\n'
            sResult=sResult+"\n".join(listBuy_item+listSell_item)
            self.send_line(sResult)
        if len(listNew_hi+listNew_lo)>2:
            sResult='New statistics: '+ str(time.ctime()) +'\n'
            sResult=sResult+'----------------\n'
            sResult=sResult+"\n".join(listNew_hi+listNew_lo)
            #self.send_line(sResult)
            self.send_lineNotify(sResult)
    def get_ticker(self):
        return self.client.get_ticker2()	
    def send_line(self,sText):
        return self.client.SendLine(config.idLine,sText)
    def send_lineNotify(self,sText):
        return self.client.send_notify(config.notify,sText)
    def openorders2(self):
        obj=self.client.get_open_orders2()
        #print obj;
        #return
        print 'Check open order status'
        if len(obj)<5:
            print obj
            return
        sResult = ''
        listOpenOrder =[]
        listOpenOrderDetail=['My order']
        listBuy =[]
        listSell =[]
        listBuy_item =['BUY']
        listSell_item =['SELL']
        listResult =['']
        for Order in obj:
            if Order['orderId'] in self._listOpenOrder:
                listOpenOrder.append(Order['orderId'])
                continue
            else:
                #print obj_24Hour
                symbol = str(Order['symbol']) 
                orderId = float(Order['orderId']) #last buy price (bid)
                price = float(Order['price']) #last buy price (bid)
                origQty = float(Order['origQty']) #last buy price (bid)
                executedQty = float(Order['executedQty']) #last buy price (bid)
                status = str(Order['status']) #last buy price (bid)
                side = str(Order['side']) #last buy price (bid)
                stime = str(Order['time']) #last buy price (bid)
                try:
                    listOpenOrder.append(Order['orderId'])
                    sResult=('%s #%s\n  Price: %.8f\n  OriQty: %.8f\n  OrdID: %s\n  dt: %s' % (side, symbol,price,origQty, str(orderId),str(stime))) 
                    listOpenOrderDetail.append(sResult)
                    # if side=="BUY"
                    #    listBuy_item.append(sResult)
                    #else:
                    #    listBuy_item.append(sResult)
                except:
                    #print ('#%s avg:%.8f, Last:%.8f ,L[%.8f] H[%.2f] H-L: %.2f' % (obj_24Hour['symbol'], weightedAvgPrice,lastPrice,lowPrice,highPrice, highPrice-lowPrice)) 
                    print '##'
        listNew=list(set(listOpenOrder)-set(self._listOpenOrder))
        listComplete=list(set(self._listOpenOrder)-set(listOpenOrder))
        print '---_listOpenOrder'
        print self._listOpenOrder
        print '---listNew'
        print listNew
        print '---listComplete'
        print listComplete
        print '---END'
        self._listOpenOrder=listOpenOrder
        
        if len(listComplete)>0:
            for Order in obj:
                if Order['orderId'] in listComplete:
                    #list complete
                    symbol = str(Order['symbol']) 
                    orderId = float(Order['orderId']) #last buy price (bid)
                    price = float(Order['price']) #last buy price (bid)
                    origQty = float(Order['origQty']) #last buy price (bid)
                    executedQty = float(Order['executedQty']) #last buy price (bid)
                    status = str(Order['status']) #last buy price (bid)
                    side = str(Order['side']) #last buy price (bid)
                    stime = str(Order['time']) #last buy price (bid)
                    try:
                        sResult='Update my Order : '+ str(time.ctime()) +'\n'
                        sResult=sResult+'----------------\n'
                        sResult=sResult+('%s #%s\n  Price: %.8f\n  OriQty: %.8f\n  OrdID: %s\n  dt: %s' % (side, symbol,price,origQty, str(orderId),str(stime))) 
                        self.send_line(sResult)
                    except:
                        print 'error##'
        
        if len(listNew)+len(listComplete)>0:
            listOpenOrderDetail[0]='My order: ' + str(len(listOpenOrderDetail)) 
            #listSell_item[0]='SELL ' + str(len(listSell))
            listOpenOrderDetail.append("----------------")
            
            print 'result:'
            sResult='Current Order : '+ str(time.ctime()) +'\n'
            sResult=sResult+'----------------\n'
            
            n=int(math.ceil(len(listOpenOrderDetail)/5))
            for i in range(1,n):
                if (i==1):
                    sResult=sResult+"\n".join(listOpenOrderDetail[0:4])
                elif str(i)==str(n):
                    sResult = "\n".join(listOpenOrderDetail[(i-1)*5: len(listOpenOrderDetail)-1])
                    if len(listComplete)>0:
                        sResult=sResult+"\n------Complete "+str(len(listComplete))
                else:
                    sResult="\n".join(listOpenOrderDetail[(i-1)*5:(i-1)*5+4])
                #sResult=sResult+"\n".join(listOpenOrderDetail)
                self.send_line(sResult)
