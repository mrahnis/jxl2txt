from setuptools import setup, find_packages
import versioneer


with open("README.rst", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setup(name='jxl2txt',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author='Michael Rahnis',
      author_email='mike@topomatrix.com',
      description='Python library to convert Trimble JobXML files using XSLT',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='http://github.com/mrahnis/jxl2txt',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements,
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
      ])
