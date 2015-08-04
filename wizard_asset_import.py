# -*- encoding: utf-8 -*-
from datetime import *
import time
import wizard
import ir
import pooler
from osv.osv import except_osv
import base64
from functions.read_excel import Read_Excel
from tools.translate import _
from osv import fields,osv
import netsvc

_init_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="导入资产明细">
    <group colspan="4" col="4">
        <field name="import"/>
        <label string="导入的文件格式必须是excel文件格式" colspan="4"
            align="0.0"/>
        <label string="数据格式为第一行" colspan="4"
            align="0.0"/>
    </group>
</form>'''

_init_fields = {
    'import': {
        'string': u'导入文件',
        'type': 'binary',
        'required': True
    }
}

_result_form = '''<?xml version="1.0"?>
<form string="导入资产明细成功" colspan="4">
<separator string="导入资产明细成功" colspan="4" />
%s
</form>'''

_result_fields = {}

# def _init(self, cr, uid, data, context):
#     _form_fields['begindate']['default'] =time.strftime('%Y-%m-%d')  #date.today()
#     _form_fields['enddate']['default'] =time.strftime('%Y-%m-%d')   #date.today()
#     _form_fields['isweekday']['default']=True
#     return {}

def _do_confirm(self, cr, uid, data, context):
    u'''批量导入资产明细 gaos add this 2015.3.26'''
    num1 = 0      
    num2 = 0  
    mod_dict    =   {}
    record      =   {}
    user_record =   {}
    form = data['form']
    obj = pooler.get_pool(cr.dbname).get('hr.seeed.asset.manage')
    att_obj = pooler.get_pool(cr.dbname).get('hr.seeed.asset.attribute')
    log_obj = pooler.get_pool(cr.dbname).get('hr.seeed.asset.user.log')
    dep_obj = pooler.get_pool(cr.dbname).get('hr.department')
    hr_obj  = pooler.get_pool(cr.dbname).get('hr.employee')   
    error_log = [] 
    trades = Read_Excel(file_contents=base64.decodestring(form['import']),col_n=1,del_n=0)()      
    # num = obj.import_new_employee_lines(cr, uid, trades,)
    if trades:
        for trade in trades:
            res_obj = pooler.get_pool(cr.dbname).get('res.users')            
            asset_dict      =  {}
            attribute_dict  =  {'asset_id':'','name':[],'value':[]}
            temp_dict = []
            log_dict        =  {}
            if trade.has_key(u'固定资产编号') and len(str(trade[u'固定资产编号'])):
                print trade[u'固定资产编号']
                asset_id = obj.search(cr,uid,[('yf_asset_id','=',trade[u'固定资产编号'])])
                asset_dict['yf_asset_id'] = trade[u'固定资产编号']

            if trade.has_key(u'OE编号') and len(str(trade[u'OE编号']).replace(' ','')):
                # asset_id = obj.search(cr,uid,[('asset_id','=',trade[u'OE编号'])])
                asset_dict['asset_id']         =     trade[u'OE编号'] 
            # else:
            #     raise wizard.except_wizard(_('Warning !'),(u'OE编号不能为空！'))                            

            if trade.has_key(u'部门') and len(str(trade[u'部门'])):                
                dep_name =  str(trade[u'部门']).replace('.0','')
                dep_id   = dep_obj.search(cr,uid,[('name','=',dep_name)])
                if not dep_id:
                    raise wizard.except_wizard(_('Warning !'),(u'你输入的部门不存在'))
                # record['department_id']     = dep_id[0]
                # record['yf_db_department']  = dep_id[0]
                asset_dict['ref_department']   =     dep_id[0]

            if trade.has_key(u'资产类型') and len(str(trade[u'资产类型'])):
                asset_dict['name']         =     trade[u'资产类型']

            if trade.has_key(u'放置位置') and len(str(trade[u'放置位置'])):
                asset_dict['position']     =     trade[u'放置位置']

            if trade.has_key(u'配置规格') and len(str(trade[u'配置规格'])):
                asset_dict['deploy']       =     trade[u'配置规格']
                   
            if trade.has_key(u'当前使用人') and len(str(trade[u'当前使用人'])):
                # print trade[u'当前使用人']
                # hr_id = hr_obj.search(cr,uid,[('name','=',str(trade[u'当前使用人']).encode('utf-8'))])
                # if hr_id:                
                asset_dict['curr_user']        =     trade[u'当前使用人']             
                log_dict['person']             =     trade[u'当前使用人']
                # else:
                    # hr_id = hr_obj.search(cr,uid,[('name','=',str(trade[u'当前使用人'])),('active','=',False)])
                    # if hr_id:
                    #     asset_dict['curr_user']        =     hr_id[0]                
                    #     log_dict['person']             =     hr_id[0]     
                    # else:
                    #     continue
                    #     error_log.append('系统中没有查到%s，请检查后重新上传该条信息')
            
            if trade.has_key(u'购买时间') and len(str(trade[u'购买时间'])):
                try:
                    time.strptime(trade[u'购买时间'],"%Y-%m-%d")
                except:
                    raise osv.except_osv(_('Warning !'),'第%d条数据的购买时间格式不对,请确定你设置的格式是文本格式'%(num1+1))

                asset_dict['date_purchased'] = trade[u'购买时间']

            if trade.has_key(u'价格') and len(str(trade[u'价格'])):
                asset_dict['price']            =     float(trade[u'价格'])

            if trade.has_key(u'系统') and len(str(trade[u'系统'])):
                temp_dict.append({'name':'系统版本','value':trade[u'系统']})                            

            if trade.has_key(u'office') and len(str(trade[u'office'])):
                temp_dict.append({'name':'office版本','value':trade['office']})

            if trade.has_key(u'数据库') and len(str(trade[u'数据库'])):
                temp_dict.append({'name':'数据库版本','value':trade[u'数据库']})
                # attribute_dict['key'].append('数据库版本')
                # attribute_dict['value'].append(trade[u'数据库'])

            if trade.has_key(u'供应商') and len(str(trade[u'供应商'])):
                asset_dict['supplier']   =     trade[u'保质期']

            if trade.has_key(u'保质期') and len(str(trade[u'保质期'])):
                asset_dict['quality_period']   =     trade[u'保质期']

            if trade.has_key(u'备注') and len(str(trade[u'备注'])):
                asset_dict['remark']           =     trade[u'备注']
            
            # asset_dict = {
            #     'asset_id':asset_id,
            #     'ref_department':ref_dep,
            #     'asset_name':name,    
            #     'charger':dep_man,  #部门负责人
            #     'keeper':dep_kper,  #部门保管人
            #     ''
            # }
            if asset_id:
                obj.write(cr,uid,asset_id,asset_dict)
                num2 += 1
            else:
                asset_id = obj.create(cr,uid,asset_dict)
                # print temp_dict
                attribute_dict['asset_id'] =   asset_id
                for line in temp_dict:
                    # attribute_dict['key']  =  key
                    attribute_dict['name'] = line['name']
                    attribute_dict['value'] = line['value']
                    att_obj.create(cr,uid,attribute_dict)   #资产属性表里面写入数据                    
                log_dict['change_id']      =   asset_id                 
                num1 += 1
                if asset_dict.has_key('curr_user'):                
                    log_obj.create(cr,uid,log_dict)                
            error_str = ''
            if error_log:
                for line in error_log:
                    error_str += line+',\r\n'
                lable_string = "<label string='导入新资产总数：%s,修改资产总数:%s,错误信息如下：%s' />" % (num1,num2,error_str)
            else:                
                lable_string = "<label string='导入新资产总数：%s,修改资产总数:%s' />" % (num1,num2)
            self.states['process']['result']['arch'] = _result_form % lable_string
    return {}


class wizard_asset_import(wizard.interface):
    states = {
              
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': _init_form,
                'fields': _init_fields,
                'state': [('end', u'取消'), ('process', u'上传')]
            }
        },
              
        'process': {
            'actions': [_do_confirm],
            'result': {
                'type': 'form',
                'arch': _result_form,
                'fields': _result_fields,
                'state': [('end', u'关闭')]
            }
        }
    }
wizard_asset_import('wizard_asset_import')
