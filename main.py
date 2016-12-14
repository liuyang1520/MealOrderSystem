"""
We're ordering meals for a team lunch. Every member in the team needs one meal, some have dietary restrictions such as vegetarian, gluten free, nut free, and fish free. We have a list of restaurants which serve meals that satisfy some of these restrictions. Each restaurant has a rating, and a limited amount of meals in stock that they can make today. Implement an object oriented system with automated tests that can automatically produce the best possible meal orders with reasonable assumptions.
 
Example:
 
Team needs: total 50 meals including 5 vegetarians and 7 gluten free.
Restaurants: Restaurant A has a rating of 5/5 and can serve 40 meals including 4 vegetarians, 
Restaurant B has a rating of 3/5 and can serve 100 meals including 20 vegetarians, and 20 gluten free.
 
Expected meal orders: Restaurant A (4 vegetarian + 36 others), Restaurant B (1 vegetarian + 7 gluten free + 2 others)
"""
import collections
import unittest


# Define constant food names here
NORMAL = "normal"
VEGETARIAN = "vegetarian"
GLUTEN_FREE = "gluten_free"
NUT_FREE = "nut_free"
FISH_FREE = "fish_free"
TOTAL = "total"


class Restaurant(object):
	"""Restaurant model class
	We assume there will be multiple teams ordering food.
	So we use _capacity to track the total food can be provided,
	and _foodInStock to track the food left.
	These parameters can be refreshed manually or when re-init the object.
	"""
	def __init__(self, name, rate, capacity):
		"""
		Args:
			name: restaurant name, e.g., "rest1"
			rate: rate number, e.g., 5
			capacity: dictionary, e.g., {NORMAL: 38, VEGETARIAN: 5}
		"""
		self._name = name
		self._rate = rate
		self._capacity = capacity
		self._orderHistory = []
		# a deep copy would be better for safety issue, should be fine in this case
		self._foodInStock = capacity.copy()

	@property
	def name(self):
		return self._name

	@property
	def rate(self):
		return self._rate

	@property
	def capacity(self):
		return self._capacity

	@capacity.setter
	def capacity(self, capacity):
		# reset capacity, and food available
		self._capacity = capacity
		self._foodInStock = capacity.copy()

	def addOrder(self, teamName, order):
		"""Process order, record order in _orderHistory
		Args:
			teamName: the name of the team who orders the meal
			order: a dictionary of the order, should be assigned based on the current available food
		"""
		# simple validation for the order
		if not isinstance(order, dict):
			raise Exception("Param order should be a dictionary in method addOrder()")
		for meal in order:
			if meal not in self._foodInStock:
				raise Exception("The restaurant {} doesn't serve {}. Need to review order.".format(self._name, meal))
			if order[meal] > self._foodInStock[meal]:
				raise Exception("The order for {} is too much. Need to review order.".format(meal))
		# update food left in stock, and record the order
		for meal in order:
			self._foodInStock[meal] -= order[meal]
		self._orderHistory.append((teamName, order)) 

	@property
	def checkFood(self):
		return self._foodInStock

	def __str__(self):
		description = """
		================================
		Restaurant: {0}
		Rate: {1}
		Capacity: {2}
		Food Available: {3}
		Order History: {4}
		================================
		""".format(self._name, 
			self._rate, 
			OrderSystem.formatOrder(self._capacity), 
			OrderSystem.formatOrder(self._foodInStock), 
			OrderSystem.formatOrderList(self._orderHistory))
		return description


class Team(object):
	"""Team model class
	_orderResult stores the order history of current team.
	"""
	def __init__(self, name, demand):
		"""
		Args:
			name: a string of team name
			demand: a dictionary contains the orders for this team
		"""
		self._name = name
		self._demand = demand
		self._orderResult = []

	@property
	def demand(self):
		return self._demand

	@demand.setter
	def demand(self, demand):
		self._demand = demand

	@property
	def name(self):
		return self._name

	def addOrder(self, restName, order):
		# update orderResult
		self._orderResult.append((restName, order))

	def __str__(self):
		description = """
		================================
		Team: {0}
		Meal Order: {1}
		Order Result: {2}
		================================
		""".format(self._name, 
			OrderSystem.formatOrder(self._demand), 
			OrderSystem.formatOrderList(self._orderResult))
		return description


