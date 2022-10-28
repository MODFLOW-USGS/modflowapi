import numpy as np

from .data  import ListInput, ArrayInput, AdvancedInput


# Note: HFB variables are not accessible in the memory manager 10/7/2022
pkgvars = {
    "dis": [
        "top",
        "bot",
        "area",
        "idomain"
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
        ("bound", ("surface", "rate", "depth"))
        # "pxdp:NSEG", "petm:NSEG"
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
        ("bound", ("recharge",)),
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
        ("bound", ('flux',)),
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
    child_type : str
        type of child input package

    """
    def __init__(self, model, pkg_type, pkg_name, child_type):
        self.model = model
        self.pkg_name = pkg_name
        self.pkg_type = pkg_type
        self._child_type = child_type
        self._rhs = None
        self._hcof = None
        self._bound_vars = None
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
                t = var_addr.split("/")
                if t[0] == self.model.name and t[1] == self.pkg_name:
                    if t[-1].lower() in self._bound_vars:
                        continue
                    elif t[-1].lower() in pkgvars[self.pkg_type]:
                        continue
                    else:
                        adv_vars.append(t[-1].lower())
            self._advanced_var_names = adv_vars
        return self._advanced_var_names

    def get_advanced_var(self, name):
        """
        Method to get an advanced variable that is not automatically
        accessible through stress period data or as an array name
        """
        if name not in self.advanced_vars:
            raise AssertionError(
                f"{name} is not accessible as an advanced "
                f"variable for this package"
            )

        values = self._variables_adv.get_variable(name)
        if values.size == self.model.nodetouser.size \
                and self._child_type == "array":
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
        if self._child_type == "array" and values.size == self.model.size:
            values = values[self.model.nodetouser]

        self._variables_adv.set_variable(name, values)

    @property
    def rhs(self):
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

        self._rhs = values

    @property
    def hcof(self):
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

        self.__hcof = values


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
        super().__init__(model, pkg_type, pkg_name.upper(), 'list')

        self._variables = ListInput(self)

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name}"
        return s

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
        else:
            raise TypeError(
                f"{type(recarray)} is not a supported stress_period_data type"
            )


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
        super().__init__(model, pkg_type, pkg_name.upper(), 'array')

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
        ):
            super().__setattr__(item, value)

        elif item.startswith("_"):
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


class AdvancedPackage(PackageBase):
    """
    Container for advanced data packages

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
        super().__init__(model, pkg_type, pkg_name.upper(), "advanced")

