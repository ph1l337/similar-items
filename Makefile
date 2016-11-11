GCC=g++

SRC=src/main.cpp

similaritems: $(SRC)
	mkdir -p bin/
	$(GCC) $(SRC) -o bin/similaritems
