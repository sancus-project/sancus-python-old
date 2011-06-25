.PHONY: all egg_info

all: egg_info

egg_info: setup.py
	python $^ egg_info
