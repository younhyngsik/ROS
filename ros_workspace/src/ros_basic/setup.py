from glob import glob
import os
from setuptools import find_packages, setup


package_name = 'ros_basic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch','*.launch.py')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='youn',
    maintainer_email='younhyngsik@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "simple_pub = ros_basic.simple_pub:main",
            "class_pub = ros_basic.class_pub:main",
            "class_sub = ros_basic.class_sub:main",
            "class2_sub = ros_basic.class2_sub:main",
            "time_pub = ros_basic.time_pub:main",
            "time_sub = ros_basic.time_sub:main",
            "mv_turtle = ros_basic.mv_turtle:main",
            "mv_turtle_ns = ros_basic.mv_turtle_ns:main",
            "qos_test_pub = ros_basic.qos_test_pub:main",
            "qos_test_sub = ros_basic.qos_test_sub:main",
            "user_int_pub = ros_basic.user_int_pub:main",
            "service_server = ros_basic.service_server:main",
            "service_thread_server = ros_basic.service_thread_server:main",
            "service_client = ros_basic.service_client:main",
            "my_param = ros_basic.my_param:main",
            "param_async = ros_basic.param_async:main",
            "action_server = ros_basic.action_server:main",
            "action_client = ros_basic.action_client:main",
            "action_thread_server = ros_basic.action_thread_server:main",
        ],
    },
)
