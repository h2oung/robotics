import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'exit_patrol_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wisekhy',
    maintainer_email='wisekhy@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
             'scan_blockage_judge = exit_patrol_robot.scan_blockage_judge:main',
              'inspection_visualizer = exit_patrol_robot.inspection_visualizer:main',        	
              'simple_patrol = exit_patrol_robot.simple_patrol:main',
              'corridor_patrol = exit_patrol_robot.corridor_patrol:main',
         ],	
    },
)
