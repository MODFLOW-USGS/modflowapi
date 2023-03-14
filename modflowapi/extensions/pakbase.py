import numpy as np

from .data import AdvancedInput, ArrayInput, ListInput, ScalarInput

# Note: HFB variables are not accessible in the memory manager 10/7/2022
pkgvars = {
    "dis": ["top", "bot", "area", "idomain"],
    "chd": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("head",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "drn": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "elev",
                "cond",
            ),
        ),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "evt": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "surface",
                "rate",
                "depth",
            ),
        ),
        # "pxdp:NSEG", "petm:NSEG"
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ghb": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "bhead",
                "cond",
            ),
        ),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ic": ["strt"],
    "npf": ["k11", "k22", "k33", "angle1", "angle2", "angle3", "icelltype"],
    "rch": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("recharge",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "sto": ["iconvert", "ss", "sy"],
    "wel": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("flux",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    # gwt model
    "adv": ["diffc", "alh", "alv", "ath1", "ath2", "atv"],
    "cnc": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("conc",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ist": [
        "cim",
        "thtaim",
        "zetaim",
        "decay",
        "decay_sorbed",
        "bulk_density",
        "distcoef",
    ],
    "mst": ["porosity", "decay", "decay_sorbed", "bulk_density", "distcoef"],
    "src": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("smassrate",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    # exchange model
    "gwf-gwf": ["nexg", "nodem1", "nodem2", "cl1", "cl2", "ihc"],
    "gwt-gwt": ["nexg", "nodem1", "nodem2", "cl1", "cl2", "ihc"],
    # simulation
    "ats": [
        "maxats",
        "iperats",
        "dt0",
        "dtmin",
        "dtmax",
        "dtadj",
        "dtfailadj",
    ],
    "tdis": [
        "nper",
        "itmuni",
        "kper",
        "kstp",
        "delt",
        "pertim",
        "totim,",
        "perlen",
        "nstp",
        "tsmult",
    ],
    # solution package
    "sln": [
        "mxiter",
        "dvclose",
        "gamma",
        "theta",
        "akappa",
        "amomentum",
        "numtrack",
        "btol",
        "breduc",
        "res_lim",
    ],
    "ims": [
        "niterc",
        "dvclose",
        "rclose",
        "relax",
        "ipc",
        "droptol",
        "north",
        "iscl",
        "iord",
    ],
}


class PackageBase:
    """
    Base class for packages within the modflow-6 api


    Parameters
    ----------
    model : ApiModel
        modflowapi ApiModel object
    pkg_type : str
        package type name. ex. 'wel'
    pkg_name : str
        modflow package name. ex. 'wel_0'
    child_type : str
        type of child input package
    sim_package : bool
        flag to indicate this is a simulation level package
    """

    def __init__(self, model, pkg_type, pkg_name, child_type, sim_package):
        self.model = model
        self.pkg_name = pkg_name
        self.pkg_type = pkg_type
        self._child_type = child_type
        self._sim_package = sim_package
        self._rhs = None
        self._hcof = None
        self._bound_vars = []
        self._advanced_var_names = None

        var_addrs = []
        if self._child_type != "advanced":
            for var in pkgvars[self.pkg_type]:
                if isinstance(var, tuple):
                    bound_vars = []
                    for bv in var[-1]:
                        t = bv.split(":")
                        if len(t) == 2:
                            # this is a repeating variable
                            addr = self.model.mf6.get_var_address(
                                t[-1].upper(), self.model.name, self.pkg_name
                            )
                            nrep = self.model.mf6.get_value(addr)[0]
                            if nrep > 1:
                                for rep in range(nrep):
                                    bound_vars.append(f"{t[0]}{rep}")
                            else:
                                bound_vars.append(t[0])
                        else:
                            bound_vars.append(t[0])

                    self._bound_vars = var[-1]
                    var = var[0]

                if sim_package:
                    var_addrs.append(
                        self.model.mf6.get_var_address(
                            var.upper(), self.pkg_name
                        )
                    )
                else:
                    var_addrs.append(
                        self.model.mf6.get_var_address(
                            var.upper(), self.model.name, self.pkg_name
                        )
                    )

        self.var_addrs = var_addrs
        self._variables_adv = AdvancedInput(self)

    @property
    def advanced_vars(self):
        """
        Returns a list of additional "advanced" variables that are
        accessible through the API
        """
        if self._advanced_var_names is None:
            adv_vars = []
            for var_addr in self.model.mf6.get_input_var_names():
                is_advanced = False
                t = var_addr.split("/")
                if not self._sim_package:
                    if t[0] == self.model.name and t[1] == self.pkg_name:
                        is_advanced = self._check_if_advanced_var(t[-1])
                else:
                    if t[0] == self.pkg_name:
                        is_advanced = self._check_if_advanced_var(t[-1])

                if is_advanced:
                    adv_vars.append(t[-1].lower())

            self._advanced_var_names = adv_vars
        return self._advanced_var_names

    def _check_if_advanced_var(self, variable_name):
        """
        Method to check if a variable is an advanced variable

        Parameters
        ----------
        variable_name : str
            variable name to check

        Returns
        -------
            bool
        """
        if variable_name.lower() in self._bound_vars:
            is_advanced = False
        elif self.pkg_type not in pkgvars:
            is_advanced = True
        elif variable_name.lower() in pkgvars[self.pkg_type]:
            is_advanced = False
        else:
            is_advanced = True
        return is_advanced

    def get_advanced_var(self, name):
        """
        Method to get an advanced variable that is not automatically
        accessible through stress period data or as an array name
        """
        name = name.lower()
        if name not in self.advanced_vars:
            raise AssertionError(
                f"{name} is not accessible as an advanced "
                f"variable for this package"
            )

        values = self._variables_adv.get_variable(name)
        if not self._sim_package:
            if (
                values.size == self.model.nodetouser.size
                and self._child_type == "array"
            ):
                array = np.full(self.model.size, np.nan)
                array[self.model.nodetouser] = values
                return array

        return values

    def set_advanced_var(self, name, values):
        """
        Method to set data to an advanced variable

        Parameters
        ----------
        name : str
            parameter name
        values : np.ndarray
            numpy array
        """
        if not self._sim_package:
            if self._child_type == "array" and values.size == self.model.size:
                values = values[self.model.nodetouser]

        self._variables_adv.set_variable(name, values)

    @property
    def rhs(self):
        if not self._sim_package:
            if self._rhs is None:
                var_addr = self.model.mf6.get_var_address(
                    "RHS", self.model.name, self.pkg_name
                )
                if var_addr in self.model.mf6.get_input_var_names():
                    self._rhs = self.model.mf6.get_value_ptr(var_addr)
                else:
                    return

        return np.copy(self._rhs)

    @rhs.setter
    def rhs(self, values):
        if self._rhs is None:
            return

        self._rhs[:] = values[:]

    @property
    def hcof(self):
        if not self._sim_package:
            if self._hcof is None:
                var_addr = self.model.mf6.get_var_address(
                    "HCOF", self.model.name, self.pkg_name
                )
                if var_addr in self.model.mf6.get_input_var_names():
                    self._hcof = self.model.mf6.get_value_ptr(var_addr)
                else:
                    return

        return np.copy(self._hcof)

    @hcof.setter
    def hcof(self, values):
        if self._hcof is None:
            return

        self._hcof[:] = values[:]


class ListPackage(PackageBase):
    """
    Package object for "list based" input packages such as WEL, DRN, RCH

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        flag to indicate this is a simulation level package
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(
            model, pkg_type, pkg_name.upper(), "list", sim_package
        )

        self._variables = ListInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name}"
        return s

    @property
    def nbound(self):
        """
        Returns the "nbound" value for the stress period
        """
        return self._variables._nbound[0]

    @property
    def maxbound(self):
        """
        Returns the "maxbound" value for the stress period
        """
        return self._variables._maxbound[0]

    @property
    def stress_period_data(self):
        """
        Returns a ListInput object of the current stress_period_data
        """
        return self._variables

    @stress_period_data.setter
    def stress_period_data(self, recarray):
        """
        Setter method to update the current stress_period_data
        """
        if isinstance(recarray, np.recarray):
            self._variables.values = recarray
        elif isinstance(recarray, ListInput):
            self._variables.values = recarray.values
        elif recarray is None:
            self._variables.values = recarray
        else:
            raise TypeError(
                f"{type(recarray)} is not a supported stress_period_data type"
            )


class ArrayPackage(PackageBase):
    """
    Package object for "array based" input packages such as NPF, DIS,

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "DIS"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        flag to indicate this is a simulation level package
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(
            model, pkg_type, pkg_name.upper(), "array", sim_package
        )

        self._variables = ArrayInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name} \n"
        s += " Accessible variables include:\n"
        for var_name in self.variable_names:
            s += f" {var_name} \n"
        return s

    def __setattr__(self, item, value):
        """
        Method that enables dynamic variable setting and distributes
        modflow variable storage and updates to the data object class
        """
        if item in (
            "model",
            "pkg_name",
            "pkg_type",
            "var_addrs",
        ):
            super().__setattr__(item, value)

        elif item.startswith("_"):
            super().__setattr__(item, value)

        elif item in self._variables._ptrs:
            self._variables.set_ptr(item, value)

        else:
            raise AttributeError(f"{item}")

    def __getattr__(self, item):
        """
        Method to dynamically get modflow variables by attribute
        """
        if item in self._variables._ptrs:
            return self._variables.get_ptr(item)
        else:
            return super().__getattribute__(item)

    @property
    def variable_names(self):
        """
        Returns a list of valid modflow variable names that the user can access
        """
        return self._variables.variable_names

    def get_array(self, item):
        """
        Method to get an array from modflow

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "k11"

        Returns
        -------
        np.array of modflow data
        """
        return self._variables.get_array(item)

    def set_array(self, item, array):
        """
        Method to update the modflow pointer arrays

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "k11"
        array : np.array
            numpy array

        """
        self._variables.set_array(item, array)


class ScalarPackage(PackageBase):
    """
    Container for advanced data packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(
            model, pkg_type, pkg_name.upper(), "scalar", sim_package
        )

        self._variables = ScalarInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name} \n"
        s += " Accessible variables include:\n"
        for var_name in self.variable_names:
            s += f" {var_name} \n"
        return s

    def __setattr__(self, item, value):
        """
        Method that enables dynamic variable setting and distributes
        modflow variable storage and updates to the data object class
        """
        if item in (
            "model",
            "pkg_name",
            "pkg_type",
            "var_addrs",
        ):
            super().__setattr__(item, value)

        elif item.startswith("_"):
            super().__setattr__(item, value)

        elif item in self._variables._ptrs:
            self._variables.set_value(item, value)

        else:
            raise AttributeError(f"{item}")

    def __getattr__(self, item):
        """
        Method to dynamically get modflow variables by attribute
        """
        if item in self._variables._ptrs:
            return self._variables.get_value(item)
        else:
            return super().__getattribute__(item)

    @property
    def variable_names(self):
        """
        Returns a list of valid modflow variable names that the user can access
        """
        return self._variables.variable_names

    def get_value(self, item):
        """
        Method to get a scalar value from modflow

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "NBOUND"

        Returns
        -------
        np.array of modflow data
        """
        return self._variables.get_value(item)

    def set_value(self, item, value):
        """
        Method to update the modflow pointer arrays

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "k11"
        array : str, int, float
            scalar value

        """
        self._variables.set_value(item, value)


class AdvancedPackage(PackageBase):
    """
    Container for advanced data packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(
            model, pkg_type, pkg_name.upper(), "advanced", sim_package
        )

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name} \n"
        s += " Advanced Package, variables only accessible through\n"
        s += " get_advanced_var() and set_advanced_var() methods"
        return s


