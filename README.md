# MealOrderSystem
This is a simple meal order system designed for Cisco.

To clone it
```bash
git clone https://github.com/liuyang1520/MealOrderSystem
```

To run it with *Python 2.7*
```bash
python main.py -v
```

Two assumptions:

1. Whenever there is a tie in the rates, we can choose to follow the origin order among restaurants, or prefer the larger restaurants. People tend to get most of things done in one large place in daily lives.
2. There is a FIFO system when there are two or more teams ordering food.
