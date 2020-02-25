# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# <a href="https://colab.research.google.com/github/mattronome52/Disposed2BOverconfident/blob/master/Disposed2BOverconfident.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %%

from random import choices
import json
from json import JSONEncoder
from copy import copy, deepcopy

CSV_DELIMITER = ";"

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
  def __init__(self, name, periodGenerated, initialPrice = None, quality = None, priceChangeHistory = None, testing = False, periodSold = None):
    self.name = name
    self.initialPrice = initialPrice
    self.quality = quality
    self.priceChangeHistory = priceChangeHistory
    self.periodGenerated = periodGenerated
    self.periodSold = periodSold
    self.testing = testing

  """
  implement copy and deepcopy on the Stock class to assign stocks from the market by value (as independent copies) 
  to investors during experiment periods.
  """
  __slots__ = 'a', '__dict__'
  def __copy__(self):
      return type(self)(self.name, self.periodGenerated, self.initialPrice, self.quality, self.priceChangeHistory, self.testing, self.periodSold)
  def __deepcopy__(self, memo): # memo is a dict of id's to copies
      id_self = id(self)        # memoization avoids unnecesary recursion
      _copy = memo.get(id_self)
      if _copy is None:
          _copy = type(self)(
              deepcopy(self.name, memo), 
              deepcopy(self.periodGenerated, memo),
              deepcopy(self.initialPrice, memo),
              deepcopy(self.quality, memo),
              deepcopy(self.priceChangeHistory, memo),
              deepcopy(self.testing, memo),
              deepcopy(self.periodSold, memo))
          memo[id_self] = _copy 
      return _copy

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

  def periodGenerated(self):
    return self.periodGenerated

  def periodSold(self):
    return self.periodSold

  def quality(self):
    return self.quality
  
  def priceChangeHistory(self):
    return self.priceChangeHistory

  def testing(self):
    return self.testing

  def priceForTestPeriod(self, periodNum):
    # get rid of the first three entries in the priceChangeHistory--they occurred before test begins
    priceChangeHistoryForTest = self.priceChangeHistory[3:]
    
    if periodNum > len(priceChangeHistoryForTest):
      print("ERROR: Asking for a test period that hasn't been created yet")
      print(f'    Period: {periodNum}, max defined periods: {len(priceChangeHistoryForTest)}')
      raise
        
    return self.initialPrice() + sum(priceChangeHistoryForTest[0:periodNum])

  def gainsPrevious(self):
    numberGainsPrevious = 0
    for num in self.priceChangeHistory[:3]:   
    # checking condition 
      if num >= 0: 
        numberGainsPrevious += 1
    return numberGainsPrevious

  def totalPriceChangeInPeriod(self, period):
    # Calculates the sum of price changes of the stock
    lastPeriod = period
    if(self.periodSold != None):
      lastPeriod = min(self.periodSold -1, period)
    periodsToSum = 11 - self.periodGenerated - (7 - lastPeriod)
    sumPreviousPriceChanges = sum(self.priceChangeHistory[3:periodsToSum])
    return sumPreviousPriceChanges

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
    print(f'  period generated:     {self.periodGenerated}')
    print(f'  period sold:          {self.periodSold}')

  @classmethod
  def headerCSV(self):
    csvHeader = "stockName" + CSV_DELIMITER + "stockQuality" + CSV_DELIMITER + "stockInitialPrice" + CSV_DELIMITER + "stockPriceChangeHistory" + CSV_DELIMITER + "stockPeriodGenerated" + CSV_DELIMITER + "stockPeriodSold" + CSV_DELIMITER + "stockGainsPrevious" + CSV_DELIMITER + "stockTotalPriceChange"
    return csvHeader

  def descriptionCSV(self):
    priceChangeHistoryString = ', '.join(map(str, self.priceChangeHistory))
    descCSV = self.name + CSV_DELIMITER + self.quality + CSV_DELIMITER + str(self.initialPrice) + CSV_DELIMITER + priceChangeHistoryString + CSV_DELIMITER + str(self.periodGenerated) + CSV_DELIMITER + str(self.periodSold) + CSV_DELIMITER + str(self.gainsPrevious()) + CSV_DELIMITER + str(self.totalPriceChangeInPeriod(7))
    return descCSV

    '''
    # Can be used when integrated with Market class
    if (Market.currentPeriod == 0):
      print(f'  price for current period:  {self.initialPrice}')
    else:
      print(f'  price for current period:  {self.priceForTestPeriod(self.marketClass.currentPeriod)}')

    if (Market.currentPeriod == 0):
      print(f'  price for current period:  {self.initialPrice}')
    else:
      print(f'  price for current period:  {self.priceForTestPeriod(self.marketClass.currentPeriod)}')
    '''


