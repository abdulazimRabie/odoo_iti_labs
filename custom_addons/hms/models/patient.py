from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'HMS Patient'

    first_name    = fields.Char(string='First Name', required=True)
    last_name     = fields.Char(string='Last Name',  required=True)
    birth_date    = fields.Date(string='Birth Date')
    age           = fields.Integer(string='Age')
    address       = fields.Text(string='Address')
    image         = fields.Image(string='Patient Image')

    history       = fields.Html(string='Medical History')
    cr_ratio      = fields.Float(string='CR Ratio')
    pcr           = fields.Boolean(string='PCR')
    blood_type    = fields.Selection(
        selection=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        string='Blood Type'
    )

    state = fields.Selection(
        selection=[
            ('undetermined', 'Undetermined'),
            ('good',         'Good'),
            ('fair',         'Fair'),
            ('serious',      'Serious'),
        ],
        string='State',
        default='undetermined'
    )

    department_id  = fields.Many2one('hms.department', string='Department')
    capacity       = fields.Integer(string='Department Capacity',
                                     related='department_id.capacity',
                                     readonly=True)
    doctor_ids     = fields.Many2many('hms.doctors', string='Doctors')

    log_ids = fields.One2many('hms.patient.log', 'patient_id', string='Log History')

    @api.onchange('age')
    def _onchange_age(self):
        if self.age and self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': 'PCR Auto-checked',
                    'message': 'PCR has been automatically checked because age is under 30.',
                }
            }

    @api.onchange('state')
    def _onchange_state(self):
        if self.state:
            self.log_ids = [(0, 0, {
                'created_by': self.env.user.id,
                'date': fields.Datetime.now(),
                'description': f'State changed to {dict(self._fields["state"].selection).get(self.state)}',
            })]

    @api.constrains('pcr', 'cr_ratio')
    def _check_cr_ratio(self):
        for record in self:
            if record.pcr and not record.cr_ratio:
                raise ValidationError('CR Ratio is required when PCR is checked.')

    @api.constrains('department_id')
    def _check_department_open(self):
        for record in self:
            if record.department_id and not record.department_id.is_opened:
                raise ValidationError('You cannot assign a patient to a closed department.')