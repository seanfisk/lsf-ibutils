""":mod:`lsf_ibutils.metadata` --- Project metadata

Information describing the project.
"""

# The package name, which is also the "UNIX name" for the project.
package = 'lsf_ibutils'
project = "LSF Interactive Batch Utilities"
project_no_spaces = project.replace(' ', '')
version = '0.1'
description = (
    'Interactive interfaces for manipulating batch jobs in Platform LSF')
authors = ['Davide Del Vento', 'Sean Fisk']
authors_string = ', '.join(authors)
emails = ['davidedelvento@gmail', 'sean@seanfisk.com']
license = 'MIT'
copyright = '2013 ' + authors_string
url = 'http://github.com/seanfisk'