# %%
## Market Class ##
import json
from collections import namedtuple

TEST_READ_STOCKS_FROM_FILE = "ReadStocksFromFile"
TEST_WRITE_STOCKS_TO_FILE = "WriteStocksToFile"

class Market(object):
  STOCK_NAMES = ["A", "B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","W","Z"]
  MAX_NUM_STOCKS = len(STOCK_NAMES)
  currentPeriod = 1
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
      newStock = Stock(self.STOCK_NAMES[i], self.currentPeriod)
      newStock.initializeRandom()
      stocks.append(newStock)
      i = i+1
    return stocks
  
  # Katrin: This is the public method that I use from outside the market class
  def updateStocks(self, numStocks):
    self.initialStocks = self.__generateStocks(numStocks)

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
      

# %% [markdown]
# Currently, the filename for the archived stocks is TestStocks.json, which is in the repo.

# %%
from enum import Enum
import random

class BuyStrategy(Enum):
  RANDOM = 1
  BUY_GAINERS = 2 # stocks with most up ticks, i.e., price increases

class SellStrategy(Enum):
  RANDOM = 1
  SELL_GAINERS = 2 # stocks with current price > starting price
  SELL_LOSERS  = 3 # stocks with current price < starting price

class Investor:
  def __init__(self, name, market, buyStrategy, sellStrategy):
    self.name = name
    self.market = market
    self.portfolio = []
    # I want to have a list with stocks that were in the investor's portfolio but were sold at some point
    self.soldStocks = []


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

  def soldStocks(self):
    return self.soldStocks

  def addStockToPortfolio(self, stock):
    self.portfolio.append(stock)
    
  def createInitialPortfolioWithNumStocks(self, numStocks, testing = False, inputTestStockFilename = None):
    # need to test numStocks is within bounds
    # Matt: for now, just implementing random strategy
    if (testing == True):
      self.portfolio = self.market.readStocksJSONFromFile(inputTestStockFilename)
    else:
      if (self.buyStrategy is BuyStrategy.RANDOM.name):
        self.portfolio = random.sample(self.market.initialStocks, numStocks)
      elif (self.buyStrategy is BuyStrategy.BUY_GAINERS.name):
          # Katrin: I changed the buying strategy in order to avoid dups. I use your dictionary approach.
          stockGainersMarketDict = {}
          i = 0
          while (i < (len(self.market.initialStocks))):
              stockToDict = deepcopy(self.market.initialStocks[i])
              stockGainersMarketDict[stockToDict] = stockToDict.gainsPrevious()
              i = i+1
          
          self.portfolio = sorted(stockGainersMarketDict, reverse=True, key=stockGainersMarketDict.__getitem__)[:numStocks]              
      # Matt: add conditions and code for other stradegies here
      # Katrin: I added the buying gainers strategy. We do not need a buying losers strategy.
      else: 
          print ("Invalid strategy")


# Buying stock following the initial period (buy one stock)
  def createPeriodPortfolioWithNumStocks(self, numStocks):
    if (self.buyStrategy is BuyStrategy.RANDOM.name):
      tempPortfolio = random.sample(self.market.initialStocks, numStocks)
      for thisStock in tempPortfolio:
        self.portfolio.append(thisStock)
    elif (self.buyStrategy is BuyStrategy.BUY_GAINERS.name):
        stockGainersMarketDict = {}
        i = 0
        while (i < (len(self.market.initialStocks))):
            stockToDict = deepcopy(self.market.initialStocks[i])
            stockGainersMarketDict[stockToDict] = stockToDict.gainsPrevious()
            i = i+1
        
        tempPortfolio = sorted(stockGainersMarketDict, reverse=True, key=stockGainersMarketDict.__getitem__)[:numStocks]
        for thisStock in tempPortfolio:
          self.portfolio.append(thisStock)

    else: 
        print ("Invalid buying strategy")

# Selling strategies
# Remove stock from investor portfolio, add the selling period as info, and append it to the "sold stocks" list in order to keep track of the sold stocks
  def sellStocks(self, numStocks):
    if (self.sellStrategy is SellStrategy.RANDOM.name):
      randomStockFromPortfolio = random.choice(self.portfolio)
      randomStockFromPortfolio.periodSold = self.market.currentPeriod
      self.portfolio.remove(randomStockFromPortfolio)
      self.soldStocks.append(randomStockFromPortfolio)

