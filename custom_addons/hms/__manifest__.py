{
    'name': 'Hospital Management System',
    'version': '1.0',
    'summary': 'Manage patients in a hospital',
    'category': 'Healthcare',
    'author': 'hms',
    'depends': ['base'],
    'data': [
      'security/ir.model.access.csv', 
      'views/department_views.xml',
      'views/doctors_views.xml',
      'views/patient_views.xml',
      'views/res_partner_views.xml'
    ],
    'installable': True,
    'application': True,
}