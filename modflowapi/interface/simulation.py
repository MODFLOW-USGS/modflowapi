from .model import Model


class Simulation:
    """
    Simulation object that holds a modflow simulation info and loads supported
    models.

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object

    """
    def __init__(self, mf6):
        self.mf6 = mf6
        self._models = {}
        self._solutions = {}
        self._set_models()
        self._set_solutions()

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
        s += f"Number of models: {len(self._models)}"
        for name, obj in self._models.items():
            s += f"{name} : {type(obj)}"
        return s

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
        return [v for _, v in self._models.items()]

    @property
    def kper(self):
        return self.mf6.get_value("TDIS/KPER")[0] - 1

    @property
    def kstp(self):
        return self.mf6.get_value("TDIS/KSTP")[0] - 1

    def _set_models(self):
        """
        Method to load model data for all models within a simulation

        """
        variables = self.mf6.get_input_var_names()
        model_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 3:
                name = t[0]
                if name.startswith("SLN"):
                    continue
                if f"{name.upper()}/ID" not in variables:
                    continue

                if name not in model_names:
                    model_names.append(name)

        for name in model_names:
            self._models[name.lower()] = Model(self.mf6, name)

    def _set_solutions(self):
        """
        Method to set a dictionary of the solution id and maxiter
        """
        variables = self.mf6.get_input_var_names()
        model_names = [name.upper() for name in self.model_names]
        solution_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 2:
                if t[0] in model_names or t[0] == "TDIS":
                    continue
                if f"{t[0]}/ID" not in variables:
                    continue

                solution_names.append(t[0])

        solution_names = list(set(solution_names))
        solution_dict = {}
        for name in solution_names:
            sid = self.mf6.get_value(f"{name}/ID")[0]
            maxiter = self.mf6.get_value(f"{name}/MXITER")[0]
            solution_dict[sid] = maxiter

        self._solutions = solution_dict

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
            raise TypeError(f"A string or int must be supplied to get model")