# I create a copy of the portfolio with only the gainers or only the losers and then choose one stock randomly
    elif (self.sellStrategy is SellStrategy.SELL_GAINERS.name):
      gainersPortfolioDict = self.portfolio.copy()
      for currentStock in self.portfolio:
        if currentStock.totalPriceChangeInPeriod(self.market.currentPeriod) <= 0:
          gainersPortfolioDict.remove(currentStock)
      if len(gainersPortfolioDict) > 0:
        pickGainerStockFromPortfolio = random.choice(gainersPortfolioDict)
        pickGainerStockFromPortfolio.periodSold = self.market.currentPeriod
        self.portfolio.remove(pickGainerStockFromPortfolio)
        self.soldStocks.append(pickGainerStockFromPortfolio)
      else:
        randomStockFromPortfolio = random.choice(self.portfolio)
        randomStockFromPortfolio.periodSold = self.market.currentPeriod
        self.portfolio.remove(randomStockFromPortfolio)
        self.soldStocks.append(randomStockFromPortfolio)

    elif (self.sellStrategy is SellStrategy.SELL_LOSERS.name):
      losersPortfolioDict = self.portfolio.copy()
      for currentStock in self.portfolio:
        if currentStock.totalPriceChangeInPeriod(self.market.currentPeriod) >= 0:
          losersPortfolioDict.remove(currentStock)
      if len(losersPortfolioDict) > 0:
        pickLoserStockFromPortfolio = random.choice(losersPortfolioDict)
        pickLoserStockFromPortfolio.periodSold = self.market.currentPeriod
        self.portfolio.remove(pickLoserStockFromPortfolio)
        self.soldStocks.append(pickLoserStockFromPortfolio)
      else:
        randomStockFromPortfolio = random.choice(self.portfolio)
        randomStockFromPortfolio.periodSold = self.market.currentPeriod
        self.portfolio.remove(randomStockFromPortfolio)
        self.soldStocks.append(randomStockFromPortfolio)
    
    else:
      print ("Invalid selling strategy")

  def buyStrategy(self):
    return self.buyStrategy

  def sellStrategy(self):
    return self.sellStrategy

  def numGoodStocksSold(self):
    numGoodStock = sum(soldStock.quality == 'good' for soldStock in self.soldStocks)
    return numGoodStock

  def numGoodStocksInitial(self):
    numGoodStockSoldFromPeriod1 = sum((soldStock.quality == 'good' and soldStock.periodGenerated == 1) for soldStock in self.soldStocks)
    numGoodStocksInPortfolioFromPeriod1 = sum((stock.quality == 'good' and stock.periodGenerated == 1) for stock in self.portfolio)
    numGoodStocksInitial = numGoodStockSoldFromPeriod1 + numGoodStocksInPortfolioFromPeriod1
    return numGoodStocksInitial

  def numGoodStocksEnd(self):
    numGoodStocksInPortfolio = sum((stock.quality == 'good') for stock in self.portfolio)
    return numGoodStocksInPortfolio

  def numGoodStocksPicked(self):
    numGoodStocksPicked = self.numGoodStocksEnd() + self.numGoodStocksSold()
    return numGoodStocksPicked

  def numGainersSold(self):
    numGainersSold = sum(soldStock.totalPriceChangeInPeriod(soldStock.periodSold - 1) > 0 for soldStock in self.soldStocks)
    return numGainersSold

  def numGainersInPortfolio(self):
    numGainersInPortfolio = sum(stock.totalPriceChangeInPeriod(self.market.currentPeriod) > 0 for stock in self.portfolio)
    return numGainersInPortfolio

  def totalEarnings(self):
    earningsFromSold = sum(soldStock.totalPriceChangeInPeriod(soldStock.periodSold - 1) for soldStock in self.soldStocks)
    earningsInPortfolio = sum(stock.totalPriceChangeInPeriod(self.market.currentPeriod) for stock in self.portfolio)
    totalEarnings = earningsFromSold + earningsInPortfolio
    return totalEarnings

  def totalUpticks(self):
    upticsInSold = sum(sum(priceChange > 0 for priceChange in stock.priceChangeHistory[:(11 - stock.periodGenerated - (7 - stock.periodSold + 1))]) for stock in self.soldStocks)
    upticsInPortfolio = sum(sum(priceChange > 0 for priceChange in stock.priceChangeHistory[:(11 - stock.periodGenerated - (7 - self.market.currentPeriod))]) for stock in self.portfolio)
    totalUpticks = upticsInSold + upticsInPortfolio
    return totalUpticks   
    
  def description(self):    
    print(f'Investor: {self.name}')
    print(f'  buy strategy:  {self.buyStrategy}')
    print(f'  sell strategy: {self.sellStrategy}')
    
    if (len(self.portfolio) == 0):
      print("    No stocks in portfolio")
    else:
      for stock in self.portfolio[:]:
        stock.description()
    
    if (len(self.soldStocks) == 0):
      print("    No stocks in sold stocks portfolio")
    else:
      for stock in self.soldStocks[:]:
        stock.description()

  @classmethod
  def headerCSV(self):
    csvHeader = "investorName" + CSV_DELIMITER + "marketName" + CSV_DELIMITER + "buyStrategy" + CSV_DELIMITER + "sellStrategy" + CSV_DELIMITER + "numGoodStocksInitial" + CSV_DELIMITER + "numGoodStocksSold" + CSV_DELIMITER + "numGoodStocksEnd" + CSV_DELIMITER + "numGoodStocksPicked" + CSV_DELIMITER + "numGainersSold" + CSV_DELIMITER + "numGainersInPortfolio" + CSV_DELIMITER + "totalEarnings" + CSV_DELIMITER + "totalUpticks"
    return csvHeader

  @classmethod
  def headerCSVAllStocks(self):
    return Investor.headerCSV() + CSV_DELIMITER + Stock.headerCSV()

  def descriptionCSV(self):
    descCSVString = self.name + CSV_DELIMITER + self.market.name + CSV_DELIMITER + self.buyStrategy + CSV_DELIMITER + self.sellStrategy + CSV_DELIMITER + str(self.numGoodStocksInitial()) + CSV_DELIMITER + str(self.numGoodStocksSold()) + CSV_DELIMITER + str(self.numGoodStocksEnd()) + CSV_DELIMITER + str(self.numGoodStocksPicked()) + CSV_DELIMITER + str(self.numGainersSold()) + CSV_DELIMITER + str(self.numGainersInPortfolio()) + CSV_DELIMITER + str(self.totalEarnings()) + CSV_DELIMITER + str(self.totalUpticks())
    return descCSVString
    
  def descriptionCSVAllStocks(self):
    CSVresult = ""
    investorDescriptionCSV = self.descriptionCSV()
    for currentStock in self.portfolio:
      stockCSV = investorDescriptionCSV + CSV_DELIMITER + currentStock.descriptionCSV() + "\n"
      CSVresult = CSVresult + stockCSV
    for currentStock in self.soldStocks:
      stockCSV = investorDescriptionCSV + CSV_DELIMITER + currentStock.descriptionCSV() + "\n"
      CSVresult = CSVresult + stockCSV


    return CSVresult

