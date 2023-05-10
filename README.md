# Automating Cisco Firewall Management Center

It is a set Python script to automate Cisco Firewall Management Center provision process.

## Prerequisites

Basic Requirement
- Python 3.x (with PIP installed)
- Cisco Firepower Management Center API access

Install additional Python packages.
```bash
pip install -r pip-requirements.txt
```

## Usage

### Configuration files
Scripts will read the build information (e.g. credentials & build parameters) from following files, hence please update them before run the script(s).
- settings.yml
- fmc-object.csv
- fmc-interface.csv
- fmc-static-route.csv

### Script Files
OPTION 1 (recommended)
- Run the master shell script which will executes all Python scripts sequentially.
```python
$ run-script.sh
```

OPTION 2
- Run individual Python script to achive certain task independently. But make sure the scripts are run in a right order. It is a good reference looking at master script "run-script.sh" content.
```python
For example, sites must be created in following order
$ python3 create-override-obj.py
$ python3 add-override-obj-network.py
```

## Limitations

- fireREST SDK doesn't support static route creation over Virtual Router, hence native API call is the only option.
- FMC API doesn't support BGP creation (e.g. request POST & PUT)


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License.
