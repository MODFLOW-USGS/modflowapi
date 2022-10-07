from .pakbase import ListPackage, ArrayPackage
import numpy as np


disvars = {
    "dis": {
        "vars": [
            "nodes",
            "nodesuser",
            "nlay",
            "nrow",
            "ncol",
        ],
        "shape": [
            "nlay",
            "nrow",
            "ncol"
        ]
    },
    "disv": [

    ],
    "disu": [

    ]
}


class Model:
    """
    Container to hold MODFLOW model information and load supported packages

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    name : str
        modflow model name. ex. "GWF_1"

    """
    def __init__(self, mf6, name):
        self.mf6 = mf6
        self.name = name
        self._id = mf6.get_value(f"{name}/ID")[0]
        self._solnid = mf6.get_value(f"{name}/IDSOLN")[0]
        grid_type = mf6.get_grid_type(self._id)
        # todo: need a better way to determine dis_name
        if grid_type == "rectilinear":
            self.dis_type = "dis"
            self.dis_name = "DIS"
        elif grid_type == "vertex":
            self.dis_type = "disv"
            self.dis_name = "DISV"
        else:
            self.grid_type = "disu"
            self.dis_name = "DISU"

        self.pkg_types = {
            "dis": ArrayPackage,
            "chd": ListPackage,
            "drn": ListPackage,
            "evt": ListPackage,
            "ghb": ListPackage,
            "ic": ArrayPackage,
            "npf": ArrayPackage,
            "rch": ListPackage,
            "sto": ArrayPackage,
            "wel": ListPackage
        }
        self.package_dict = {}
        self._shape = None
        self._size = None
        self._pkg_names = None
        self._pak_type = None
        self._nodetouser = None
        self._usertonode = None
        self._set_package_names()
        self._create_package_list()

    def __repr__(self):
        s = f"{self.name}, "
        shape = self.shape
        if self.dis_type == "dis":
            s += f"{shape[0]} Layer, {shape[1]} Row, {shape[2]}, " \
                 f"Column model\n"
        elif self.dis_type == "disv":
            s += f"{shape[0]} Layer, {shape[1]} Nodes per layer model\n"
        else:
            s += f"{shape[0]} Node model\n"

        s += "Packages accessible include: \n"
        for name in self.package_names:
            s += f" {name} \n"

        return s

    def __getattr__(self, item):
        """
        Method for getting packages either by package name or by
        package type name

        """
        if item in self.package_dict:
            return self.package_dict[item]
        else:
            pkg_list = []
            for pkg_name, package in self.package_dict.items():
                if item == package.pkg_type:
                    pkg_list.append(package)

            if len(pkg_list) == 0:
                return super().__getattribute__(item)
            elif len(pkg_list) == 1:
                return pkg_list[0]
            else:
                return pkg_list

    @property
    def kper(self):
        return self.mf6.get_value("TDIS/KPER")[0] - 1

    @property
    def kstp(self):
        return self.mf6.get_value("TDIS/KSTP")[0] - 1

    @property
    def subcomponent_id(self):
        """
        Returns the model subcomponent id
        """
        return self._id

    @property
    def solution_id(self):
        """
        Returns the model solution id
        """
        return self._solnid

    @property
    def package_list(self):
        """
        Returns a list of package objects for the model
        """
        return [package for _, package in self.package_dict.items()]

    @property
    def package_names(self):
        """
        Returns a list of package names for the model
        """
        return list(self.package_dict.keys())

    @property
    def shape(self):
        """
        Returns a tuple of the model shape
        """
        if self._shape is None:
            shape_vars = disvars[self.dis_type]["shape"]
            shape = []
            for var in shape_vars:
                var_addr = self.mf6.get_var_address(
                    var.upper(), self.name, self.dis_name
                )
                shape.append(self.mf6.get_value(var_addr)[0])
            self._shape = tuple(shape)
        return self._shape

    @property
    def size(self):
        """
        Returns the number of nodes in the model
        """
        if self._size is None:
            size = 1
            for dim in self.shape:
                size *= dim
            self._size = size
        return self._size

    @property
    def nodetouser(self):
        """
        Returns the "nodeuser" array
        """
        if self._nodetouser is None:
            self._set_node_mapping()
        return self._nodetouser

    @property
    def usertonode(self):
        """
        Returns an array that maps user arrays to modflow's internal nodes
        """
        if self._usertonode is None:
            self._set_node_mapping()
        return self._usertonode

    def _set_node_mapping(self):
        """
        Sets the node mapping arrays NODEUSER and NODEREDUCED for mapping
        user arrays to modflow's internal arrays
        """
        nodes = self.mf6.get_value(f"{self.name}/{self.dis_name}/NODES")
        if nodes[0] == self.size:
            nodeuser = np.arange(nodes).astype(int)
            nodereduced = np.copy(nodeuser)
        else:
            nodeuser = self.mf6.get_value(
                f"{self.name}/{self.dis_name}/NODEUSER"
            ) - 1
            nodereduced = self.mf6.get_value(
                f"{self.name}/{self.dis_name}/NODEREDUCED"
            ) - 1

        self._nodetouser = nodeuser
        self._usertonode = nodereduced

    def _set_package_names(self):
        """
        Method to get/set all package names within the model
        """
        var_addrs = self.mf6.get_input_var_names()
        pak_types = {}
        for addr in self.mf6.get_input_var_names():
            tmp = addr.split("/")
            if addr.endswith("PACKAGE_TYPE") and tmp[0] == self.name:
                pak_types[tmp[1]] = self.mf6.get_value(addr)[0]

        self._pak_type = list(pak_types.values())
        self._pkg_names = list(pak_types.keys())

    def _create_package_list(self):
        """
        Method to load packages and set up the package dict/list variable
        """
        # hack for now. need a pkg_type variable for robustness
        def __init__(self, obj, model, pkg_type, pkg_name):
            obj.__init__(self, model, pkg_type, pkg_name)

        for ix, pkg_name in enumerate(self._pkg_names):
            pkg_type = self._pak_type[ix].lower()
            if pkg_type in self.pkg_types:
                basepackage = self.pkg_types[pkg_type]
                package = type(
                    f"{pkg_type[0].upper()}{pkg_type[1:]}Package",
                    (basepackage,),
                    {"__init__": __init__}
                )
                package = package(basepackage, self, pkg_type, pkg_name)
                self.package_dict[pkg_name.lower()] = package

    def get_package(self, pkg_name) -> ListPackage or ArrayPackage:
        """
        Method to get a package

        Parameters
        ----------
        pkg_name : str
            package name str. Ex. "wel_0"
        """
        pkg_name = pkg_name.lower()
        if pkg_name in self.package_dict:
            return self.package_dict[pkg_name]

        raise KeyError(
            f"{pkg_name} is not a valid package name for this model"
        )
