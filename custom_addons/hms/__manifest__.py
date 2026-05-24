{
    'name': 'Hospital Management System',
    'version': '1.0',
    'summary': 'Manage patients in a hospital',
    'category': 'Healthcare',
    'author': 'hms',
    'depends': ['base'],
    'data': [
      'security/ir.model.access.csv', 
      'views/patient_views.xml',
    ],
    'installable': True,
    'application': True,
}