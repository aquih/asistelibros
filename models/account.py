# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
import logging

class AccountJournal(models.Model):
    _inherit = "account.journal"

    codigo_establecimiento = fields.Char('Código establecimiento')
