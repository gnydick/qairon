# import os
# import tarfile
# import tempfile
#
# from flask import Response, send_file
#
# from db import db
# from qairon.models import Deployment, DeploymentConfig
#
#
# class HelmController:
#
#     def genChart(self, dep_id):
#         s = db.session
#         deployment = s.query(Deployment).filter(Deployment.id == dep_id).first()
#         helm_files = list(
#             map(lambda c: c.id, filter(lambda x: x.config_template.id == 'helm_template', deployment.configs)))
#         configs = s.query(DeploymentConfig).filter(DeploymentConfig.id.in_(helm_files)).all()
#         print(configs)
#
#         workdir = tempfile.mkdtemp(dir='/tmp')
#
#         os.chdir(workdir)
#         os.mkdir("templates")
#         tarfilename = (deployment.id + '.tar.gz').replace(':', '.')
#         tf = tarfile.open(name=tarfilename, mode="w:gz")
#         for file in configs:
#             filename = 'templates/' + file.name + '.yaml'
#             helm_file = open(filename, 'w')
#
#             helm_file.write(file.deploymentConfig)
#             helm_file.close()
#             tf.add(filename)
#
#         chartYaml = open("Chart.yaml","w")
#         chartYaml.close()
#         tf.add(chartYaml.name)
#         tf.close()
#
#         return send_file(tf.name, mimetype="application/tar+gz", as_attachment=True)
