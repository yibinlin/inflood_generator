SRC=influence_simulation.py

all: demo

demo: 
	python $(SRC) -d 4 -p 0.93 -a 1.17

full: 
	python $(SRC) -d 140 -p 0.93 -a 1.17

