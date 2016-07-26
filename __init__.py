# This file is part of the sale_payment module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .sale import *
def register():
    Pool.register(
        Sale,
        AddTermForm,
        module='nodux_sale_payment_term_pymes', type_='model')
    Pool.register(
        WizardAddTerm,
        module='nodux_sale_payment_term_pymes', type_='wizard')