# %% [markdown]
# ## To verify the Buy Gainers strategy
# I created the testStocks_BuyGainers.json file that has only five gainers: stocks with names: A,G,H,J,O

# %%
import unittest
MARKET_NAME = 'marketUnitTest'
NUM_STOCKS = 20

class TestMarketClass(unittest.TestCase):
# Katrin: I added information "periodGenerated" to the json files
    
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
    correctSelection = ["A","G","H","J","O"] # The testStocks_BuyGainers.json file has only these gainers
    # Katrin: I changed this correct selection from ["A","G","J","O","T"] to ["A","G","H","J","O"] because of different buying rule
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

# %% [markdown]
# Unit tests for selling strategies and calculations

# %%
# Unittest for selling strategies

# Testing sell gainer strategy

class TestInvestorClass(unittest.TestCase):

    def test_investor_sell_gains(self):
        correctSelection_SG = ["I", "M", "P", "R"] # The testStocks_SellGainers.json file has only one gainer ("B")

        marketName = "Market.sellGainers"
        self.market = Market(marketName, 20, "testStocks_SellGainers.json", testMode = "ReadStocksFromFile")
        
        # test sell gainers strategy
        sellGainerInvestor = Investor("investor1", self.market, 'BUY_GAINERS', 'SELL_GAINERS')
        sellGainerInvestor.createInitialPortfolioWithNumStocks(5, testing = True, inputTestStockFilename = "testStocks_SellGainers.json")
        
        self.market.currentPeriod = 6

        sellGainerInvestor.sellStocks(1)
        
        sellGainerPortfolio = []
        for stock in sellGainerInvestor.portfolio:
            sellGainerPortfolio.append(stock.name)

        sellGainerPortfolio.sort()
        correctSelection_SG.sort()
        
        print (f'sellGainerPortfolio: {sellGainerPortfolio}')
        print (f'correctSelection_SG: {correctSelection_SG}')

        self.assertEqual(sellGainerPortfolio, correctSelection_SG)


