# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare #, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    fauca = fields.Char('FAUCA')
    dua = fields.Char('DUA')
    cadi = fields.Char('CADI')
    cexe = fields.Char('CEXE')
    criva = fields.Char('CRIVA')
    valor_constancia = fields.Float('Valor de constancia')
