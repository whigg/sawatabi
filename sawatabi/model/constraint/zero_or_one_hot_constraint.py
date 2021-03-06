# Copyright 2021 Kotaro Terada
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sawatabi
import sawatabi.constants as constants
from sawatabi.model.constraint.abstract_constraint import AbstractConstraint

"""
Zero-or-One-hot Constraint:
    Note that this constraint is equivalent to 0.5-hot constraint.
"""


class ZeroOrOneHotConstraint(AbstractConstraint):
    def __init__(self, variables=None, label=constants.DEFAULT_LABEL_0_OR_1_HOT, strength=1.0):
        super().__init__(label=label, strength=strength)
        self._constraint_class = self.__class__.__name__

        # Avoid duplicate variable, so we use set() for variables
        if variables is None:
            self._variables = set()
        else:
            self._variables = self._check_variables_and_to_set(variables)

    def add_variable(self, variables):
        variables_set = self._check_variables_and_to_set(variables)
        self._variables = self._variables.union(variables_set)

    def remove_variable(self, variables):
        variables_set = self._check_variables_and_to_set(variables)
        for v in variables_set:
            if v not in self._variables:
                raise ValueError(f"Variable '{v}' does not exist in the constraint variables.")
        self._variables = self._variables.difference(variables_set)

    def get_variables(self):
        return self._variables

    def to_model(self):
        model = sawatabi.model.LogicalModel(mtype="qubo")

        # Zero-or-One-hot constraint:
        #   E = \sum{ x_i } * ( \sum{ x_i } - 1 )
        for var in self._variables:
            for adj in self._variables:
                if var.label < adj.label:
                    coeff = -2.0 * self._strength
                    model.add_interaction((var, adj), name=f"{var.label}*{adj.label} ({self._label})", coefficient=coeff)

        return model

    ################################
    # Built-in functions
    ################################

    def __eq__(self, other):
        return (
            isinstance(other, ZeroOrOneHotConstraint)
            and (self._constraint_class == other._constraint_class)
            and (self._variables == other._variables)
            and (self._label == other._label)
            and (self._strength == other._strength)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__str__()})"

    def __str__(self):
        data = {
            "constraint_class": self._constraint_class,
            "variables": self._variables,
            "label": self._label,
            "strength": self._strength,
        }
        return str(data)
