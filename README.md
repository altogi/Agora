# Agora
Agora is a simulation of a physical free market, made up of fixed agents which sell and produce goods of their own production group and buy goods from other groups with their generated profit.

In this simulation, a number of market days are recreated. Consumer demand is fixed by assuming a number of goods from each production group to be consumed within a week, the duration of the latter being fixed by the user.

Agents interact in a physical, two-dimensional space, with the objective of generating profit. Agents are classified into production groups, such that each agent produces goods from its own goods and consumes from other production groups. Agents have two tasks: on the one hand, each agent is in charge of producing a stock of products of its own production group, and generating some profit by selling such goods to its neighboring consumers. On the other hand, the agent has also to buy products from neighboring producers, in order to fulfill its inherent needs.

__Process of selling:__ Before each market opening, all producers have to select a price and a number of goods to produce. Price is set based on how much it costs to produce a good from the agent's production group (costs whose evolution is set by the market), the personal production factor (dependent on the agent and set randomly), and the desired margin. This margin is set by the variation in the neighboring demand of the agent's good (calculated based on the consumption hierarchies of neighboring consumers) as well as by neighboring competitor prices. The amount to produce depends on the neighboring demand of the agent's good as well as on the profit obtained from the last day's transactions.

__Process of buying:__ Each consumer has a consumption hierarchy, showing its needs, and cash. It will look for neighboring procuders of its most important needs and buy if it can afford it, at the cheapest possible price. The consumption hierarchy of an agent is based on what it has not bought in the past few days.


