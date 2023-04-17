import py7zr
with py7zr.SevenZipFile('test.7z', mode='r') as z:
    z.extractall()
