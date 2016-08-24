# -*- encoding: utf-8 -*-

#
# Asistelibros para Guatemala
#
# Status 1.0 - tested on Open ERP 6.1.1
#

{
    'name' : 'asistelibros',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Asistelibros para Guatemala""",
    'author': 'Rodrigo Fernandez',
    'website': 'http://solucionesprisma.com/',
    'depends' : [ 'account', 'l10n_gt_extra' ],
    'init_xml' : [ ],
    'demo_xml' : [ ],
    'update_xml' : [ 'asistelibros_view.xml' ],
    'installable': True,
    'certificate': '',
}
