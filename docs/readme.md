please install the python moduls and linux packages using

	pip3 install -r requirements.txt --upgrade
	cat requirements-apt.txt | xargs sudo apt install -y

and then ignore every change to the env file, if you want to upload something to github

	git update-index --assume-unchanged