# Testing sell loser strategy

    def test_investor_sell_losers(self):
        correctSelection_SL = ["B", "I", "M", "P"] # The testStocks_SellLosers.json file has only one loser ("R")

        marketName = "Market.sellLosers"
        self.market = Market(marketName, 20, "testStocks_SellLosers.json", testMode = "ReadStocksFromFile")
        
        # test sell losers strategy
        sellLoserInvestor = Investor("investor2", self.market, 'BUY_GAINERS', 'SELL_LOSERS')
        sellLoserInvestor.createInitialPortfolioWithNumStocks(5, testing = True, inputTestStockFilename = "testStocks_SellLosers.json")

        self.market.currentPeriod = 6

        sellLoserInvestor.sellStocks(1)
        
        sellLoserPortfolio = []
        for stock in sellLoserInvestor.portfolio:
            sellLoserPortfolio.append(stock.name)

        sellLoserPortfolio.sort()
        correctSelection_SL.sort()
        
        print (f'sellLoserPortfolio: {sellLoserPortfolio}')
        print (f'correctSelection_SL: {correctSelection_SL}')

        self.assertEqual(sellLoserPortfolio, correctSelection_SL)

# Testing calculations for result files

    def test_investor_calculations(self):
        marketName = "Market.CalculationTests"
        self.market = Market(marketName, 20, "testStocks_SellLosers.json", testMode = "ReadStocksFromFile")
        
        calculationsTestInvestor = Investor("investor2", self.market, 'BUY_GAINERS', 'SELL_GAINERS')
        calculationsTestInvestor.portfolio = self.market.readStocksJSONFromFile('testPortfolio_Calculations.json')
        calculationsTestInvestor.soldStocks = self.market.readStocksJSONFromFile('testSoldStocks_Calculations.json')

        self.market.currentPeriod = 7

        calculationsTestInvestor.numGoodStocksInitial()
        self.assertEqual(calculationsTestInvestor.numGoodStocksInitial(), 1)

        calculationsTestInvestor.numGoodStocksSold()
        self.assertEqual(calculationsTestInvestor.numGoodStocksSold(), 3)

        calculationsTestInvestor.numGoodStocksEnd()
        self.assertEqual(calculationsTestInvestor.numGoodStocksEnd(), 1)

        calculationsTestInvestor.numGoodStocksPicked()
        self.assertEqual(calculationsTestInvestor.numGoodStocksPicked(), 4)

        calculationsTestInvestor.numGainersSold()
        self.assertEqual(calculationsTestInvestor.numGainersSold(), 4)

        calculationsTestInvestor.numGainersInPortfolio()
        self.assertEqual(calculationsTestInvestor.numGainersInPortfolio(), 2)

        calculationsTestInvestor.totalEarnings()
        self.assertEqual(calculationsTestInvestor.totalEarnings(), 11)

        calculationsTestInvestor.totalUpticks()
        self.assertEqual(calculationsTestInvestor.totalUpticks(), 37)


# %%
# Run unit tests

if __name__ == '__main__':
   unittest.main(argv=['first-arg-is-ignored'], exit=False)


# %%
# Main: Simulation Experiment

