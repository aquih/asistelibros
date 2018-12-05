# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    criva = fields.Char('Constancia de retención de IVA')
    valor_constancia = fields.Float('Valor de constancia')
    cadi = fields.Char('CADI')
    fauca = fields.Char('FAUCA')
    dua = fields.Char('DUA')
