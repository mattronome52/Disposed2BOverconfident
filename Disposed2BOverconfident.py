#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/mattronome52/Disposed2BOverconfident/blob/master/Disposed2BOverconfident.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[ ]:


from random import choices
import json
from json import JSONEncoder

"""
A function takes in a custom object and returns a dictionary representation of the object.
This dict representation includes meta data such as the object's module and class names.
"""
def convertObjectToDict(obj):
  #  Populate the dictionary with object meta data 
  obj_dict = {
    "__class__": obj.__class__.__name__,
    "__module__": obj.__module__
  }
  #  Populate the dictionary with object properties
  obj_dict.update(obj.__dict__)
  return obj_dict

"""
Function that takes in a dict and returns a custom object associated with the dict.
This function makes use of the "__module__" and "__class__" metadata in the dictionary
to know which object type to create.
"""
def convertDictToObject(our_dict):
  if "__class__" in our_dict:
    # Pop ensures we remove metadata from the dict to leave only the instance arguments
    class_name = our_dict.pop("__class__")
    
    # Get the module name from the dict and import it
    module_name = our_dict.pop("__module__")
    
    # We use the built in __import__ function since the module name is not yet known at runtime
    module = __import__(module_name)
    
    # Get the class from the module
    class_ = getattr(module, class_name)
    
    # Use dictionary unpacking to initialize the object
    obj = class_(**our_dict)
  else:
    obj = our_dict
  return obj

## Stock Class ##
QUALITIES = ['good', 'bad']
QUALITY_WEIGHTS = [0.25, 0.75]
PRICE_CHANGES = [-3, -1, 1, 5]
PRICE_CHANGE_WEIGHTS_GOOD = [0.2, 0.2, 0.3, 0.3]
PRICE_CHANGE_WEIGHTS_BAD = [0.3, 0.3, 0.2, 0.2]
INITIAL_PRICE = 10

class Stock(object):
  def __init__(self, name, initialPrice = None, quality = None, priceChangeHistory = None, testing = False):
    self.name = name
    self.initialPrice = initialPrice
    self.quality = quality
    self.priceChangeHistory = priceChangeHistory

  def __createPriceChangeHistory(self):
    global QUALITIES, QUALITY_WEIGHTS, PRICE_CHANGE_WEIGHTS_GOOD, PRICE_CHANGE_WEIGHTS_BAD, PRICE_CHANGES
    generatedPriceChangeHistory = []
    
    if self.quality == 'good':
      weights = PRICE_CHANGE_WEIGHTS_GOOD
    else: 
      weights = PRICE_CHANGE_WEIGHTS_BAD

    generatedPriceChangeHistory = choices(PRICE_CHANGES, weights, k=10)
    return generatedPriceChangeHistory

  def initializeRandom(self):
    global QUALITIES, QUALITY_WEIGHTS, PRICE_CHANGES, PRICE_CHANGE_WEIGHTS_GOOD, PRICE_CHANGE_WEIGHTS_BAD
    
    self.initialPrice = INITIAL_PRICE
    randQualityList = choices(QUALITIES, QUALITY_WEIGHTS) # random choice with weightings.
    self.quality = randQualityList[0]  # Get string from list
    self.priceChangeHistory = self.__createPriceChangeHistory()

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

  def gainsPrevious(self):
    numberGainsPrevious = sum(1 for priceChangePrev in self.priceChangeHistory[:3] if priceChangePrev > 0)
    return numberGainsPrevious

  def toJSONString(self):
    return json.dumps(self, default=convertObjectToDict, sort_keys=True)

  @classmethod
  def fromJSONString(cls, jsonString):
    return json.loads(jsonString, object_hook=convertDictToObject)

  def description(self):    
    print(f'Stock: {self.name}')
    print(f'  quality:              {self.quality}')
    print(f'  initial price:        {self.initialPrice}')
    print(f'  price change history: {self.priceChangeHistory}')

    return
    # Can be used when integrated with Market class
    if (Market.currentPeriod == 0):
      print(f'  price for current period:  {self.initialPrice}')
    else:
      print(f'  price for current period:  {self.priceForTestPeriod(self.marketClass.currentPeriod)}')

    if (Market.currentPeriod == 0):
      print(f'  price for current period:  {self.initialPrice}')
    else:
      print(f'  price for current period:  {self.priceForTestPeriod(self.marketClass.currentPeriod)}')


