from odoo import models, fields,api,_
from odoo.exceptions import ValidationError
import re

# self.env.user.has_group('base.group_user') # Check for Internal User
#     self.env.user.has_group('base.group_portal') # Check for Portal User
#     self.env.user.has_group('base.group_public') # Check for Public User
#
# class ResPartners(models.Model):
#     _inherit = 'res.partner'
#
#     @api.model
#     def create(self, vals_list):
#         res = super(ResPartners, self).create(vals_list)
#         print("yes working")
#         # do the custom coding here
#         return res


class UniversityStudent(models.Model):
    _name = 'university.student'
    _inherit = ['mail.thread','mail.activity.mixin',]
    _description = 'student inscription'
    _rec_name = 'f_name'


    _sql_constraints = [
        ('cin_pass_uniq', 'unique(identity_card)', 'Numero de cin/passeport existe déja'),
        ('e_mail_uniq', 'unique(e_mail)', 'Email existe déja'),
     ]

    reference = fields.Char(string='student reference', required=True, copy=False, readonly=True,
                             default=lambda self: _('New'))
    student_id = fields.Many2one('res.users', ondelete='set null', string="User", index=True)
    class_id = fields.Many2one(comodel_name='university.class', string='Classe' )

    f_name = fields.Char(string="Prenom",required = True )
    l_name = fields.Char(string='Nom',tracking = True ,required = True)
    date_of_birth = fields.Date(string='Date de Naissance', required=True)
    e_mail = fields.Char('E-mail', tracking=True , required = True)
    identity_card = fields.Char(string='Carte Identité',required = True,tracking = True)
    phone = fields.Char(string='Téléphone' ,required = True)
    gender = fields.Selection([('male','Male'),('female','Female')] )
    rue = fields.Char('Rue')
    ville = fields.Char('Ville')
    code_postale = fields.Char('Code postale')
    date_inscription = fields.Datetime(string='Date Inscription' , default=fields.Datetime.now, readonly=True)
    image = fields.Binary(string="Image", attachment=True)
    image_cin = fields.Binary(string="CIN", attachment=True)
    image_cv= fields.Binary(string="CV", attachment=True)
    date_paiement = fields.Datetime(string='Date Prochain Paiement', default=fields.Datetime.now)
    state = fields.Selection([
        ('nouveau', 'Nouveau Inscrit'),
        ('attente', 'En attente'),
        ('affecte', 'Affecté'),
        ('paiment_reg', 'Paiement effectué'),
    ], string='Status', readonly=True, default='nouveau')



    def action_administration(self):
        student_group = self.env.ref('university_managment.group_university_student')
        student_group.write({'users':[(4,self.student_id.id)]})
        teacher_group = self.env.ref('university_managment.group_university_teacher')
        teacher_group.write({'users':[(3,self.student_id.id)]})
        admin_group = self.env.ref('university_managment.group_university_administrateur')
        admin_group.write({'users':[(3,self.student_id.id)]})

    def action_en_attente(self):
        for rec in self:
            rec.state = 'attente'
        print("azuz")

    def action_affecte(self):
        for rec in self:
            rec.state = 'affecte'

    def action_paiement_reg(self):
        for rec in self:
            rec.state = 'paiment_reg'

    # @api.model
    # def create(self, values):
    #     if values.get('reference', _('New')) == _('New'):
    #         values['reference'] = self.env['ir.sequence'].next_by_code('university.student.seq') or _('New')
    #     result = super(UniversityStudent, self).create(values)
    #     return result

    @api.model
    def test_cron_job(self):
        print("Abcd")# print will get printed in the log of pycharm
        #code accordingly to execute the cron

    @api.model
    def create(self, values):
        if self.env['res.users'].sudo().search([('login', '=', values.get('e_mail'))]):
            user_id = self.env['res.users'].search([('login', '=', values.get('e_mail'))])
            values.update(student_id=user_id.id)
        else:
            vals_user = {
                'name': values.get('f_name'),
                'login': values.get('e_mail'),
                #'password': values.get('mot_passe'),
                # other required field
            }
            user_id = self.env['res.users'].sudo().create(vals_user)
            values.update(student_id=user_id.id)
        res = super(UniversityStudent, self).create(values)
        return res

    @api.constrains('e_mail')
    def validate_email(self):
        for obj in self:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", obj.e_mail) == None:
                raise ValidationError("Vérifier votre adresse mail  : %s" % obj.e_mail)

        return True

    @api.constrains('phone')
    def check_name(self):
        for rec in self:
            if len(self.phone) != 8:
                raise ValidationError(_('Numéro de tel doit contenir seulement 8 chiffres'))
            if len(self.identity_card) != 8:
                raise ValidationError(_('Numéro  de cin/passeport doit contenir seulement 8 chiffres'))

