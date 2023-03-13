import os
import pathlib

import pkg_resources
from setuptools import find_packages, setup

package_folder_name = 'discount_calculator'
package_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), package_folder_name)


def get_requirements():
    with pathlib.Path('requirements.txt').open() as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


setup(
    name=package_folder_name,
    version='0.1.0',
    description=package_folder_name,
    author='admin',
    packages=find_packages(),
    install_requires=get_requirements(),
    package_data={package_folder_name: []},
)
