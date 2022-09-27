# billbalancer

Takes a list of bills paid by multiple people and will balance them and say who needs to pay who and how much

**This is not complete yet, but _somewhat_ usable.**

## Running it

Recommended to use [Conda](#conda), otherwise packages can be installed with venv or pip. 

### Requirements

- python (3.9)
- numpy (1.23.1)
- regex (2022.7.9)
- pandas (1.4.4)

### Conda

- Create environment with `conda env create -f environment.yml`
- To run with conda:
  - `conda activate billbalancer`
  - `python billbalancer.py`
- Export environment with `conda env export --no-builds | findstr -v "prefix" > environment.yml`

## TODO

- [ ] Upgrade to qt GUI interface
- [ ] Add option to increase print level to show intermediate calculations
- [ ] Add recurring bill (e.g. on the first from March to June 2022)
