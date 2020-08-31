import numpy as np

#Here, the class defining the actions of a market agent is established. On the one hand, the agent is in charge of producing
#a stock of products of its own production group, and generating some profit by selling such goods to its neighboring consumers.
#On the other hand, the agent has also to buy products from neighboring producers, in order to fulfill inherent needs.

#Process of buying: Each consumer has a consumption hierarchy and cash. It will look for
#neighboring procuders of its most important needs and buy if it can afford it, at the cheapest price. Consumption hierarchy
#is based on what they havent bought in the past few days.

#Process of selling: Before each market opening, all producers have to select a price and an inventory size. Price is set
#based on how much it costs to produce (whose evolution is set by the market), the personal production factor dependent
# on the agent (set to be random), and the desired margin. This margin is set by the neighboring demand score (calculated
#based on the consumption hierarchies of neighboring consumers) as well as neighboring competitor prices. The amount to produce
#depends on the saving percentage, the remaining free inventory, anf the neighboring demand sscore.

class agent:
    """Class defining a consumer/producer. Inputs:
    market: market class containing all neighboring consumers
    cash: initial cash of agent
    price0: initial selling price of seller
    quantity0: initial stock
    position: position of agent within agora
    group: Producer clan
    prod: Deviation from base production cost
    rSell: Radius of proximity detecting demand and prices
    rBuy: Radius of proximity detecting supply and prices
    save: Ratio of cash to be saved each day
    """
    def __init__(self, market, cash0, price0, quantity0, position, group=0, prod=0.01, rSell=1.1, rBuy=1.1, save=0.25):
        self.market = market
        self.cash = cash0
        self.price = price0
        self.stock = quantity0
        self.position = position
        self.group = group
        self.prod = prod + 1
        self.rSell = rSell
        self.rBuy = rBuy
        self.save = save

        self.demand0 = self.market.needs[group]
        self.cash0 = cash0

        # Array showing all transactions of agent.
        # First col: 1 if buy, -1 if sell, 0 is produce. Second col: Price, or production cost. Third col: Agent's Cash before transaction.
        # Fourth col: Sellers stock before transaction, or when producing, items produced. Fifth col: Product group
        self.transactions = np.array([[-1, 0, 0, 0, 0]])

        self.resetNeeds()

    def resetNeeds(self):
        """Reset consumers needs after a new week"""
        # consumerHierarchy is simply a list which, for each production group in the market, stores the number of items each consumer
        #requires per week
        self.consumerHierarchy = self.market.needs.copy()

    def openStore(self):
        """Routine which each producer carries out every day"""
        self.seeDemandandCompetitors()
        self.setPrice()
        self.setQuantity()
        self.produce()
        self.coherenceCheck()

    def seeDemandandCompetitors(self):
        """Examine neighboring consumers in order to see what the neighboring demand score is. Also examine neighboring
        competitor producers to see what the selling price usually is."""
        _, nbrs = self.market.nbrs.radius_neighbors(X=self.position, radius=self.rSell, sort_results=True)
        nbrs = nbrs[0][1:]
        self.demand = 0
        for n in nbrs:
            self.demand += self.market.agents[n].consumerHierarchy[self.group]

        competitors = [n for n in nbrs if self.market.groups[n] == self.group]
        self.competitorPrices = [self.market.agents[p].price for p in competitors]

    def setPrice(self, maxPercentile=50):
        """Here is were we definitely model reality. Set a price based on how much demand has varied wrt the previous day,
        and a maxPercentile of the price within the prices of neighboring competitors."""
        self.costPerUnit = self.market.prodCosts[self.group] * self.prod
        demandChange = 1 + (self.demand - self.demand0 + 0.00001) / (self.demand0 + 0.00001)
        basePrice = self.costPerUnit * demandChange

        if len(self.competitorPrices) > 0:
            competitivePrice = np.percentile(self.competitorPrices, maxPercentile)
            desired = max(basePrice, competitivePrice)
        else:
            desired = basePrice

        self.price = max(self.costPerUnit, desired)
        self.demand0 = self.demand

    def setQuantity(self):
        """Simply determine the quantity to produce based on current stock, existing demand, and available cash"""
        profit = self.cash - self.cash0
        self.cash0 = self.cash
        available = profit * (1 - self.save)
        toMake = self.demand - self.stock

        if toMake < 0:
            self.canMake = 0
        else:
            self.canMake = min(toMake, np.floor(available / self.costPerUnit))

    def produce(self):
        """Update existing cash and stock based on production"""
        if self.canMake > 0:
            self.cash -= self.canMake * self.costPerUnit
            self.stock += self.canMake
            self.transactions = np.vstack((self.transactions, np.array([0, self.costPerUnit, self.cash + self.canMake * self.costPerUnit, self.canMake, self.group])))

    def sell(self):
        """Update existing cash and stock based on selling"""
        self.cash += self.price
        self.stock -= 1

        self.transactions = np.vstack((self.transactions, np.array([-1, self.price, self.cash - self.price, self.stock + 1, self.group])))

    def shoppingRoutine(self, reset=False):
        """Shopping routine of consumer"""
        self.seeSupply()
        self.buyAsNeeded()
        self.coherenceCheck()

        if reset:
            self.resetNeeds()

    def seeSupply(self):
        """For each need of the consumer, see neighboring producer with the cheapest price"""
        _, nbrs = self.market.nbrs.radius_neighbors(X=self.position, radius=self.rBuy, sort_results=True)
        nbrs = nbrs[0]
        self.myself = nbrs[0]
        nbrs = nbrs[1:]
        self.cheapest = []
        for g in range(self.market.Ng):
            if g == self.group: #The fisherman can get fish himself, at production cost
                if self.stock > 0:
                    self.cheapest.append(self.myself)
                else:
                    self.cheapest.append(-1)
            else:
                producers = [n for n in nbrs if self.market.groups[n] == g]
                if len(producers) > 0:
                    prices = [self.market.agents[p].price for p in producers]
                    stock = [self.market.agents[p].stock for p in producers]
                    new = -1
                    for p in np.argsort(prices):
                        if stock[p] > 0:
                            new = producers[p]
                            break
                    self.cheapest.append(new)
                else:
                    self.cheapest.append(-1)

    def buyAsNeeded(self):
        good = -1
        sorted = np.argsort(self.consumerHierarchy)[::-1]
        for i in sorted:
            if self.cheapest[i] != -1 and self.consumerHierarchy[i] > 0:
                seller = self.cheapest[i]
                price = self.market.agents[seller].price
                if self.cash > price:
                    good = i
                    break

        if good != -1:
            self.market.agents[seller].sell()
            self.cash -= price
            self.consumerHierarchy[good] -= 1
            self.transactions = np.vstack((self.transactions, np.array([1, price, self.cash - price, self.market.agents[seller].stock + 1, good])))
            self.market.contacts = np.vstack((self.market.contacts, np.array([self.market.day, self.myself, seller])))

    def coherenceCheck(self):
        if self.cash < 0:
            print('Agent cash is negative.')
            print(self.transactions[-5:, :])

        if self.stock < 0:
            print('Agent stock is negative.')
            print(self.transactions[-5:, :])