class ApiSlnPackage(ScalarPackage):
    """
    Class to acess solution packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, sim, pkg_name):
        from .apimodel import ApiMbase

        super().__init__(sim, "sln", pkg_name, sim_package=True)

        mdl = ApiMbase(
            sim.mf6, pkg_name.upper(), pkg_types={"ims": ScalarPackage}
        )
        imslin = ScalarPackage(mdl, "ims", "IMSLINEAR")
        for key, ptr in imslin._variables._ptrs.items():
            if key in self._variables._ptrs:
                key = f"{imslin.pkg_type}_{key}".lower()
            self._variables._ptrs[key] = ptr


def package_factory(pkg_type, basepackage):
    """
    Method to autogenerate unique package "types" from the base packages:
    ArrayPackage, ListPackage, and AdvancedPackage

    Parameters
    ----------
    pkg_type : str
        package type
    basepackage : ArrayPackage, ListPackage, or AdvancedPackage
        a base package type

    Returns
        Package object : ex. ApiWelPackage
    """

    # hack for now. need a pkg_type variable for robustness
    def __init__(self, obj, model, pkg_type, pkg_name, sim_package=False):
        obj.__init__(self, model, pkg_type, pkg_name, sim_package=sim_package)

    cls_str = "".join(pkg_type.split("-"))
    cls_str = f"{cls_str[0].upper()}{cls_str[1:]}"

    package = type(
        f"Api{cls_str}Package",
        (basepackage,),
        {"__init__": __init__},
    )

    return package
