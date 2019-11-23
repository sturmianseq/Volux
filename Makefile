init:
		make install

test:
		py.test tests

build:
		python3 setup.py bdist_wheel sdist

install:
		pip install -r requirements.txt
		pip install dist/volux-*-*.whl

uninstall:
		pip uninstall volux -y

clean:
		rm -rf dist build *.egg-info .eggs

dev:
		make uninstall
		make clean
		make test
		make build
		make install

build-all:
		make build
		cd modules/voluxaudio && make build
		cd modules/voluxgui && make build
		cd modules/voluxlightvisualiser && make build

install-all:
		make install
		cd modules/voluxaudio && make install
		cd modules/voluxgui && make install
		cd modules/voluxlightvisualiser && make install

uninstall-all:
		make uninstall
		cd modules/voluxaudio && make uninstall
		cd modules/voluxgui && make uninstall
		cd modules/voluxlightvisualiser && make uninstall

clean-all:
		make clean
		cd modules/voluxaudio && make clean
		cd modules/voluxgui && make clean
		cd modules/voluxlightvisualiser && make clean

dev-all:
		make dev
		cd modules/voluxaudio && make dev
		cd modules/voluxgui && make dev
		cd modules/voluxlightvisualiser && make dev

gui:
		make dev
		volux launch

.PHONY: init test
