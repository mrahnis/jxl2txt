from setuptools import setup, find_packages


# Parse the version from the shapely module
for line in open('jxl2txt/__init__.py', 'r'):
    if line.find("__version__") >= 0:
        version = line.split("=")[1].strip()
        version = version.strip('"')
        version = version.strip("'")
        continue

#open('VERSION.txt', 'wb').write(bytes(version, 'UTF-8'))
with open('VERSION.txt', 'w') as fp:
    fp.write(version)


setup(name='jxl2txt',
	version=version,
	author='Michael Rahnis',
	author_email='michael.rahnis@fandm.edu',
	description='Python library to convert Trimble JobXML files using XSLT',
	url='http://github.com/mrahnis/jxl2txt',
	license='BSD',
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'lxml', 'Click'
	],
	entry_points='''
		[console_scripts]
		jxl2txt=jxl2txt.jxl2txt:cli
	''',
	keywords='survey, conversion',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Topic :: Scientific/Engineering :: GIS'
	]
)

