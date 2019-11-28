"""
  breadcrumbs

  Take an individual HTML file, and modify its contents to insert breadcrumb
  information

  breadcrumbs.process_file(filename), where filename is a file that exists
  
  If the file cannot be modified, throw an error, otherwise return
  nothing silently
"""

def process_file(path):
    """
    """

    modified = False

    print "WOULD modify file"

    if False:

        with file(path, 'w') as f:
            data = f.read()
            # manipulate data
            modified = True

            assert modified
            f.seek(0)
            f.write(data)

    return
