import numpy as np


class ListInput:
    """
    Data object for storing pointers and working with list based input data

    Parameters
    ----------
    parent : ListPackage
        modflowapi ListPackage object
    var_addrs : list, None
        optional list of variable addresses
    mf6 : ModflowApi, None
        optional ModflowApi object
    """
    def __init__(self, parent, var_addrs=None, mf6=None):
        self.parent = parent
        if self.parent is not None:
            self.var_addrs = self.parent.var_addrs
            self.mf6 = self.parent.model.mf6
        else:
            if var_addrs is None or mf6 is None:
                raise AssertionError(
                    "var_addrs and mf6 must be supplied if parent is None"
                )
            self.var_addrs = var_addrs
            self.mf6 = mf6

        self._ptrs = {}
        self._nodevars = ('nodelist',)
        self._boundvars = ('bound', )
        self._maxbound = [0, ]
        self._nbound = [0, ]
        self._dtype = []
        self._reduced_to_var_addr = {}
        self._set_stress_period_data()

    def _set_stress_period_data(self):
        """
        Method to set stress period data variable pointers to the _ptrs
        dictionary

        """
        for var_addr in self.var_addrs:
            values = self.mf6.get_value_ptr(var_addr)
            reduced = var_addr.split("/")[-1].lower()
            if reduced in ("maxbound", "nbound"):
                setattr(self, f"_{reduced}", values)
                # self._maxbound = self.mf6.get_value_ptr(var_addr)
            else:
                self._ptrs[reduced] = values
                self._reduced_to_var_addr[reduced] = var_addr
                if reduced in self._boundvars:
                    for name in self.parent._bound_vars:
                        typ_str = values.dtype.str
                        dtype = (name, typ_str)
                        self._dtype.append(dtype)
                else:
                    typ_str = values.dtype.str
                    dtype = (reduced, typ_str)
                    self._dtype.append(dtype)

    def _ptr_to_recarray(self):
        """
        Method to get a recarray of stress period data from modflow pointers

        Returns
        -------
            np.recarray
        """
        if self._nbound[0] == 0:
            return
        recarray = np.recarray((self._nbound[0],), self._dtype)
        for name, ptr in self._ptrs.items():
            values = np.copy(ptr)
            if name in self._boundvars:
                for ix, nm in enumerate(self.parent._bound_vars):
                    recarray[nm][0:self._nbound[0]] = values[:, ix]
            else:
                values = values.ravel()
                if name in self._nodevars:
                    values -= 1
                    values = self.parent.model.nodetouser[values]

                recarray[name][0:self._nbound[0]] = values

        return recarray

    def _recarray_to_ptr(self, recarray):
        """
        Method to update stress period information pointers from user supplied
        data

        Parameters
        ----------
        recarray : np.recarray
            numpy recarray of stress period data

        """
        resize = False
        if len(recarray) != self._nbound:
            resize = True
            self._nbound[0] = len(recarray)
            if len(recarray) > self._maxbound[0]:
                self._maxbound[0] = len(recarray)

        for name in recarray.dtype.names:
            if name in self._nodevars:
                recarray[name] = self.parent.model.usertonode[recarray[name]] + 1

            # todo: adjust this
            if name in self.parent._bound_vars:
                idx = self.parent._bound_vars.index(name)
                bname = "bound"  # ? this will probably need to change
                if resize:
                    # todo: resize will need to be updated at some point!
                    dtype = self._ptrs[bname].dtype
                    x = np.zeros(
                        (len(recarray), self._ptrs[bname].shape[1]), dtype=dtype
                    )
                    x[:, idx] = recarray[name]

                    self.mf6.set_value(self._reduced_to_var_addr[bname], x)
                else:
                    self._ptrs[bname][:, idx] = recarray[name]
            else:
                if resize:
                    x = recarray[name].ravel()
                    self.mf6.set_value(self._reduced_to_var_addr[name], x)
                else:
                    self._ptrs[name][:] = recarray[name].ravel()

    @property
    def stress_period_data(self):
        """
        Returns a np.recarray of the current stress_period_data
        """
        return self._ptr_to_recarray()

    @stress_period_data.setter
    def stress_period_data(self, recarray):
        """
        Setter method to update the current stress_period_data
        """
        self._recarray_to_ptr(recarray)


class ArrayInput:
    """
    Data object for storing pointers and working with array based input data

    Parameters
    ----------
    parent : ArrayPackage
        modflowapi ArrayPackage object
    var_addrs : list, None
        optional list of variable addresses
    mf6 : ModflowApi, None
        optional ModflowApi object
    """
    def __init__(self, parent, var_addrs=None, mf6=None):
        self._ptrs = {}
        self.parent = parent
        # change this to a parent package.mapping
        self._mapping = None

        if self.parent is not None:
            self.var_addrs = self.parent.var_addrs
            self.mf6 = self.parent.model.mf6
        else:
            if var_addrs is None or mf6 is None:
                raise AssertionError(
                    "var_addrs and mf6 must be supplied if parent is None"
                )
            self.var_addrs = var_addrs
            self.mf6 = mf6

        self._maxbound = [0, ]
        self._nbound = [0, ]
        self._reduced_to_var_addr = {}
        self._set_arrays()

    def _set_arrays(self):
        """
        Method to modflow variable pointers to the _ptrs dictionary
        """
        for var_addr in self.var_addrs:
            values = self.mf6.get_value_ptr(var_addr)
            reduced = var_addr.split("/")[-1].lower()
            self._ptrs[reduced] = values
            self._reduced_to_var_addr[reduced] = var_addr

    def __getattr__(self, item):
        """
        Dynamic method to get modflow varaibles as an attribute
        """
        if item in self._ptrs:
            return self.get_array(item)
        else:
            return super(ArrayInput).__getattribute__(item)

    def __setattr__(self, item, value):
        """
        Dynamic method that allows users to set modflow variables to the
        _ptr dict
        """
        if item in (
            "parent",
            "var_addrs",
            "_mapping",
            "_ptrs",
            "mf6",
            "_maxbound",
            "_nbound",
            "_reduced_to_var_addr"

        ):
            super().__setattr__(item, value)

        elif item in self._ptrs:
            self.set_array(item, value)
        else:
            raise AttributeError(f"{item} is not a vaild attribute")

    @property
    def variable_names(self):
        """
        Returns a list of valid array names that can be accessed by the user
        """
        return list(sorted(self._ptrs.keys()))

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
        if item in self._ptrs:
            value = np.ones((self.parent.model.size,)) * np.nan
            value[self.parent.model.nodetouser] = self._ptrs[item]
            return value.reshape(self.parent.model.shape)
        else:
            raise KeyError(f"{item} is not accessible in this package")

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
        if item in self._ptrs:
            if not isinstance(array, np.ndarray):
                raise TypeError()
            if array.size != self.parent.model.size:
                raise ValueError(
                    f"{item} size {array.size} is not equal to "
                    f"modflow variable size {self.parent.model.size}"
                )
            array = array.ravel()
            array = array[self.parent.model.nodetouser]
            self._ptrs[item][:] = array
        else:
            raise KeyError(
                f"{item} is not a valid variable name for this package"
            )
