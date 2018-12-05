# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from datetime import datetime
import base64
import logging

class asistente_ventas(osv.osv):
    _name = 'asistelibros.asistente_ventas'
    _description = 'Asistelibros de ventas'

    def reporte(self, cr, uid, ids, context={}):

        result = []
        for obj in self.browse(cr, uid, ids, context):

            periodos_id = [x.id for x in obj.periodos_id]
            diarios_id = [x.id for x in obj.diarios_id]
            facturas_id = self.pool.get('account.invoice').search(cr, uid, [('state','in',['open','cancel','paid']), ('period_id','in',periodos_id), ('journal_id','in',diarios_id)])

            for f in self.pool.get('account.invoice').browse(cr, uid, facturas_id):

                doc_criva = f.criva
                criva = f.valor_constancia
                # if f.type == "out_invoice":
                #     for p in f.payment_ids:
                #         if p.journal_id.id == 46:
                #             doc_criva = p.ref
                #             criva = p.credit


                # Datos basicos
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

                # for l in f.invoice_line:
                #     if not l.product_id or l.product_id.type == 'service':
                #         total_lineas_servicio += l.price_unit*l.quantity*(100-l.discount)/100
                #     else:
                #         total_lineas_bien += l.price_unit*l.quantity*(100-l.discount)/100

                for l in f.invoice_line:
                    if f.tipo_gasto == 'servicio':
                        total_lineas_servicio += l.price_unit*l.quantity*(100-l.discount)/100
                    else:
                        total_lineas_bien += l.price_unit*l.quantity*(100-l.discount)/100

                iva = 0
                for i in f.tax_line:
                    if i.tax_code_id.id == obj.impuesto_id.id:
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
            texto += '|'.join(l)+"\r\n"

        datos = base64.b64encode(texto.encode('utf-8'))
        self.write(cr, uid, ids, {'archivo': datos})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asistelibros.asistente_ventas',
            'res_id': ids[0],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _columns = {
        'company_id': fields.many2one('res.company', 'Empresa', required=True),
        'diarios_id': fields.many2many('account.journal', 'asistelibros_ventas_diario_rel', 'ventas_id', 'diario_id', 'Diarios', required=True),
        'impuesto_id': fields.many2one('account.tax.code', 'Impuesto', required=True),
        'base_id': fields.many2one('account.tax.code', 'Base', required=True),
        'periodos_id': fields.many2many('account.period', 'asistelibros_ventas_periodo_rel', 'ventas_id', 'periodo_id', 'Periodos', required=True),
        'archivo': fields.binary('Reporte'),
    }

    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'asistelibros.asistente_ventas', context=c),
    }
asistente_ventas()

class asistente_compras(osv.osv):
    _name = 'asistelibros.asistente_compras'
    _description = 'Asistelibros de compras'

    def reporte(self, cr, uid, ids, context={}):

        result = []
        for obj in self.browse(cr, uid, ids, context):

            periodos_id = [x.id for x in obj.periodos_id]
            diarios_id = [x.id for x in obj.diarios_id]
            facturas_id = self.pool.get('account.invoice').search(cr, uid, [('state','in',['open','paid']), ('period_id','in',periodos_id), ('journal_id','in',diarios_id)])

            for f in self.pool.get('account.invoice').browse(cr, uid, facturas_id):

                # Datos basicos
                local = True
                peq = f.pequenio_contribuyente
                total_quetzales = 0
                total_lineas_servicio = 0
                total_lineas_bien = 0

                if f.partner_id.country_id and f.partner_id.country_id.id != f.company_id.id:
                    local = False
                if f.dua or f.fauca:
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
                        if not f.cadi:
                            if len(l.invoice_line_tax_ids) > 0 or peq:
                                total_lineas_servicio += l.price_unit*l.quantity*(100-l.discount)/100
                        else:
                            total_lineas_servicio += l.price_unit*l.quantity*(100-l.discount)/100
                    else:
                        if not f.cadi:
                            if len(l.invoice_line_tax_ids) > 0 or peq:
                                total_lineas_bien += l.price_unit*l.quantity*(100-l.discount)/100
                        else:
                            total_lineas_bien += l.price_unit*l.quantity*(100-l.discount)/100

                iva = 0
                for i in f.tax_line:
                    if i.tax_code_id.id == obj.impuesto_id.id:
                        iva += i.amount
                if f.amount_total*iva > 0:
                    iva = total_quetzales/f.amount_total*iva

                r = [
                    f.date_invoice,
                    '1', # Establecimiento
                    'C' # Compra/Venta
                ]

                # Documento
                if f.type == 'in_invoice':
                    if peq:
                        r.append('FPC')
                    elif f.dua:
                        r.append('DA')
                    elif f.fauca:
                        r.append('FA')
                    elif f.reference and len(f.reference.split()[0]) > 6:
                        r.append('FCE')
                    else:
                        r.append('FC')
                else:
                    r.append('NC')

                # Serie y numero
                if f.reference and len(f.reference.split(None, 1)) > 1:
                    r.append(f.reference.split(None, 1)[0])
                    r.append(f.reference.split(None, 1)[1])
                else:
                    r.append("")
                    r.append("")

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

                # Local o importacion
                if local:
                    r.append('L')
                else:
                    r.append('I')

                # Bien o servicio de importacion
                if not local:
                    if f.tipo_gasto in ['compra','importacion','combustible','mixto']:
                        r.append('BIEN')
                    else:
                        r.append('SERVICIO')
                else:
                    r.append('')

                # Emitido o anulado
                r.append('')

                # Orden cedula
                r.append('')

                # Registro cedula
                r.append('')

                # FAUCA o DUA
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
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor bien importacion
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if not local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor servicio local
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Valor servicio importacion
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if not local and not f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Valor exento bien local
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor exento bien importacion
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if not local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))
                    else:
                        r.append('0')

                # Valor exento servicio local
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Valor exento servicio importacion
                if f.state in ['cancel'] or peq:
                    r.append('')
                else:
                    if not local and f.cadi and f.amount_total != 0:
                        r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))
                    else:
                        r.append('0')

                # Tipo de constancia
                r.append('')

                # Numero de constancia
                r.append('')

                # Valor de constancia
                r.append('')

                # Valor bien pequeño local
                if f.state in ['cancel'] or not peq:
                    r.append('')
                else:
                    r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_bien))

                # Valor servicios pequeño local
                if f.state in ['cancel'] or not peq:
                    r.append('')
                else:
                    r.append('%.2f' % (total_quetzales/f.amount_total*total_lineas_servicio))

                # Valor bien pequeño importacion
                r.append('')

                # Valor servicios pequeño importacion
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
            texto += '|'.join(l)+"\r\n"

        datos = base64.b64encode(texto.encode('utf-8'))
        self.write(cr, uid, ids, {'archivo': datos})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asistelibros.asistente_compras',
            'res_id': ids[0],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _columns = {
        'company_id': fields.many2one('res.company', 'Empresa', required=True),
        'diarios_id': fields.many2many('account.journal', 'asistelibros_comprasdiario_rel', 'compras_id', 'diario_id', 'Diarios', required=True),
        'impuesto_id': fields.many2one('account.tax.code', 'Impuesto', required=True),
        'base_id': fields.many2one('account.tax.code', 'Base', required=True),
        'periodos_id': fields.many2many('account.period', 'asistelibros_compras_periodo_rel', 'compras_id', 'periodo_id', 'Periodos', required=True),
        'archivo': fields.binary('Reporte'),
    }

    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'asistelibros.asistente_compras', context=c),
    }
asistente_compras()