import datetime
import os
# Generate the market
def market_experiment(experimentId = 'no_experiment_id_set', useSharedMarket = True, buyStrategy = 'BUY_GAINERS', sellStrategy = 'SELL_GAINERS', numInvestors = 20, numPeriods = 7, portfolioSize = 5, newStocksPerPeriod = 4):
  
  marketNameBase = "market"
  NUM_INVESTORS = numInvestors
  NUM_PERIODS = numPeriods
  CURRENT_PERIOD = 1
  PORTFOLIO_SIZE = portfolioSize
  NEW_STOCKS_PER_PERIOD = newStocksPerPeriod

  # validate buy and sell strategies
  if (buyStrategy in BuyStrategy.__members__):
    BUY_STRATEGY  = buyStrategy
  else:
    print(f'{buyStrategy} is not a valid buying strategy')
    return
  
  if (sellStrategy in SellStrategy.__members__):
    SELL_STRATEGY  = sellStrategy
  else:
    print(f'{sellStrategy} is not a valid selling strategy')
    return

  # if all investors are supposed to share a market, create only one global market
  if(useSharedMarket == True):
    globalMarket = Market(marketNameBase + '_global', NUM_PERIODS)
  
  # Generate the investors and initial portfolio
  marketInvestors = []
  i = 0
  while (i < NUM_INVESTORS):
    # if investors get individual market, create one for each investor, otherwise assign global market
    if(useSharedMarket == False):
      investorMarket = Market(marketNameBase + '_' + str(i), NUM_PERIODS)
      newInvestor = Investor("investor" + str(i), investorMarket, BUY_STRATEGY, SELL_STRATEGY)
    else:
      newInvestor = Investor("investor" + str(i), globalMarket, BUY_STRATEGY, SELL_STRATEGY)
    
    newInvestor.createInitialPortfolioWithNumStocks(PORTFOLIO_SIZE)
    marketInvestors.append(newInvestor)
    i = i + 1

  # Revise portfolio each period
  while (CURRENT_PERIOD < NUM_PERIODS):
    
    # set market period to next period (both global ind individual markets)
    CURRENT_PERIOD = CURRENT_PERIOD + 1
    if(useSharedMarket == True):
      globalMarket.currentPeriod = CURRENT_PERIOD
    else:
      for currentInvestor in marketInvestors:
        currentInvestor.market.currentPeriod = CURRENT_PERIOD
    
    # in each period: generate new stocks and perform buy / sell operations
    if(useSharedMarket == True):
      globalMarket.updateStocks(NEW_STOCKS_PER_PERIOD)
    for currentInvestor in marketInvestors:
      if(useSharedMarket == False):
        currentInvestor.market.updateStocks(NEW_STOCKS_PER_PERIOD)
      currentInvestor.sellStocks(1)
      currentInvestor.createPeriodPortfolioWithNumStocks(1)

  # print all investors into verbose output (uncomment to see in terminal)
  # for currentInvestor in marketInvestors:   
  #  currentInvestor.description()
  
    # create file names and correct path
  currentTimeString = datetime.datetime.now().strftime("%y%m%d_%H%M")
  scriptDir = os.path.join(os.path.abspath(''), "results")
  os.makedirs(scriptDir, exist_ok=True) 
  
  # write to file (create if not found, overwrite otherwise)
  # write investor summary file
  fileNameInvestors = currentTimeString + "_" + experimentId + "_investors.csv"
  completePathInvestors = os.path.join(scriptDir, fileNameInvestors)
  resultFile = open(completePathInvestors,"w") 
  resultFile.write(Investor.headerCSV() + "\n")
  for currentInvestor in marketInvestors: 
    resultFile.write(currentInvestor.descriptionCSV() + "\n")
  resultFile.close() 

  # write file with complete stock output
  fileNameStocks = currentTimeString + "_" + experimentId + "_stocks.csv"
  completePathStocks = os.path.join(scriptDir, fileNameStocks)
  resultFile = open(completePathStocks,"w") 
  resultFile.write(Investor.headerCSVAllStocks() + "\n")
  for currentInvestor in marketInvestors: 
    resultFile.write(currentInvestor.descriptionCSVAllStocks() + "\n")
  resultFile.close()
  
# run the simulation
''' 
signature: 
  market_experiment(
  experimentId = 'no_experiment_id_set', 
  useSharedMarket = True, 
  buyStrategy = 'BUY_GAINERS', 
  sellStrategy = 'SELL_GAINERS', 
  numInvestors = 20, 
  numPeriods = 7, 
  portfolioSize = 5, 
  newStocksPerPeriod = 4)
'''

#market_experiment("shared_market_test",True)
#market_experiment("individual_markets_test",False)
market_experiment("individual_markets-gainers_test",False,'BUY_GAINERS','SELL_GAINERS', 60)
market_experiment("individual_markets-losers_test",False,'BUY_GAINERS','SELL_LOSERS', 60)
market_experiment("individual_markets-rand-gainers_test",False,'RANDOM','SELL_GAINERS', 60)
market_experiment("individual_markets-rand-losers_test",False,'RANDOM','SELL_LOSERS', 60)


# %%


