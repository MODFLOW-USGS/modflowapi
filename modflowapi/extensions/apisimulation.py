from .apimodel import ApiModel


class ApiSimulation:
    """
    ApiSimulation object that holds a modflow simulation info and loads supported
    models.

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    models : dict
        dictionary of model_name: modflowapi.extensions.ApiModel objects
    solutions : dict
        dictionary of solution_id: maxiters

    """

    def __init__(self, mf6, models, solutions):
        self.mf6 = mf6
        self._models = models
        self._solutions = solutions
        self._iteration = -1

    def __getattr__(self, item):
        """
        Dynamic method to get models by model name
        """
        if item.lower() in self._models:
            return self.get_model(item)
        else:
            return super().__getattribute__(item)

    def __repr__(self):
        s = self.__doc__
        s += f"Number of models: {len(self._models)}:"
        for name, obj in self._models.items():
            s += f"\n\t{name} : {type(obj)}"
        return s

    @property
    def allow_convergence(self):
        """
        Returns a boolean value that specifies if the user will allow the
        model to converge. Default is True
        """
        for model in self.models:
            if not model.allow_convergence:
                return False
        return True

    @allow_convergence.setter
    def allow_convergence(self, value):
        """
        Method to set the allow_convergence flag

        Parameters
        ----------
        value : bool
            if True (default) model converges if solution converges, if False
            model will continue solving after solution converges.
        """
        for model in self.models:
            model.allow_convergence = value

    @property
    def subcomponent_count(self):
        """
        Returns the number of subcomponents in the simulation
        """
        return self.mf6.get_subcomponent_count()

    @property
    def solutions(self):
        """
        Returns a dictionary of solution_id : maxiter
        """
        return self._solutions

    @property
    def model_names(self):
        """
        Returns a list of model names
        """
        return list(self._models.keys())

    @property
    def models(self):
        """
        Returns a list of ApiModel objects associated with the simulation
        """
        return [v for _, v in self._models.items()]

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, value):
        if isinstance(value, int):
            self._iteration = value

    @property
    def kper(self):
        """
        Returns the current stress period
        """
        var_addr = self.mf6.get_var_address("KPER", "TDIS")
        return self.mf6.get_value(var_addr)[0] - 1  # "TDIS/KPER"

    @property
    def kstp(self):
        """
        Returns the current time step
        """
        var_addr = self.mf6.get_var_address("KSTP", "TDIS")
        return self.mf6.get_value(var_addr)[0] - 1

    @property
    def nstp(self):
        """
        Returns the total number of time steps
        """
        var_addr = self.mf6.get_var_address("NSTP", "TDIS")
        return self.mf6.get_value(var_addr)[0]

    @property
    def nper(self):
        """
        Returns the total number of stress periods
        """
        var_addr = self.mf6.get_var_address("NPER", "TDIS")
        return self.mf6.get_value(var_addr)[0]

    def get_model(self, model_id):
        """
        Method to get a model from the simulation object by model name or
        subcomponent id

        Parameters
        ----------
        model_id : str, int
            model name (ex. "GWF_1") or subcomponent id (ex. 1)
        """
        if isinstance(model_id, int):
            for model in self._models:
                if model_id == model.subcomponent_id:
                    return model
            raise KeyError(f"No model found with subcomponent id {model_id}")

        elif isinstance(model_id, str):
            model_id = model_id.lower()
            if model_id in self._models:
                return self._models[model_id]
            raise KeyError(f"Model name {model_id} is invalid")

        else:
            raise TypeError("A string or int must be supplied to get model")

    @staticmethod
    def load(mf6):
        """
        Method to load a modflowapi instance into the ApiSimulation extensions

        Parameters
        ----------
        mf6 : ModflowApi
            initialized ModflowApi object
        """
        variables = mf6.get_input_var_names()
        model_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 3:
                name = t[0]
                id_var_addr = mf6.get_var_address("ID", name)
                if name.startswith("SLN"):
                    continue
                if id_var_addr not in variables:
                    continue

                if name not in model_names:
                    model_names.append(name)

        models = {}
        for name in model_names:
            models[name.lower()] = ApiModel(mf6, name)

        solution_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 2:
                name = t[0]
                id_var_addr = mf6.get_var_address("ID", name)
                if name.lower() in models or name == "TDIS":
                    continue
                if id_var_addr not in variables:
                    continue

                solution_names.append(t[0])

        solution_names = list(set(solution_names))
        solution_dict = {}
        for name in solution_names:
            sid_var_addr = mf6.get_var_address("ID", name)
            sid = mf6.get_value(sid_var_addr)[0]
            maxiter_var_addr = mf6.get_var_address("MXITER", name)
            maxiter = mf6.get_value(maxiter_var_addr)[0]
            solution_dict[sid] = maxiter

        solutions = solution_dict

        return ApiSimulation(mf6, models, solutions)