from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'camera_opencv'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'data'), glob('camera_opencv/data/*')),
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
            "img_show = camera_opencv.img_show:main",
            "img_pub = camera_opencv.img_pub:main",
            "img_sub = camera_opencv.img_sub:main",
            "img_compressed_pub = camera_opencv.img_compressed_pub:main",
            "img_compressed_sub = camera_opencv.img_compressed_sub:main",
            "camera_pub = camera_opencv.camera_pub:main",
            "circle_follow = camera_opencv.circle_follow:main",
            "event_draw = camera_opencv.event_draw:main",
            "find_redball = camera_opencv.find_redball:main",
            "tracking_redball = camera_opencv.tracking_redball:main",
            "aruco_tracker = camera_opencv.aruco_tracker:main",
            "camera_Canny = camera_opencv.camera_Canny:main",
            "match_orb = camera_opencv.match_orb:main",
            "camera_yolo = camera_opencv.camera_yolo:main",
        ],
    },
)
