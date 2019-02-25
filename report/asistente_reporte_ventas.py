# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
from datetime import datetime
import time
import xlwt
import base64
import io
import logging

class AsistenteReporteVentas(models.TransientModel):
    _inherit = 'l10n_gt_extra.asistente_reporte_ventas'

    def print_report_excel_asistelibros(self):
        for w in self:
            result = []
            dict = {}
            diarios_id = [x.id for x in w.diarios_id]
            dict['fecha_hasta'] = w['fecha_hasta']
            dict['fecha_desde'] = w['fecha_desde']

            facturas_id = self.env['account.invoice'].search([  ['state','in',['open','cancel','paid']]  ,['date_invoice', '>=',  w.fecha_desde ], ['date_invoice', '<=',  w.fecha_hasta ],['journal_id','in',diarios_id]])

            for f in facturas_id:
                doc_criva = f.criva
                criva = f.valor_constancia

                local = True
                total_quetzales = 0
                total_lineas_servicio = 0
                total_lineas_bien = 0

                if f.partner_id.country_id and f.partner_id.country_id.id != 91:
                    local = False

                if f.currency_id.id == f.company_id.currency_id.id:
                    total_quetzales = abs(f.amount_total)
                else:
                    if f.move_id:
                        for l in f.move_id.line_id:
                            if l.account_id.id == f.account_id.id:
                                total_quetzales += l.debit - l.credit
                    total_quetzales = abs(total_quetzales)


                for l in f.invoice_line_ids:
                    if f.tipo_gasto == 'servicio':
                        total_lineas_servicio += l.price_unit*l.quantity*(100-l.discount)/100
                    else:
                        total_lineas_bien += l.price_unit*l.quantity*(100-l.discount)/100

                iva = 0
                for i in f.invoice_line_ids:
                    if i.id == w.impuesto_id.id:
                        iva += i.amount
                if f.amount_total*iva > 0:
                    iva = total_quetzales/f.amount_total*iva

                r = [
                    f.date_invoice,
                    '1', # Establecimiento
                    'V' # Compra/Venta
                ]

                # Documento
                if f.type == 'out_invoice':
                    r.append('FC')
                else:
                    r.append('NC')

                # Serie y numero
                if f.number:
                    r.append(f.number[0])
                    r.append(f.number[1:])
                else:
                    r.append(f.internal_number[0])
                    r.append(f.internal_number[1:])

                # Fecha
                r.append(datetime.strptime(f.date_invoice,'%Y-%m-%d').strftime('%d/%m/%Y'))

                # NIT
                if f.state in ['cancel']:
                    r.append('0')
                elif f.partner_id.vat:
                    r.append(f.partner_id.vat.replace('-','').replace('/',''))
                else:
                    r.append('0')

                # Nombre
                r.append(f.partner_id.name.replace(',',''))

                # Local o exportacion
                if local:
                    r.append('L')
                else:
                    r.append('E')

                # Bien o servicio de exportacion
                if not local:
                    if f.tipo_gasto in ['compra','importacion','combustible','mixto']:
                        r.append('BIEN')
                    else:
                        r.append('SERVICIO')
                else:
                    r.append('')

                # Emitido o anulado
                if f.state in ['open','paid']:
                    r.append('E')
                else:
                    r.append('A')

                # Orden cedula
                r.append('')

                # Registro cedula
                r.append('')

                # FAUCA o DUA y valor
                if not local:
                    if f.fauca:
                        r.append('FAUCA')
                        r.append(f.fauca)
                    elif f.dua:
                        r.append('DUA')
                        r.append(f.dua)
                    else:
                        r.append('')
                        r.append('')
                else:
                    r.append('')
                    r.append('')

                # Valor bien local
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor bien exportacion
                if f.state in ['cancel']:
                    r.append('')
                else:
                    r.append('0')

                # Valor servicio local
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Valor servicio exportacion
                if f.state in ['cancel']:
                    r.append('')
                else:
                    r.append('0')

                # Valor exento bien local
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor exento bien exportacion
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if not local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor exento servicio local
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Valor exento servicio exportacion
                if f.state in ['cancel']:
                    r.append('')
                else:
                    if not local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Tipo, numero y valor de constancia
                if f.state in ['cancel']:
                    r.append('')
                    r.append('')
                    r.append('')
                else:
                    if criva != 0:
                        r.append('CRIVA')
                        r.append(doc_criva)
                        r.append('%.2f' % criva)
                    else:
                        r.append('')
                        r.append('')
                        r.append('')

                # Valor bien pequeño local
                r.append('')

                # Valor servicios pequeño local
                r.append('')

                # Valor bien pequeño exportacion
                r.append('')

                # Valor servicios pequeño exportacion
                r.append('')

                # IVA
                if f.state in ['cancel']:
                    r.append('')
                else:
                    r.append('%.2f' % 0)

                # Total
                if f.state in ['cancel']:
                    r.append('%.2f' % 0)
                else:
                    if f.amount_total*(total_lineas_bien+total_lineas_servicio) > 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*(total_lineas_bien+total_lineas_servicio)))
                    else:
                        r.append('%.2f' % 0)

                result.append(r)

            texto = ""
            for l in sorted(result, key=lambda x: x[1]+'-'+x[3]+'-'+x[0]+'-'+x[5]):
                l.pop(0)
                if len(l) < 30:
                    logging.warn(l)
                texto += '\t'.join(l)+"\r\n"

            logging.warn(texto)

            libro = xlwt.Workbook()
            hoja = libro.add_sheet('reporte')

            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')

            f = io.BytesIO()
            libro.save(f)
            datos = base64.b64encode(texto.encode('utf-8'))
            self.write({'archivo':datos, 'name':'asiste_ibros.asl'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_gt_extra.asistente_reporte_ventas',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
