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
    show_history = fields.Boolean(string='Show History', compute='_compute_show_history')

    @api.depends('age')
    def _compute_show_history(self):
        for record in self:
            record.show_history = record.age is False or record.age >= 50

    @api.onchange('age')
    def _onchange_age(self):
        if self.age is not False and self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': 'PCR Auto-checked',
                    'message': 'PCR has been automatically checked because age is under 30.',
                }
            }

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

    @api.model_create_multi
    def create(self, vals_list):
        patients = super(Patient, self).create(vals_list)
        Log = self.env['hms.patient.log']
        state_label_map = dict(self._fields['state'].selection)
        for patient in patients:
            Log.create({
                'patient_id': patient.id,
                'created_by': self.env.user.id,
                'date': fields.Datetime.now(),
                'description': f'State changed to {state_label_map.get(patient.state)}',
            })
        return patients

    def write(self, vals):
        if 'state' in vals:
            old_states = {r.id: r.state for r in self}
        result = super(Patient, self).write(vals)
        if 'state' in vals:
            Log = self.env['hms.patient.log']
            new_state = vals['state']
            state_label = dict(self._fields['state'].selection).get(new_state)
            for record in self:
                if old_states.get(record.id) != new_state:
                    Log.create({
                        'patient_id': record.id,
                        'created_by': self.env.user.id,
                        'date': fields.Datetime.now(),
                        'description': f'State changed to {state_label}',
                    })
        return result