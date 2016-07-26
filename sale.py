# This file is part of the sale_payment module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
#! -*- coding: utf8 -*-
from decimal import Decimal
from trytond.model import ModelView, fields, ModelSQL
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Bool, Eval, Not
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button, StateAction
from trytond import backend
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from trytond.report import Report

__all__ = [ 'Sale', 'AddTermForm', 'WizardAddTerm']
__metaclass__ = PoolMeta
_ZERO = Decimal('0.0')
PRODUCT_TYPES = ['goods']


class Sale():
    __name__ = 'sale.sale'

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        cls._buttons.update({
                'wizard_add_term': {
                    'invisible': ((Eval('state') != 'draft') | (Eval('invoice_state') != 'none')),
                    'readonly': ~Eval('lines', [0])
                    },

                'wizard_sale_payment': {
                    'readonly': ~Eval('lines', [0]),
                    'invisible': Eval('invoice_state') != 'none'
                    },
                })

    @classmethod
    @ModelView.button_action('nodux_sale_payment_term_pymes.wizard_add_term')
    def wizard_add_term(cls, sales):
        pass

class AddTermForm(ModelView):
    'Add Term Form'
    __name__ = 'nodux_sale_payment_term_pymes.add_payment_term_form'

    dias = fields.Integer("Numero de dias", help=u"Ingrese el numero de dias en los que se realizara el pago")

    @staticmethod
    def default_dias_pagos():
        return int(0)

class WizardAddTerm(Wizard):
    'Wizard Add Term'
    __name__ = 'nodux_sale_payment_term_pymes.add_term'
    start = StateView('nodux_sale_payment_term_pymes.add_payment_term_form',
        'nodux_sale_payment_term_pymes.add_term_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'add_', 'tryton-ok'),
        ])
    add_ = StateTransition()

    def default_start(self, fields):
        default = {}
        pool = Pool()
        Sale = pool.get('sale.sale')
        sale = Sale(Transaction().context['active_id'])
        nombre = sale.party.name
        nombre = nombre.lower()
        if nombre == 'consumidor final':
            self.raise_user_error("No puede aplicar credito a cliente: CONSUMIDOR FINAL")
        elif sale.party.name == '9999999999999':
            self.raise_user_error("No puede aplicar credito a cliente: CONSUMIDOR FINAL")
        else:
            default['dias'] = 0
            return default

    def transition_add_(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        active_id = Transaction().context.get('active_id', False)
        sale = Sale(active_id)
        Term = Pool().get('account.invoice.payment_term')
        term = Term()
        PaymentTermLine = Pool().get('account.invoice.payment_term.line')

        if self.start.dias > 0 :
            terms = Term.search([('name','=', 'CREDITO')])
            if terms:
                for t in terms:
                    term = t
                    eliminar =  term.id
                    cursor = Transaction().cursor
                    cursor.execute('DELETE FROM account_invoice_payment_term_line WHERE payment = %s' % eliminar)
            else:
                term.name = 'CREDITO'
            dias = self.start.dias
            lines= []
            term_line = PaymentTermLine(payment=term.id, type='remainder', days=dias, divisor=Decimal(0.0))
            lines.append(term_line)
            term.lines = lines
            term.save()

        sale.payment_term = term
        sale.save()

        return 'end'
