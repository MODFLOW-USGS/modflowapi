from .data  import ListInput, ArrayInput


# Note: HFB variables are not accessible in the memory manager 10/7/2022
pkgvars = {
    "dis": [
        "top",
        "bot",
    ],
    "chd": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("head",))
    ],
    "drn": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("elev", "cond"))
    ],
    "evt": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("surface", "rate", "depth"))  # pxdp:NSEG, petm:NSEG
    ],
    "ghb": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("bhead", "cond"))
    ],
    "ic": [
        "strt"
    ],
    "npf": [
        "k11",
        "k22",
        "k33",
        "angle1",
        "angle2",
        "angle3",
        "icelltype"
    ],
    "rch": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("recharge",))
    ],
    "sto": [
        "iconvert",
        "ss",
        "sy"
    ],
    # "mvr": [
    #     "id1",
    #     "id2",
    #     "value"
    # ],
    "wel": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ['flux',]),
    ],
}


class PackageBase:
    """
    Base class for packages within the modflow-6 api


    Parameters
    ----------
    model : Model
        modflowapi Model object
    pkg_type : str
        package type name. ex. 'wel'
    pkg_name : str
        modflow package name. ex. 'wel_0'

    """
    def __init__(self, model, pkg_type, pkg_name):
        self.model = model
        self.pkg_name = pkg_name
        self.pkg_type = pkg_type
        self._bound_vars = None

        var_addrs = []
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

            var_addrs.append(
                self.model.mf6.get_var_address(
                    var.upper(), self.model.name, self.pkg_name
                )
            )

        self.var_addrs = var_addrs


class ListPackage(PackageBase):
    """
    Package object for "list based" input packages such as WEL, DRN, RCH

    Parameters
    ----------
    model : Model
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    """
    def __init__(self, model, pkg_type, pkg_name):
        super().__init__(model, pkg_type, pkg_name.upper())

        self._variables = ListInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name}"
        return s

    @property
    def stress_period_data(self):
        """
        Returns a np.recarray of the current stress_period_data
        """
        return self._variables.stress_period_data

    @stress_period_data.setter
    def stress_period_data(self, recarray):
        """
        Setter method to update the current stress_period_data
        """
        self._variables.stress_period_data = recarray


class ArrayPackage(PackageBase):
    """
    Package object for "array based" input packages such as NPF, DIS, RCHA

    Parameters
    ----------
    model : Model
        modflowapi model object
    pkg_type : str
        package type. Ex. "RCH"
    pkg_name : str
        package name (in the mf6 variables)
    """
    def __init__(self, model, pkg_type, pkg_name):
        super().__init__(model, pkg_type, pkg_name.upper())

        self._variables = ArrayInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name} \n"
        s += f" Accessible variables include:\n"
        for var_name in self.variable_names:
            s += f" {var_name} \n"
        return s

    def __setattr__(self, item, value):
        """
        Method that enables dynamic variable setting and distributes
        modflow variable storage and updates to the data object class
        """
        if item in (
                'model',
                "pkg_name",
                "pkg_type",
                "var_addrs",
                "_variables",
                "_bound_vars"
        ):
            super().__setattr__(item, value)

        elif item in self._variables._ptrs:
            self._variables.set_array(item, value)

        else:
            raise AttributeError(f"{item}")

    def __getattr__(self, item):
        """
        Method to dynamically get modflow variables by attribute
        """
        if item in self._variables._ptrs:
            return self._variables.get_array(item)
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
