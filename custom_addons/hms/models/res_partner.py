from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient')
    vat = fields.Char(required=True)

    @api.constrains('email')
    def _check_email_not_in_patients(self):
        for partner in self:
            if not partner.email:
                continue
            patient = self.env['hms.patient'].search([('email', '=', partner.email)], limit=1)
            if patient:
                raise ValidationError(_('This email already exists in the patient records.'))

    def unlink(self):
        for partner in self:
            if partner.related_patient_id:
                raise UserError(_('You cannot delete a customer linked to a patient.'))
        return super(ResPartner, self).unlink()
