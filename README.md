# DemandRegio

This project aims at setting up both a database and a python toolkit called `disaggregator` for
- temporal and
- spatial dissagregation

of demands of 
- electricity,
- heat and
- natural gas

of the final energy sectors
- private households,
- commerce, trade & services (CTS) and
- industry.


## Installation

Before we really start, please install the [latest Anaconda package](https://www.anaconda.com/distribution/) and open the **Anaconda Powershell Prompt**.  
For experts: You can also open a bash shell (Linux) or command prompt (Windows), but then make sure that your local environment variable `PATH` points to your anaconda installation directory.

Now, in the root folder of the project create an environment called `demandregio` to work in

```bash
$ conda create --name demandregio --file environment.yml
```

and install all required packages. Then activate the environment

```bash
$ activate demandregio
```

## How to start

Once the environment is activated, you can start a Jupyter Notebook from there

```bash
(demandregio) $ jupyter notebook
```

As soon as the Jupyter Notebook opens in your browser, click on the `01_Introduction_data.ipynb` file to start with a demonstration:

![Jupyter_View][img_01]

[img_01]: img/jupyter_notebook.png "Jupyter Notebook View"

## Results

![Jupyter_View][img_02]

[img_02]: img/spatial_elc_by_household_sizes.png "Year Electricity Consumption of Private Households"

## Acknowledgements

The development of disaggregator was part of the joint [DemandRegio-Project](https://www.ffe.de/en/topics-and-methods/production-and-market/736-harmonization-and-development-of-methods-for-a-spatial-and-temporal-resolution-of-energy-demands-demandregio) which was carried out by

- Forschungszentrum Jülich GmbH (Simon Burges, Bastian Gillessen, Fabian Gotzens)
- Forschungsstelle für Energiewirtschaft e.V. (Tobias Schmid)
- Technical University of Berlin (Stephan Seim, Paul Verwiebe)

## License

Software written by Fabian P. Gotzens, 2019.

disaggregator is released as free software under the [GPLv3](http://www.gnu.org/licenses/gpl-3.0.en.html), see [LICENSE](LICENSE) for further information.