class OrderSystem(object):
	"""
	1. This class can be instantiated as a FIFO to process orders for multiple teams;
	2. This is also a delegation class, providing methods to optimize orders and format orders.
	optimizeOrder can be used as a stand alone method
	"""
	COMMON_INDENT = "\n" + "\t"*3
	FOODTYPE = [NORMAL, 
				VEGETARIAN, 
				GLUTEN_FREE, 
				NUT_FREE, 
				FISH_FREE]

	def __init__(self):
		self.FIFO = []

	def addTeam(self, team):
		if isinstance(team, Team):
			self.FIFO.append(team)
		elif isinstance(team, list):
			for i in team:
				self.FIFO.append(i)

	def processOrder(self, restaurantList, chooseLargeRestWhenEqualRate = False):
		while self.FIFO:
			team = self.FIFO.pop(0)
			OrderSystem.optimizeOrder(team, restaurantList, chooseLargeRestWhenEqualRate)

	@staticmethod
	def optimizeOrder(team, restaurantList, chooseLargeRestWhenEqualRate = False):
		"""Optimize the orders placed by the team with a greedy algorithm

		This method takes the team and restaurant information. Sort the restaurants according to their ratings, 
		and prefers larger restaurant (supplies more amount of meals) if chooseLargeRestWhenEqualRate is True.
		It places the order in both team and restaurant sides, updates the food in stock for restaurants.
		Returns a OrderDetail object which can be viewed by direct print statement.

		Args:
			team: a single Team model object
			restaurantList: a list of available Restaurant model objects
			chooseLargeRestWhenEqualRate: default to False
		Returns:
			None
		"""
		if not chooseLargeRestWhenEqualRate:
			restaurantList.sort(key = lambda x: x.rate, reverse = True)
		else:
			restaurantList.sort(key = lambda x: (x.rate, sum(x.checkFood().values())), reverse = True)
		demand, orderResultList = team.demand.copy(), []
		for rest in restaurantList:
			if sum(rest.checkFood.values()) == 0:
				continue
			orderResult = collections.OrderedDict()
			for foodType in OrderSystem.FOODTYPE:
				if foodType in demand and foodType in rest.checkFood:
					orderResult[foodType] = min(demand[foodType], rest.checkFood[foodType])
					demand[foodType] -= orderResult[foodType]
			orderResultList.append((rest.name, orderResult))
			# Place order in restaurant, team
			rest.addOrder(team.name, orderResult)
			team.addOrder(rest.name, orderResult)
		# check whether this team's order is successful
		for foodType in demand:
			if demand[foodType] > 0:
				raise Exception("Order from team-{} cannot be satisfied on food type {}".format(team.name, foodType))

	@staticmethod
	def formatOrder(order):
		"""Takes an order dictionary and return a formatted string
		Args:
			order: dictionary
		Returns:
			orderStr: a string
		"""
		orderStr = ""
		for foodType in OrderSystem.FOODTYPE:
			if foodType in order:
				orderStr += OrderSystem.COMMON_INDENT + "{foodType} = {count}".format(foodType = foodType, count = order[foodType])
		return orderStr

	@staticmethod
	def formatOrderList(orderList):
		"""Takes an order list and return a formatted string
		Args:
			order: list of dictionary
		Returns:
			orderStr: a string
		"""
		orderStr = ""
		for name, order in orderList:
			orderStr += OrderSystem.COMMON_INDENT + name + ":"
			for foodType in OrderSystem.FOODTYPE:
				if foodType in order:
					orderStr += OrderSystem.COMMON_INDENT + "\t{foodType} = {count}".format(foodType = foodType, count = order[foodType])
		return orderStr


class OrderSystemTests(unittest.TestCase):
	def testSingleTeamTestWithUniqueRates(self):
		team1 = Team("cisco1",  
			{	
				NORMAL: 38,
				VEGETARIAN: 5,
				GLUTEN_FREE: 7,
			})
		rest1 = Restaurant("rest1", 5, 
				{
					NORMAL: 36,
					VEGETARIAN: 4,
				})
		rest2 = Restaurant("rest2", 3, 
				{
					NORMAL: 60,
					VEGETARIAN: 20,
					GLUTEN_FREE: 20,
				})
		OrderSystem.optimizeOrder(team1, [rest1, rest2])
		print team1
		print rest1
		print rest2

	def testSingleTeamTestWithEqualRates(self):
		team1 = Team("cisco1",  
			{	
				NORMAL: 38,
				VEGETARIAN: 5,
				GLUTEN_FREE: 7,
			})
		rest1 = Restaurant("rest1", 5, 
				{
					NORMAL: 36,
					VEGETARIAN: 4,
				})
		rest2 = Restaurant("rest2", 3, 
				{
					NORMAL: 60,
					VEGETARIAN: 20,
					GLUTEN_FREE: 20,
				})
		OrderSystem.optimizeOrder(team1, [rest1, rest2])
		print team1
		print rest1
		print rest2

	def testMultipleTeamTest(self):
		team1 = Team("cisco1",  
			{	
				NORMAL: 38,
				VEGETARIAN: 5,
				GLUTEN_FREE: 7,
			})
		team2 = Team("cisco2",  
			{	
				NORMAL: 30,
				VEGETARIAN: 8,
				GLUTEN_FREE: 10,
			})
		rest1 = Restaurant("rest1", 5, 
				{
					NORMAL: 36,
					VEGETARIAN: 4,
				})
		rest2 = Restaurant("rest2", 3, 
				{
					NORMAL: 60,
					VEGETARIAN: 20,
					GLUTEN_FREE: 20,
				})
		orderSystem = OrderSystem()
		orderSystem.addTeam([team1, team2])
		orderSystem.processOrder([rest1, rest2])
		print team1
		print team2
		print rest1
		print rest2


if __name__ == "__main__":
	unittest.main()