# In[ ]:


## Market Class ##
import json
from collections import namedtuple

TEST_READ_STOCKS_FROM_FILE = "ReadStocksFromFile"
TEST_WRITE_STOCKS_TO_FILE = "WriteStocksToFile"

class Market(object):
  STOCK_NAMES = ["A", "B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","W","Z"]
  MAX_NUM_STOCKS = len(STOCK_NAMES)
  currentPeriod = 0
  outputTestStockFilename = 'TestStocks.json'

  def __init__(self, name, numStocks = 20, inputTestStockFilename = None, testMode = None):
    # print (f'testing is =====> {testMode}')
    if (numStocks > self.MAX_NUM_STOCKS):
      print(f"ERROR: No more than {len(self.MAX_NUM_STOCKS)} stocks can be created")
      raise
    self.name = name
    self.testMode = testMode
    
    if (testMode == TEST_READ_STOCKS_FROM_FILE):
      self.initialStocks = self.readStocksJSONFromFile(inputTestStockFilename)
    else:
      self.initialStocks = (self.__generateStocks(numStocks))
    
      if (testMode == TEST_WRITE_STOCKS_TO_FILE):
        self.__writeStocksJSONToFile()

  def __generateStocks(self, numStocks):
    i = 0
    stocks = []
    while (i < numStocks):
      newStock = Stock(self.STOCK_NAMES[i])
      newStock.initializeRandom()
      stocks.append(newStock)
      i = i+1
    return stocks

  def __writeStocksJSONToFile(self):
    testFileName = self.testStockFilename
    with open(testFileName, "w") as testStocksFile:
      testStocksFile.write(self.__encodeStocksToJSONString())

  def __encodeStocksToJSONString(self):
    # write them out as array of json-encoded Stocks
    encodedStocks = '['
    i = 0
    numStocks = len(self.initialStocks)
    while i < numStocks:
      encodedStocks = encodedStocks + self.initialStocks[i].toJSONString()
      if (i < numStocks - 1):
        encodedStocks = encodedStocks + ', \n'
      i = i + 1
    encodedStocks = encodedStocks + ']\n'    
    return encodedStocks

  def readStocksJSONFromFile(self, inputTestStockFilename):
    if (inputTestStockFilename is None):
      print(f"ERROR: Must supply name of input file.")
      raise
        
    stocks = []
    with open(inputTestStockFilename, "r") as testStocksFile:
      stockArray = json.load(testStocksFile)

    for stockDict in stockArray:
      # Matt: figure out why double quotes become single when reading in
      # until then, replace them since JSON needs double quotes
      dictString = str(stockDict)
      dictString = dictString.replace("\'", "\"")

      newStock = Stock.fromJSONString(dictString)
      stocks.append(newStock)
        
    return stocks

  def initialStocks(self):
    return self.initialStocks

  # Print out each stock
  def description(self):
    print(f'Market name: {self.name}')
    print(f'  current period: {Market.currentPeriod}')

    if (len(self.initialStocks) == 0):
      print("  Market has no stocks")
    else:
      for stock in self.initialStocks:
        stock.description()


# Currently, the filename for the archived stocks is TestStocks.json, which is in the repo.

# In[ ]:


from enum import Enum
import random

class BuyStrategy(Enum):
  RANDOM = 1
  BUY_GAINERS = 2 # stocks with current price > starting price

class SellStrategy(Enum):
  RANDOM = 1
  SELL_GAINERS = 2 
  SELL_LOSERS  = 3

