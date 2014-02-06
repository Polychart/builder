Polychart Dashboard Builder
===========================

Setting up a dev environment
----------------------------

Be sure to retrieve the repository's submodules:
 - `git submodule update --init --recursive`

It is recommended that a recent version of Node.js be installed:
 - `sudo apt-get install python-software-properties`
 - `sudo apt-add-repository ppa:chris-lea/node.js`
 - `sudo apt-get update`
 - `sudo apt-get install nodejs` (this include `npm`)

To see a list of dependencies, search for "package" in the
[Chef recipe](https://github.com/Polychart/deployment/blob/master/cookbooks/polychart/recipes/default.rb).

Install Python dependencies:
 - `sudo apt-get install python-setuptools python-virtualenv python2.7-dev`
 - `sudo pip install -U virtualenv`
 - `sudo pip install -r requirements`.

Install Node.js dependencies:
 - `npm install` (in the repo directory)
 - `sudo npm install -g grunt-cli`

Finally, run `grunt`.

