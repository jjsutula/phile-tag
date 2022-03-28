# phile-tag
A Python Flask project to examine and change metadata for local music files.

To run, use the following shell script:
    ./run

## Installattion Instructions

**Set up the Conda environment**
Make sure Conda is up to date:
```
conda update -n base -c defaults conda
```

Create a new Conda environment:
```
conda create -n phileTag
```

Activate Conda:
```
conda activate phileTag
```

Install modules:
```
    conda install -c conda-forge mutagen
    conda install flask
    conda install -c conda-forge flask-bootstrap
    conda install flask-wtf
    conda install -c conda-forge python-dotenv
```
