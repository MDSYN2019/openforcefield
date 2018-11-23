#!/usr/bin/env python

# =============================================================================================
# MODULE DOCSTRING
# =============================================================================================

"""
Substances API.

Authors
-------
* John D. Chodera <john.chodera@choderalab.org>
* Levi N. Naden <levi.naden@choderalab.org>
* Simon Boothroyd <simon.boothroyd@choderalab.org>
"""
# =============================================================================================
# GLOBAL IMPORTS
# =============================================================================================


# =============================================================================================
# Component
# =============================================================================================

# TODO: Delete this?
class Component(object):

    def __init__(self, smiles):
        """Create a chemical component.

        Parameters
        ----------
        smiles : str
            SMILES descriptor of the component
        """
        self.smiles = smiles


# =============================================================================================
# SUBSTANCE
# =============================================================================================

class Substance(object):
    """
    A substance, can be a pure chemical, or could be a Mixture.

    This class is not specific enough to be a chemical species all on its own
    """

    def to_tag(self):
        raise NotImplementedError('A Substance is a purely abstract base class.')


# =============================================================================================
# MIXTURE
# =============================================================================================

# TODO: The name is perhaps misleading as a mixture can be pure...
# SystemComposition or just Composition perhaps?
class Mixture(Substance):
    """Defines the components and their amounts in a mixture.

    Examples
    --------

    A neat liquid has only one component:

    >>> liquid = Mixture()
    >>> liquid.add_component('water')

    A binary mixture has two components:

    >>> binary_mixture = Mixture()
    >>> binary_mixture.add_component('water', mole_fraction=0.2)
    >>> binary_mixture.add_component('methanol') # assumed to be rest of mixture if no mole_fraction specified

    A ternary mixture has three components:

    >>> ternary_mixture = Mixture()
    >>> binary_mixture.add_component('ethanol', mole_fraction=0.2)
    >>> binary_mixture.add_component('methanol', mole_fraction=0.2)
    >>> ternary_mixture.add_component('water')

    The infinite dilution of one solute within a solvent or mixture is also specified as a `Mixture`, where the solute
    has is treated as an impurity, and so only 1 atom is added:

    >>> infinite_dilution = Mixture()
    >>> infinite_dilution.add_component('phenol', impurity=True) # infinite dilution
    >>> infinite_dilution.add_component('water')

    """

    class MixtureComponent(Component):
        """Subclass of Component which has mole_fractions and impurity"""
        def __init__(self, smiles, mole_fraction=0.0, impurity=False):

            self.mole_fraction = mole_fraction
            self.impurity = impurity

            super().__init__(smiles)

    def __init__(self):
        """Create a Mixture.
        """
        self._components = list()

    @property
    def total_mole_fraction(self):
        """Compute the total mole fraction.
        """
        return sum([component.mole_fraction for component in self._components])

    @property
    def number_of_components(self):
        return len(self._components)

    @property
    def components(self):
        return self._components

    @property
    def number_of_impurities(self):
        return sum([1 for component in self._components if component.impurity is True])

    def add_component(self, smiles, mole_fraction, impurity=False):
        """Add a component to the mixture.

        Parameters
        ----------
        smiles : str
            SMILES pattern of the component
        mole_fraction : float or None, optional, default=None
            If specified, the mole fraction of this component as a float on the domain [0,1]
            If not specified, this will be the last or only component of the mixture.
        impurity : bool, optional, default=False
            If True, the component represents an impurity (single molecule).
            This is distinct from 0 mole fraction
        """

        mole_fraction, impurity = self._validate_mol_fraction(mole_fraction, impurity)

        component = self.MixtureComponent(smiles, mole_fraction=mole_fraction, impurity=impurity)
        self._components.append(component)

    def get_component(self, smiles: str):
        """Retrieve component by name.

        Parameters
        ----------
        smiles : str
            The smiles of the component to retrieve

        """
        for component in self._components:

            if component.smiles != smiles:
                continue

            return component

        raise Exception("No component with smiles '{0:s}' found.".format(smiles))

    def _validate_mol_fraction(self, mole_fraction, impurity):
        """
        Validates the mole_fraction and impurity, setting the defaults if need be.
        See :func:``add_component`` for parameters.
        """
        if not impurity and mole_fraction is None:
            raise ValueError("Either mole_fraction or impurity must be specified!")
        elif impurity and mole_fraction != 0:
            raise ValueError('Mole fraction must be 0.0 or None for impurities. '
                             'Specified mole fraction of {0:f}'.format(mole_fraction))
        elif mole_fraction is not None and not 0.0 <= mole_fraction <= 1.0:
            raise ValueError('Mole fraction must be positive; specified {0:f}.'.format(mole_fraction))
        if impurity:
            mole_fraction = 0.0
        if mole_fraction is None:
            mole_fraction = 1.0 - self.total_mole_fraction
        if (self.total_mole_fraction + mole_fraction) > 1.0:
            raise ValueError("Total mole fraction would exceed "
                             "unity ({0:f}); specified {1:f}".format(self.total_mole_fraction, mole_fraction))

        return mole_fraction, impurity

    def to_tag(self):

        sorted_tags = [component.smiles + '{' + str(component.mole_fraction) + '}' for component in self._components]
        sorted_tags.sort()

        return "|".join(sorted_tags)
