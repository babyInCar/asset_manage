# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from __future__ import division
from osv import fields,osv
from tools.translate import _
import math
import tools
import time


class hr_seeed_asset_manage(osv.osv):
    _name = "hr.seeed.asset.manage"
    _description = "Seeed固定资产明细"

    # _asset_email_tmp1 = '''
    #     Hi %(name)s:
    #     申请人%(applicant)s提交了资产领取申请，请于OE系统中进行审核。       
    #     '''

    _columns = {
        'yf_asset_id':fields.char(u'固资编号',size=64,select=1),
        'asset_id': fields.char(u'OE编号', size=64,select=1),
        'name': fields.selection([(u'主机',u'主机'),
                                (u'主机(服务器)',u'主机(服务器)'),                                
                                (u'显示器',u'显示器'),
                                (u'服务器',u'服务器'),
                                (u'一体机',u'一体机'),
                                (u'上网本',u'上网本'),
                                (u'笔记本',u'笔记本'),
                                (u'打印机',u'打印机'),                            
                                (u'条码打印机',u'条码打印机'),
                                (u'华硕平板',u'华硕平板')],u'资产类型',select=1),        
        'ref_department': fields.many2one('hr.department',  u'部门',select=1),
        'keeper': fields.many2one('hr.employee', u'部门保管人', readonly=True),        
        'date_purchased':fields.datetime(u'购买时间'),
        'price':fields.float(u'设备价格',digits=(8,2)), #,states={'draft':[('readonly',False)]}
        'depreciation':fields.float(u'折旧年限(年)',digits=(4,2)),
        'lend_line_id':fields.one2many('hr.seeed.asset.lend.line','lend_id',u'借出记录'),
        'fetch_line_id':fields.one2many('hr.seeed.asset.fetch.line','fetch_id',u'领取记录'),
        'repair_line_id':fields.one2many('hr.seeed.asset.repair.line','repair_id',u'维修记录'),
        'attribute_id':fields.one2many('hr.seeed.asset.attribute','asset_id',u'资产属性'),
        'user_change_id':fields.one2many('hr.seeed.asset.user.log','change_id',u'资产使用人变更记录'),
        'curr_user':fields.char(u'当前使用人',size=32,select=1),
        'position':fields.char(u'放置位置',size=32,select=1),
        'deploy':fields.char(u'配置规格',size=64,select=2),
        # 'department_manager_uid':fields.many2one('hr.employee', u'部门负责人审批',readonly=True,select=True),
        'sys_version':fields.char(u'系统版本',size=32),
        'office_version':fields.char(u'office版本',size=32),
        'supplier':fields.char(u'供应商',size=64),
        'quality_period':fields.integer(u'保质期'),
        # 'purchase_order':fields.many2one('hr.seeed.asset.purchase.request',u'采购单'),
        'condition': fields.selection([
            ('instock',u'在库'),
            ('missing',u'丢失'),
            ('repairing',u'维修'),
            ('applying',u'申请中'),
            ('occupying',u'使用中'),
            ('scrapped',u'报废'),            
            ('other',u'其它'),                                  
            ],u'设备状态',select=1,required=True),
        'remark':fields.char(u'备注',size=256,select=2),
        # 'state':fields.selection([
        #     ('draft',u'草稿'),
        #     ('dep_approving',u'主管审批中'),
        #     ('it_approving',u'IT审核中'),           
        #     ('done',u'审批通过'),
        #     ],u'状态',readonly=True),        
    }
    
    _order = 'asset_id desc'
    _defaults = {
                'depreciation':lambda *a:3.00,
                'condition':lambda *a:'occupying',
    }

    _sql_constraints = [
        # ('asset_id_uniq', 'unique(asset_id)',u'资产ID不能重复!'),
        ('yf_asset_id_uniq', 'unique(yf_asset_id)',u'易飞资产编号不能重复!'),
    ]
    
    def is_accessable(self, cr, uid, context,role_name):        
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        is_editable = not '%s'%role_name in [group.name for group in user.groups_id]
        if is_editable:
            return True
        else:
            return False

    def create(self, cr, uid, vals, context=None):
        flag = self.is_accessable(cr,uid,context,'IT / Asset Admin')
        if flag:
            raise osv.except_osv(_('Warning !'), u'您不是资产管理员，不具有添加新资产的权限！')
        else:
            if not vals.has_key('price'):
                vals['price'] = 1.0
            if vals.has_key('curr_user'):
                vals['condition'] = ''
            else:
                vals['condition'] = 'instock'
            return  super(hr_seeed_asset_manage, self).create(cr, uid, vals, context) 
    
    def write(self,cr,uid,ids,vals,context=None):
        u'''资产编号和易飞编号不能修改 gaos add this 2015.4.29'''
        asset_arr = self.read(cr,uid,ids[0],['yf_asset_id','asset_id'])

        # if vals.has_key('asset_id') and asset_arr['asset_id']:
        #     raise osv.except_osv(_('Warning !'), u'资产编号已经存在，不能修改！')
        # # if asset_arr['asset_id'] and vals['asset_id']:
            
        # if vals.has_key('yf_asset_id') and asset_arr['yf_asset_id'] :
        #     raise osv.except_osv(_('Warning !'), u'易飞资产编号已经存在，不能修改！')
        return super(hr_seeed_asset_manage,self).write(cr,uid,ids,vals,context)

