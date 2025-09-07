# Evolutionary Machine Learning in Power Hungry Pets Card Game
[Power Hungry Pets](https://www.explodingkittens.com/products/power-hungry-pets) is a simple card game created by Seiji Kanai where players choose between two cards each turn by comparing their effects, and separately their values.

This repository implements a digital version of Power Hungry Pets, and Evolutionary Agents that play the game by evolving different priorities for each card under the selective pressures of competition with one another.

![alt text](https://www.explodingkittens.com/cdn/shop/files/PHP-COREFrontPackShot1400x1400_1300x.png?v=1704962327)

To download this repository:
```
git clone https://github.com/noahlb123/power-hungry-pets-evolution-ml
cd power-hungry-pets-evolution-ml
```

To run an evolutionary simulation:
```
python index.py
```
(you can change the number of training cycles, agents per game, and total agents in lines 269-271)

Deviations from Power Hungry Pets' rules:
* 4: no effect
* 7: instead of shuffling cards into the deck, players play cards as if a 5 were played against each of them, and then draw new cards
