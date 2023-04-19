# modflowapi

`modflowapi` is an extension to [xmipy](https://pypi.org/project/xmipy/) for the MODFLOW API.

The `modflowapi` can be used to access functionality in the eXtended Model Interface (XMI) wrapper (XmiWrapper) 
and additional functionality specific to the MODFLOW API. Currently it is a joint development of the USGS and Deltares.

Use of modflowapi and modflowapi extensions can be found in the [Quickstart](examples/notebooks/Quickstart.ipynb) and the [Extensions](examples/notebooks/MODFLOW-API_extensions_objects.ipynb) Notebooks. An example of using the MODFLOW API to monitor heads during a simulation can be found in the [Head Monitor Example](examples/notebooks/Head_Monitor_Example.ipynb) Notebook. 


`modflowapi` can be installed by running

```
pip install modflowapi
```

or

```
conda install -c conda-forge modflowapi
```

### Citation

Hughes, Joseph D., Russcher, M. J., Langevin, C. D., Morway, E. D. and McDonald, R. R., 2022, The MODFLOW Application Programming Interface for simulationcontrol and software interoperability: Environmental Modelling & Software, v. 148, p. 105257, [doi:10.1016/j.envsoft.2021.105257](https://doi.org/10.1016/j.envsoft.2021.105257).