hr_seeed_asset_manage()

class hr_seeed_asset_attribute(osv.osv):
    _name = "hr.seeed.asset.attribute"
    _description = u"资产属性详细"

    _columns = {
        'asset_id':fields.many2one('hr.seeed.asset.manage',u'资产属性明细'),
        # 'id':fields.char
        'name':fields.char(u'属性名',size=32),
        'value':fields.char(u'属性值',size=32),
        'active':fields.boolean(u'有效'),
    }

    _defaults={
        'active':lambda *a:True,
    }
hr_seeed_asset_attribute()


class hr_seeed_asset_purchase_request(osv.osv):
    _name = "hr.seeed.asset.purchase.request"
    _description = u"固定资产采购申请"

    _columns = {
        'name':fields.char(u'单据号', size=16,readonly=True,select=1),
        # 'asset_manage_id':fields.one2many('hr.seeed.asset.manage','purchase_order','采购单'),
        'applicant':fields.many2one('hr.employee',u'申请人',readonly=True,select=1),
        'approver':fields.many2one('hr.employee',u'审批人',readonly=True),
        'department':fields.many2one('hr.department',u'所在部门',readonly=True),
        'asset_name':fields.char(u'资产名称',size=64,select=1),
        # 'qty':fields.integer(u'申请数量',readonly=True,states={'draft':[('readonly',False),('required',True)]}),
        'demand':fields.char(u'资产要求简述',size=128,readonly=True,states={'draft':[('readonly',False)]}),
        'resource':fields.selection([('outgo',u'外购'),('diy',u'自行组装'),('outrent',u'外租')],u'资产来源',states={'draft':[('required',True)]}),
        'type':fields.selection([('usual',u'普通办公设备类'),('profdevice',u'专用设备')],u'资产类别',readonly=True,states={'draft':[('required',True)],'draft':[('readonly',False)]}),
        'request_lines':fields.one2many('hr.seeed.asset.purchase.request.line','request_id',u'采购明细',states={'draft':[('readonly',False)]}),
        'estimate_price':fields.float(u'预估价格',digits=(8,2),states={'it_confirming':[('required',True)]}),
        'department_manager':fields.many2one('hr.employee',u'部门经理'),
        'it_approver':fields.many2one('hr.employee','IT工作流审批人'),
        'actual_price':fields.float(u'实际价格',digits=(8,2)),
        'reason':fields.text(u'申请理由'),
        'ceo_id':fields.many2one('hr.employee',u'总经理'),
        'state':fields.selection([('draft',u'草稿'),('dep_approving',u'部门经理审批中'),('ceo_approving',u'CEO审批中'),('it_confirming',u'IT确认中'),('done',u'结束')],u'状态',readonly=True),
    }

    _defaults = {
        'name':lambda self,cr,uid,context:self.create_pr_num(cr,uid,context),
        'applicant':lambda self,cr,uid,context:self.get_employee(cr,uid,context),
        'approver':lambda self,cr,uid,context:self.get_department_manager(cr,uid,context),
        'department':lambda self,cr,uid,context:self.get_department(cr,uid,context),
        'department_manager':lambda self,cr,uid,context:self.get_department_manager(cr,uid,context),
        'it_approver':lambda self,cr,uid,context:self.get_it_approver(cr,uid,context),
        'state':lambda *a:'draft',
        'ceo_id':lambda *a:1,
    }

    def get_employee(self,cr,uid,context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr,uid,[('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['id','name'], context)
        return res and res[0]['id'] or 0

    #取到申请人主管的信息    
    def get_approver(self, cr, uid, context={}):
        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        ids = employee_obj.search(cr,uid,[('user_id','=',uid)])
        if not ids:
            return 0
        employee = employee_obj.browse(cr, uid, ids[0])
        department = department_obj.browse(cr, uid, employee.department_id.id)
        if department.manager_id.id == uid:
            return ids[0]
        # else:
        
        if employee.work_approver_id :
            return employee.work_approver_id.id
        parent = employee_obj.browse(cr, uid, employee.parent_id.id)
        return parent.id

    def get_department(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr,uid,[('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['department_id'], context)
        return res[0]['department_id'][0] or 0

    def get_department_manager(self,cr,uid,context):
        #获取部门经理的id
        leader_id = self.get_approver(cr,uid,context)        
        hr_obj = self.pool.get('hr.employee')
        leader_obj = hr_obj.browse(cr,uid,leader_id)
        manager_id =  leader_obj.user_id.id
        if manager_id in (1,17,14,481,13,49,107,176,116,347):
            dep_id = leader_obj.id
            # print dep_id  
        else:
            dep_id    = self.get_approver(cr,manager_id,context)
        return dep_id

    def get_it_approver(self,cr,uid,context={}):
        u'''获取IT工作流的审批人'''
        hr_obj = self.pool.get('hr.employee')
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        it_engineer_id = hr_obj.search(cr,uid,[('title','=','IT工程师'),('active','=','TRUE')])
        # asset_obj.read()
        # if work_approver_id:
        #     return employee.work_approver_id.id
        return it_engineer_id[0]

    def create_pr_num(self, cr, uid, context={}):
        sql = "select count(*) from hr_seeed_asset_purchase_request where date(create_date) = '%s'" % time.strftime('%Y-%m-%d')
        cr.execute(sql)
        result = cr.fetchone()[0]
        if result != 0:
            sql = "select substring(name from 9 for 3)::integer from hr_seeed_asset_purchase_request where date(create_date) = '%s' order by id desc" % time.strftime('%Y-%m-%d')
            cr.execute(sql)
            total_num = cr.fetchone()[0]
        else:
            total_num = 0
        total_num = total_num+1
        order_name = 'CR'+time.strftime('%y%m%d')+('%03d'%total_num)
        return order_name

    def action_draft(self,cr,uid,ids,context={}):
        obj = self.browse(cr, uid, ids[0])
        if obj.state == 'dep_approving' and obj.department_manager.user_id.id != uid:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能退回')         
        elif obj.state == 'ceo_approving' and uid != 13:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能退回') 

        self.write(cr,uid,ids,{'state':'draft'})       
    

    def action_submit(self,cr,uid,ids,context={}):        
        u'''提交当前的资产领用单,发邮件给直接负责人 gaos add this 2015.4.17 modified 2015.06.18''' 
        # print "ttttt" 

        parent_id = self.get_approver(cr,uid,context)
        request = self.browse(cr, uid, ids[0])
        employee_obj = self.pool.get('hr.employee')       
        curr_id = request.approver.id
        leader_id = request.approver.user_id.id
        if request.applicant.user_id.id != uid:
            raise osv.except_osv(_('Warning !'), u'你不是申请人不能提交申请' )
        if not request.request_lines:
            raise osv.except_osv(_('Warning !'), u'采购明细不能为空!' )
        self.write(cr, uid, ids, {'state':'dep_approving'})
        return True    

    def action_confirm(self,cr,uid,ids,context={}):
        #各部门部长审批
        request = self.browse(cr,uid,ids[0])
        dp_manager =  request.department_manager.user_id.id
        if dp_manager != uid:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能提交') 
        flag = self.ssh_to_who(cr,uid,ids,context)
        if flag == "ceo":
            self.write(cr,uid,ids,{'state':'ceo_approving'})
        else:
            self.write(cr,uid,ids,{'state':'done'})

    def action_it_confirm(self,cr,uid,ids,context={}):
        #总经理审批完成了，到IT审批
        request = self.browse(cr,uid,ids[0])
        fetch_obj = self.pool.get('hr.seeed.asset.fetch.line')
        res_obj = self.pool.get('hr.employee')
        hr_id   = res_obj.search(cr,uid,[('user_id','=',uid)])

        if request.state == 'ceo_approving' and  uid != 13:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能提交')         
        self.write(cr,uid,ids,{'state':'it_confirming'})

    def action_done(self,cr,uid,ids,context={}):
        #到货之后IT工程师确认把物资发放给申请人(之前必须建立相应的资产明细)
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        flag = asset_obj.is_accessable(cr,uid,context,'IT / Asset Admin')
        if flag:
            raise osv.except_osv(_('Warning !'), u'你不是资产管理员，不能审批！')
        request = self.browse(cr,uid,ids[0])
        name = request.name
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        asset_id = asset_obj.search(cr,uid,[('purchase_order','=',name)])
        if not asset_id:
            raise osv.except_osv(_('Warning !'), u'你还没有为此申请单建相应的资产明细，不能确认领取！')
        else:
            self.write(cr,uid,ids,{'state':'done'})

    def ssh_to_who(self,cr,uid,ids,context={}):
        u'''根据价格判断是否要经过总经理审批 gaos add this 2015.4.21 '''
        actual_price = self.read(cr,uid,ids,['estimate_price'])
        print actual_price
        if actual_price >= 20000:
            return "ceo"
        else:
            return "dep"

hr_seeed_asset_purchase_request()

class hr_seeed_asset_purchase_request_line(osv.osv):
    _name = 'hr.seeed.asset.purchase.request.line'
    _description = u'资产采购明细'

    _columns = {
        'request_id':fields.many2one('hr.seeed.asset.purchase.request',u'资产明细'),
        'asset_name':fields.char(u'资产名称',size=32,required=True),
        'asset_desc':fields.char(u'资产描述',size=64),
        'asset_qty':fields.integer(u'资产数量',required=True),
        # 'asset_unit':fields.float(u'单价',digits=(7,2)),
        # 'asset_price':fields.float(u'金额',digits=(8,2)),
    }

    _defaults={
        'asset_qty':lambda *a:1,
    }
hr_seeed_asset_purchase_request_line()

class hr_seeed_asset_lend_request(osv.osv):
    _name = "hr.seeed.asset.lend.request"
    _description = u"资产领借申请"

    _columns = {
        'name':fields.char(u'单据号', size=16,readonly=True,select=1),
        'create_date': fields.datetime(u'单据日期', readonly=True),
        'date_submit': fields.date(u'提交日期', readonly=True),
        'ref_department': fields.many2one('hr.department',  u'领（借）料部门',readonly=True),        
        'applicant': fields.many2one('hr.employee', u'申请人', readonly=True,select=1),
        'approver': fields.many2one('hr.employee', u'审批人', readonly=True),
        'processing': fields.many2one('hr.employee', u'处理人',readonly=True),
        'type': fields.selection([('recipients',u'领用'),('borrow',u'借用')],u'领取类型',required=True, readonly=True,states={'draft':[('readonly',False)]}),
        'notes': fields.char(u'备注',size=256, readonly=True, states={'draft':[('readonly',False)]}),        
        'lend_lines': fields.one2many('hr.seeed.asset.lend.request.line', 'ar_id', u'领(借)物料明细', readonly=True, states={'draft':[('readonly',False)],'approving':[('readonly',False)]}),
        'it_processer':fields.char(u'IT审核人',size=32),
        'failed_reason': fields.char(u'退回原因', size=128, readonly=True),
        'use_method_detail':fields.char(u'领借详细用途', size=512, required=True,readonly=True,states={'draft':[('readonly',False)]}),
        # 'curr_user_id':fields.many2one('hr.employee',u'当前处理人',readonly=True),
        'state' : fields.selection(
             [('draft',u'草稿'),
             ('approving',u'主管审批中'),             
             ('it_approving',u'IT审批中'),             
             ('cancel', u'取消'),
             ('done',u'完成'),],u'状态',readonly=True),
    }

    _defaults={
        'applicant':lambda self,cr,uid,context:self.get_employee(cr,uid,context),
        # 'approver':lambda self,cr,uid,context:self.get_approver(cr,uid,context),
        'ref_department':lambda self,cr,uid,context:self.get_department(cr,uid,context),
        'state':lambda *a:'draft',
        'it_processer':lambda self,cr,uid,context:self.get_it_processor(cr,uid,context),
        'name':lambda self,cr,uid,context:self.create_material_num(cr,uid,context),
    }

    def get_employee(self,cr,uid,context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr,uid,[('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['id','name'], context)
        return res and res[0]['id'] or 0

    #取到申请人主管的信息    
    def get_approver(self, cr, uid, context={}):
        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        ids = employee_obj.search(cr,uid,[('user_id','=',uid)])
        if not ids:
            return 0
        employee = employee_obj.browse(cr, uid, ids[0])
        department = department_obj.browse(cr, uid, employee.department_id.id)
        if department.manager_id.id == uid:
            return ids[0]
        # else:
        
        if employee.work_approver_id :
            return employee.work_approver_id.id
        parent = employee_obj.browse(cr, uid, employee.parent_id.id)
        return parent.id

    def get_department(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr,uid,[('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['department_id'], context)
        return res[0]['department_id'][0] or 0

    def get_it_processor(self,cr,uid,context={}):
        hr_obj = self.pool.get('hr.employee')
        it_list = ''
        it_engineer_id = hr_obj.search(cr,uid,[('title','=','IT工程师'),('active','=','TRUE')])
        net_enginer_id = hr_obj.search(cr,uid,[('title','=','OPE网络'),('active','=','TRUE')])
        # it_engineer  = hr_obj.read(cr,uid,it_engineer_id)
        # net_engineer = hr_obj.read(cr,uid,net_enginer_id)
        it_list = str(it_engineer_id[0]) + ',' + str(net_enginer_id[0])
        return it_engineer_id

    def ssh_to_who(self,cr,uid,ids,context={}):
        request = self.browse(cr,uid,ids[0])    
        lend_type = request.type
        if lend_type == 'borrow':
            return "it"
        else:
            return "dep"

    def create_material_num(self, cr, uid, context={}):
        sql = "select count(*) from hr_seeed_asset_lend_request where date(create_date) = '%s'" % time.strftime('%Y-%m-%d')
        cr.execute(sql)
        result = cr.fetchone()[0]
        if result != 0:
            sql = "select substring(name from 9 for 3)::integer from hr_seeed_asset_lend_request where date(create_date) = '%s' order by id desc" % time.strftime('%Y-%m-%d')
            cr.execute(sql)
            total_num = cr.fetchone()[0]
        else:
            total_num = 0
        total_num = total_num+1
        order_name = 'AR'+time.strftime('%y%m%d')+('%03d'%total_num)
        return order_name

    def change_asset_state(self,cr,uid,ids,state,applicant_id=0):
        u'''公共函数 修改资产的状态 gaos add this 2015.04.30'''
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        lend_obj = self.pool.get('hr.seeed.asset.lend.request.line')
        set_id = lend_obj.search(cr,uid,[('ar_id','=',ids[0])])
        for line in set_id:
            time_arr = lend_obj.read(cr,uid,line,['qty','est_back_time','asset_id'])
            asset_one = time_arr['asset_id'][0]
            est_back_time = time_arr['est_back_time']            
            set_arr = asset_obj.search(cr,uid,[('id','=',asset_one)])
            # print set_arr
            if applicant_id != 0:
                asset_obj.write(cr,1,set_arr,{'condition':state,'curr_user':applicant_id})
            else:
                asset_obj.write(cr,1,set_arr,{'condition':state})
        return True

    def action_draft(self,cr,uid,ids,context={}):
        obj = self.browse(cr, uid, ids[0])
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        flag = asset_obj.is_accessable(cr,uid,context,'IT / Asset Admin')
        if obj.state == 'approving' and obj.approver.user_id.id != uid:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能退回')         
        elif obj.state == 'it_approving' and flag:
            raise osv.except_osv(_('Warning !'), u'您不是审批人，不能退回')
        self.change_asset_state(cr,uid,ids,'instock')
        self.write(cr,uid,ids,{'state':'draft'})

    def action_submit(self,cr,uid,ids,context={}):
        request = self.browse(cr,uid,ids[0])
        applicant = request.applicant.id
        # asset_obj = self.pool.get('hr.seeed.asset.manage')
        lend_obj = self.pool.get('hr.seeed.asset.lend.request.line')        
        if request.applicant.user_id.id != uid:
            raise osv.except_osv(_('Warning !'), u'你不是申请人不能提交申请')
        flag_arr = self.read(cr,uid,ids,['type'])        
        
        set_id = lend_obj.search(cr,uid,[('ar_id','=',ids[0])])
        if not set_id:
            raise osv.except_osv(_('Warning !'), u'领借资产明细不能为空！')
        approver_id = self.get_approver(cr,uid,ids)
        it_approver = self.get_it_processor(cr,uid)
        for line in set_id:                        
            time_arr = lend_obj.read(cr,uid,line,['qty','est_back_time','asset_id'])            
            est_back_time = time_arr['est_back_time']            
            # set_arr = asset_obj.search(cr,uid,[('id','=',asset_one)])
            if time_arr['qty'] < 1:
                raise osv.except_osv(_('Warning !'), u'领借用数量不能小于1！')
            if flag_arr[0]['type'] == 'borrow':
            #检查是否填写了预归还时间    
                if not time_arr['est_back_time']:
                    raise osv.except_osv(_('Warning !'), u'预计归还时间不能为空！')
                self.write(cr,uid,ids,{'state':'it_approving','approver':it_approver})
            else:
                self.write(cr,uid,ids,{'state':'approving','approver':approver_id})
            #第一个人申请之后把资产状态写成"申请中" gaos add this 2015.4.30
            self.change_asset_state(cr,uid,ids,'applying',applicant)
        return True
        

    def action_it_confirm(self,cr,uid,ids,context={}):
        request = self.browse(cr,uid,ids[0])        

        if request.type == 'recipients' and request.state == 'approving' and  request.approver.user_id.id != uid :
            raise osv.except_osv(_('Warning !'), u'你不是申请人主管不能提交')
        elif request.type == 'borrow' and request.applicant.user_id.id != uid:
            raise osv.except_osv(_('Warning !'), u'你不是申请人不能提交申请')
        flag_arr = self.read(cr,uid,ids,['type'])
        self.write(cr,uid,ids,{'state':'it_approving'})       
     
    def action_done(self,cr,uid,ids,context={}):
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        flag = asset_obj.is_accessable(cr,uid,context,'IT / Asset Admin')
        if flag:
            raise osv.except_osv(_('Warning !'), u'你不是资产管理员，不能审批！')
        # self.is_accessable(cr,uid,ids,context,'HR / Asset Admin')
        fetch_obj = self.pool.get('hr.seeed.asset.fetch.line')
        lend_obj  = self.pool.get('hr.seeed.asset.lend.line')
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        user_obj  = self.pool.get('hr.seeed.asset.user.log')
        req_obj =  self.pool.get('hr.seeed.asset.lend.request.line')  
        hr_obj  = self.pool.get('hr.employee')
        flag_arr = self.read(cr,uid,ids,['type'])
        request  = self.browse(cr,uid,ids[0])
        applicant = request.applicant.id        
        #读取领借明细里面的资产明细，审批通过之后把状态写成"使用中",然后给领用的设备都添加一条领(借) 记录                 
        set_id  =  req_obj.search(cr,uid,[('ar_id','=',ids[0])])        
        hr_id   = hr_obj.search(cr,uid,[('user_id','=',uid)])
        for line in set_id:
            asset_arr = req_obj.read(cr,uid,line,['asset_id','est_back_time'])
            asset_one = asset_arr['asset_id'][0]
            est_back_time = asset_arr['est_back_time']            
            set_arr = asset_obj.search(cr,uid,[('id','=',asset_one)])
            user_id = user_obj.search(cr,uid,[('change_id','=',asset_one)])
            if flag_arr[0]['type'] == 'recipients':                
                fetch_obj.create(cr,uid,{'fetch_id':asset_one,'fetch_time':time.strftime('%Y-%m-%d %H:%M:%S'),'fetch_person':applicant,'pass_by':hr_id[0]})
                # asset_obj.write(cr,uid,set_arr,{'condition':'occupying'})
                # user_obj.write(cr,uid,user_id,{'person':applicant,'start_time':time.strftime('%Y-%m-%d %H:%M:%S')})
            elif flag_arr[0]['type'] == 'borrow':
                lend_obj.create(cr,uid,{'lend_id':asset_one,'lend_time':time.strftime('%Y-%m-%d %H:%M:%S'),'lend_to':applicant,'est_back_time':est_back_time,'pass_by':hr_id[0]})
            asset_obj.write(cr,uid,set_arr,{'condition':'occupying','curr_user':applicant})
            if not user_id:
                user_obj.create(cr,uid,{'change_id':asset_one,'person':applicant,'start_time':time.strftime('%Y-%m-%d %H:%M:%S')})
            else:    
                user_obj.write(cr,uid,user_id,{'person':applicant,'start_time':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr,uid,ids,{'state':'done'})
        return True

hr_seeed_asset_lend_request()

class hr_seeed_asset_lend_request_line(osv.osv):
    _name = "hr.seeed.asset.lend.request.line"
    _description = u"资产领借申请详细"

    def _compute_amount(self, cr, uid, ids, field_names=None, arg=False, context={}):
        u'''计算出总金额'''
        if not field_names:
            field_names=[]
        res = {}.fromkeys(ids, 0.0)
        cr.execute('select id,price_unit*qty from hr_seeed_asset_lend_request_line where id in %s ;', (tuple(ids),))
        result=cr.fetchall()
        for id, amount in result:
            res[id] = amount
        #for id in ids:
            #material = self.browse(cr, uid, id)
            #res[id] = material.price_unit*material.quantity
        return res
    _columns={
        'ar_id':fields.many2one('hr.seeed.asset.lend.request',u'借出记录'),        
        'asset_id':fields.many2one('hr.seeed.asset.manage',u'资产名称',readonly=True,domain="[('condition','=','instock')]",states={'draft':[('readonly',False)]}),
        'price_unit':fields.float(u'单价',digits=(16,4), readonly=True),
        'est_back_time':fields.datetime(u'预计归还时间'),
        'qty':fields.integer(u'数量',readonly=True),
        # 'amount': fields.function(_compute_amount,store=True, method=True, type='float',string=u"金额", readonly=True),
        'amount':fields.float(u'总金额',digits=(16,4), readonly=True),

    }
    _defaults={
        'qty':lambda *a:1,
    }
    # def product_change(self, cr, uid, ids, product_id):
    #     if not product_id:
    #         return {'value':{'code':False,'price_unit':False,'product_uom':False,'supply_method':False},}
    #     product_obj = self.pool.get('product.product')
    #     product = product_obj.browse(cr, uid, product_id)
    #     result = {'code':product.code,
    #               'price_unit':product.standard_price,
    #               'product_uom':product.uom_id.id,
    #               'supply_method':product.supply_method,
    #               'product_name_description':(product.default_code or '')+(product.name or '' )+(product.variants or '')}
    #     return {'value':result}

    def price_change(self,cr,uid,ids,asset_id):
        if not asset_id:
            return {'value':{'price_unit':False}}
        asset_obj = self.pool.get('hr.seeed.asset.manage')
        asset = asset_obj.browse(cr,uid,asset_id)
        
        amount = asset.price
        result = {
            'price_unit':amount,
            'amount':amount,
        }
        
        return {'value':result}
   

hr_seeed_asset_lend_request_line()

class hr_seeed_asset_lend_line(osv.osv):
    u"""设备借出记录 gaos add this 2015.4.9"""

    _name = "hr.seeed.asset.lend.line"
    _description = u"固定资产借出记录"
    
    _columns = {
        'lend_id':fields.many2one('hr.seeed.asset.manage',u'借出记录'),
        'lend_time':fields.datetime(u'借出时间',required=True),
        'lend_to':fields.many2one('hr.employee',u'借给',required=True),
        'pass_by':fields.many2one('hr.employee',u'经手人',required=True),
        'est_back_time':fields.datetime(u'预计归还时间',required=True),
        'real_back_time':fields.datetime(u'实际归还时间'),
        'remark':fields.char(u'备注',size=64),   
    }

hr_seeed_asset_lend_line()

class hr_seeed_asset_fetch_line(osv.osv):
    _name = "hr.seeed.asset.fetch.line"
    _description = u"固定资产领用记录"

    _columns = {
        'fetch_id':fields.many2one('hr.seeed.asset.manage',u'领取记录'),
        'fetch_time':fields.datetime(u'领用时间',required=True),
        'fetch_person':fields.many2one('hr.employee',u'领取人',required=True),
        'pass_by':fields.many2one('hr.employee',u'经手人',required=True),
        
    }
hr_seeed_asset_fetch_line()

class hr_seeed_asset_repair_line(osv.osv):
    _name = "hr.seeed.asset.repair.line"
    _description = "固定资产维修记录"

    _columns = {
        'repair_id':fields.many2one('hr.seeed.asset.manage',u'维修记录',required=True),
        'repair_time':fields.datetime(u'维修时间',required=True),
        'cost':fields.float(u'花费',required=True),
        'within_garantee':fields.boolean(u'是否在保质期内'),
        'remark':fields.char(u'备注',size=128),
        # 'alter_onchange_id':fields.many2one('mrp.project.alter',u'变更序号'),
    }

    _defaults={
        'within_garantee':lambda *a:True,
    }
hr_seeed_asset_repair_line()

class hr_seeed_asset_user_log(osv.osv):
    _name = "hr.seeed.asset.user.log"
    _description = u"使用人变更记录"
    _columns={
            "change_id":fields.many2one('hr.seeed.asset.manage',u'资产名称'),
            "person":fields.many2one('hr.employee',u'使用人'),
            "start_time":fields.datetime(u'开始使用时间'),
            "end_time":fields.datetime(u'结束使用时间'),
    }

hr_seeed_asset_user_log()

# class hr_seeed_asset_change_log(osv.osv):
#     _name = "hr.seeed.asset.change.log"
#     _description=u"资产修改记录"

#     _columns={

#     }

# hr_seeed_asset_change_log()