class Investor:
  def __init__(self, name, market, buyStrategy, sellStrategy):
    self.name = name
    self.market = market
    self.portfolio = []

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

  def market(self):
    return self.market

  def portfolio(self):
    return self.portfolio

  def addStockToPortfolio(self, stock):
    self.portfolio.append(stock)
    
  def createInitialPortfolioWithNumStocks(self, numStocks):
    # need to test numStocks is within bounds
    # Matt: for now, just implementing random strategy
    if (self.buyStrategy is BuyStrategy.RANDOM.name):
      self.portfolio = random.sample(self.market.initialStocks, numStocks)
    elif (self.buyStrategy is BuyStrategy.BUY_GAINERS.name):
      # Katrin: Pick five stock at random and then go through market stocks and replace if more gains in previous periods
      stockMaxPrevGains = random.sample(self.market.initialStocks, numStocks)
      i = 0
      while (i < (len(self.market.initialStocks)-2)):
        currentGains = self.market.initialStocks[i].gainsPrevious()
        j = 0
        while (j < numStocks):
          if (currentGains > stockMaxPrevGains[j].gainsPrevious()):
            stockMaxPrevGains[j] = self.market.initialStocks[i]
            break
          j = j+1
        i = i+1
      self.portfolio = stockMaxPrevGains
    else:
      # Matt: add conditions and code for other stradegies here
      # Katrin: I added the buying gainers strategy. We do not need a buying losers strategy.
      print ("Invalid strategy")
    
  def buyStrategy(self):
    return self.buyStrategy

  def sellStrategy(self):
    return self.sellStrategy

  def description(self):    
    print(f'Investor: {self.name}')
    print(f'  buy strategy:  {self.buyStrategy}')
    print(f'  sell strategy: {self.sellStrategy}')
    
    if (len(self.portfolio) == 0):
      print("    No stocks in portfolio")
    else:
      for stock in self.portfolio[:]:
        stock.description()


# ## To verify the Buy Gainers strategy
# I created the testStocks_BuyGainers.json file that has only five gainers: stocks with names: A,G,J,O,T

# In[ ]:


import unittest
MARKET_NAME = 'marketUnitTest'
NUM_STOCKS = 20

class TestMarketClass(unittest.TestCase):
    
  def test_market_basic(self):
    marketName = MARKET_NAME + ".basic"
    self.market = Market(marketName, NUM_STOCKS)
    self.assertEqual(self.market.name, marketName)
    self.assertEqual(len(self.market.initialStocks), NUM_STOCKS)

  def test_market_read_stocks(self):
    marketName = MARKET_NAME + ".readFromFile"
    self.market = Market(marketName, NUM_STOCKS, "testStocks_17Stocks.json", testMode = "ReadStocksFromFile" )
    self.assertEqual(self.market.name, marketName)
    self.assertEqual(self.market.testMode, "ReadStocksFromFile")
    self.assertEqual(len(self.market.initialStocks), 17)
    
  def test_investor_buy_gains(self):
    correctSelection = ["A","G","J","O","T"] # The testStocks_BuyGainers.json file has only these gainers
    marketName = MARKET_NAME + ".buyGainers"
    self.market = Market(marketName, NUM_STOCKS, "testStocks_BuyGainers.json", testMode = "ReadStocksFromFile" )
    
    # test buy gainers strategy
    buyGainersInvestor = Investor("investor1", self.market, 'BUY_GAINERS', 'RANDOM')
    buyGainersInvestor.createInitialPortfolioWithNumStocks(5)
    
    gainersPortfolio = []
    for stock in buyGainersInvestor.portfolio:
      gainersPortfolio.append(stock.name)

    gainersPortfolio.sort()
    correctSelection.sort()
    
    # Matt: Katrin, I've added these lines to help in debugging. They should be removed later.
    print (f'gainersPortfolio: {gainersPortfolio}')
    print (f'correctSelection: {correctSelection}')

    self.assertEqual(gainersPortfolio, correctSelection)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)



# In[ ]:


correctSelection


# In[ ]:


investor2.description()


# In[ ]:




