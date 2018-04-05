from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('python.pycharm')


name = "booking"
default_task = ['clean', "publish"]


@init
def set_properties(project):
    project.version = '0.1'
    project.depends_on_requirements('requirements.txt')
    project.include_file('booking', 'fonts/courier-bold.ttf')
    project.include_file('booking', 'fonts/times-bold.ttf')
