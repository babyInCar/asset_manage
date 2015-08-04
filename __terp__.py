##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

{
    "name" : "Seeed asset manage",
    "author" : "Coniverse",
    "version" : "1.0",
    "description": "Seeed Asset Module",
    "depends" : ["base","process","hr"],
    "init_xml" : [],
    "update_xml" : [
        "security/hr_seeed_asset_security.xml",
        "security/ir.model.access.csv",        
        'hr_seeed_asset_manage_view.xml',
        'hr_seeed_asset_manage_workflow.xml', 
    ],
    # "category" : "Generic Modules/Human Resources",
    "active": False,
    "installable": True
    # 'certificate': '0063495605623',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

