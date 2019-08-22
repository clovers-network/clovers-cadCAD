# clovers-cadCAD

[cadCAD](https://github.com/BlockScience/cadCAD-Tutorials) notebooks for the [Clovers](https://clovers.network).

## Local Running !

Make sure you have python3 installed in order to use this project.

The first time you're starting to work with this project locally, you'll need to setup a virtual environment (for maintaining all the packages we need):
```
python -m venv venv
```

Required packages are installed via pip, and managed in the `requirements.txt`.

Each time you want to startup the jupyter server, we need to first activate the virtual environment (venv) and run the `install-packages.sh` script if we are running for the first time.

```
source venv/bin/activate
./install-packages.sh
```

Finally, run the jupyter server:
```
jupyter notebook
```
