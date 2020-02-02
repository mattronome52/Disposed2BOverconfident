#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/mattronome52/Disposed2BOverconfident/blob/master/Disposed2BOverconfident.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[1]:


## Market Class ##
class Market(object):
  STOCK_NAMES = ["A", "B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","W","Z"]
  MAX_NUM_STOCKS = len(STOCK_NAMES)
  initialStocks = []
  currentPeriod = 0

  def __init__(self, name, numStocks):
    if (numStocks > self.MAX_NUM_STOCKS):
        print(f"ERROR: No more than {len(self.MAX_NUM_STOCKS)} stocks can be created")
        raise
    self.name = name
    self.initialStocks.extend(self.__generateStocks(numStocks))
    
  def __generateStocks(self, numStocks):
    i = 0
    stocks = []
    while (i < numStocks):
      newStock = Stock(self.STOCK_NAMES[i], self)
      stocks.append(newStock)
      i = i+1
    return stocks

  # Print out each stock
  def description(self):
    print(f'Market name: {self.name}')
    print(f'  current period: {Market.currentPeriod}')

    for stock in self.initialStocks:
        stock.description()


# In[2]:


from enum import Enum
import random

class BuyStrategy(Enum):
  RANDOM = 1
  BUY_GAINERS = 2 # stocks with current price > starting price
  BUY_LOSERS  = 3 # stocks with current price > starting price 

class SellStrategy(Enum):
  RANDOM = 1
  SELL_GAINERS = 2 
  SELL_LOSERS  = 3 

class Investor:
  def __init__(self, name, buyStrategy, sellStrategy):
    self.name = name
    self.allStocks = []

    if (buyStrategy in BuyStrategy.__members__):
      self.buyStrategy  = buyStrategy
    else:
      print(f'{buyStrategy} is not a valid buying strategy')

    if (sellStrategy in SellStrategy.__members__):
      self.sellStrategy  = sellStrategy
    else:
      print(f'{sellStrategy} is not a valid selling strategy')

  def name(self):
    return self.name

  def portfolio(self):
    return self.allStocks

  def addStockToPortfolio(self, stock):
    self.allStocks.append(stock)
    
  def createInitialPortfolioWithNumStocks(self, numStocks):
    # need to test numStocks is within bounds
    # Matt: for now, just implementing random strategy
    if (self.buyStrategy is BuyStrategy.RANDOM.name):
      self.allStocks = random.sample(Market.initialStocks, numStocks)
    else:
      # Matt: add conditions and code for other stradegies here
      print ("Under Construction: Only the RANDOM stategy is implemented at this time")
    
  def buyStrategy(self):
    return self.buyStrategy

  def sellStrategy(self):
    return self.sellStrategy

  def description(self):    
    print(f'Investor: {self.name}')
    print(f'  buy strategy:  {self.buyStrategy}')
    print(f'  sell strategy: {self.sellStrategy}')
    
    if (len(self.allStocks) == 0):
      print("    No stocks in portfolio")
    else:
      for stock in self.allStocks[:]:
        stock.description()


# In[3]:


from random import choices

####### Constants ######
## Stock Class ##
QUALITIES = ['good', 'bad']
QUALITY_WEIGHTS = [0.25, 0.75]
PRICE_CHANGES = [-3, -1, 1, 5]
PRICE_CHANGE_WEIGHTS_GOOD = [0.2, 0.2, 0.3, 0.3]
PRICE_CHANGE_WEIGHTS_BAD = [0.3, 0.3, 0.2, 0.2]
INITIAL_PRICE = 10

class Stock(object):

  def __init__(self, name, market):
    global QUALITIES, QUALITY_WEIGHTS, PRICE_CHANGES, PRICE_CHANGE_WEIGHTS_GOOD, PRICE_CHANGE_WEIGHTS_BAD
    
    self.name = name
    randQualityList = choices(QUALITIES, QUALITY_WEIGHTS) # random choice with weightings.
    self.quality = randQualityList[0]  # Get string from list
    self.priceChangeHistory = self.__createPriceChangeHistory()
    self.marketClass = market # needs to have backpointer to query the period
    self.initialPrice = INITIAL_PRICE

  def __createPriceChangeHistory(self):
    global QUALITIES, QUALITY_WEIGHTS, PRICE_CHANGE_WEIGHTS_GOOD, PRICE_CHANGE_WEIGHTS_BAD, PRICE_CHANGES
    generatedPriceChangeHistory = []
    
    if self.quality == 'good':
      weights = PRICE_CHANGE_WEIGHTS_GOOD
    else: 
      weights = PRICE_CHANGE_WEIGHTS_BAD

    generatedPriceChangeHistory = choices(PRICE_CHANGES, weights, k=10)
    return generatedPriceChangeHistory

  def name(self):
    return self.name

  def initialPrice(self):
    return self.initialPrice

  def priceForTestPeriod(self, periodNum):
    # get rid of the first three entries in the priceChangeHistory--they occurred before test begins
    priceChangeHistoryForTest = self.priceChangeHistory[3:]
    
    if periodNum > len(priceChangeHistoryForTest):
        print("ERROR: Asking for a test period that hasn't been created yet")
        print(f'    Period: {periodNum}, max defined periods: {len(priceChangeHistoryForTest)}')
        raise
        
    return self.initialPrice() + sum(priceChangeHistoryForTest[0:periodNum])

  def description(self):    
    print(f'Stock: {self.name}')
    print(f'  quality:                  {self.quality}')
    print(f'  price change history:     {self.priceChangeHistory[3:]}')
    
    if (Market.currentPeriod == 0):
      print(f'  price for current period: {self.initialPrice}')
    else:
      print(f'  price for current period: {self.priceForTestPeriod(self.marketClass.currentPeriod)}')


# In[4]:


market = Market('Changeable', 20)
market.description()


# In[5]:


investor = Investor("firstInvestor", 'RANDOM', 'RANDOM')


# In[6]:


investor.description()


# In[7]:


investor.createInitialPortfolioWithNumStocks(5)


# In[8]:


investor.description()


# In[ ]:




