## AsyncIO Sitemap Generator ##

The repository contains the project files required by python test

### Python Version
3.5

### Installation

Clone the repo to your local machine
```
git clone [repo_url]
```

it is recommended to use Virtualenvwrapper:

```
$ pip3 install virtualenvwrapper
...
$ export WORKON_HOME=~/.virtualenvs
$ mkdir -p $WORKON_HOME
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv sitemap
```

Install requirements
```
$ cd asyncio-sitemap
$ pip3 install -r requirements.txt
```

To use the script from terminal
```
./sitemap_generator.py -n 5 -o sitemap.xml http://centione.com
```

You can view the help
```
./sitemap_generator.py -h
```

You can also import SitemapGenerator and use it from your code
```python
gen = SitemapGenerator(URL, NUM, OUTPUT)
gen.generate_sitemap()
```

The project inspired by [sitemap-generator by Haikson](https://github.com/Haikson/sitemap-generator)