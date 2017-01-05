#---NIKHIL SWAMI--------------------------------------------------------------------------
#---UTA ID : 1000915606-------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# Include the Dropbox SDK libraries
from dropbox import client, rest, session
#-----------------------------------------------------------------------------------------
#including classes and system files
import ConfigParser
import webbrowser
import glob
import sys
import time
import datetime as dt
import os, random, struct
from Crypto.Cipher import AES
#-----------------------------------------------------------------------------------------
#----------------------ENCRPYTION CODE----------------------------------------------------
#The code snippet for Encrpytion may have been taken from the Dropbox website =>
#http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

key= 16
secret = os.urandom(key)

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


#-----------------------------------EOF---------------------------------------------------


#--------------------Reading the config file for the folder-------------------------------
Config = ConfigParser.ConfigParser()

Config.read("config.ini")
dict1 ={}
dict2 ={}
dict3 ={}

for section in Config.sections():
    if section== 'SectionOne':
        options = Config.options(section)
        for option in options:
            dict1[option]= Config.get(section, option)                
    elif section== 'SectionTwo':
        options = Config.options(section)
        for option in options:
            dict2[option]= Config.get(section, option)
    elif section== 'SectionThree':
        options = Config.options(section)
        for option in options:
            dict3[option]= Config.get(section, option)
#------------------------------------EOF--------------------------------------------------

#--------------------App key and Secret from the Dropbox developer website----------------
#--------------------AUthenticating the app code snipet was derived from the site---------
#--------------------https://www.dropbox.com/developers/core/start/python-----------------
APP_KEY = dict1['app_key']
APP_SECRET = dict1['app_secret']
    
#-----------------------------------------------------------------------------------------
    
#-----ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app----------
ACCESS_TYPE = dict1['access_type']
#-----------------------------------------------------------------------------------------

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

request_token = sess.obtain_request_token()

#----------------------- Make the user sign in and authorize this token-------------------
#-----------------Token and session code snipet was derived from the site-----------------
#--------------------https://www.dropbox.com/developers/core/start/python-----------------

url = sess.build_authorize_url(request_token)
print "url:", url
print "Please authorize in the browser. After you're done, press enter."
webbrowser.open_new(url)
raw_input()

# This will fail if the user didn't visit the above URL and hit 'Allow'
access_token = sess.obtain_access_token(request_token)

client = client.DropboxClient(sess)
print "linked account:", client.account_info()

#-----------------------------------------------------------------------------------------

rootdir = dict2['dir_key']
listfiles = []
listofExisting = []

def scan(path):
    while len(listfiles)>0:
        listfiles.pop()
    present = 0
    for singlefile in glob.glob( os.path.join(rootdir, '*') ):
        if os.path.isdir(singlefile):
            scan(singlefile)
        else:
            for item in listofExisting:
                if item == singlefile:
                    present = 1
            if present == 0:
                listofExisting.append(singlefile)
                listfiles.append(singlefile)        

scan(rootdir)
print " files scanning"
#-----------------------------------------------------------------------------------------

#----------------------monitoring the root directory and encrpytion of file types---------


while 1:
    time.sleep(10)
    for files in listfiles:
        shouldencrypt = 0
        extension = os.path.splitext(files)[1]
        for key1,value in dict3.iteritems():
            if value == extension:
                shouldencrypt = 1                
        if shouldencrypt == 1:
            out = os.path.basename(files) + '.nks'
            encrypt_file(secret,files,out)
            fh = open(out, 'rb')
            response = client.put_file(out, fh)
            fh.close()
            os.remove(out)
        elif shouldencrypt == 0:
            fh = open(files, 'rb')
            response = client.put_file(os.path.basename(files), fh)
            fh.close()
    while len(listfiles)>0:
        listfiles.pop()

    scan(rootdir)
#-----------------------------------------------------------------------------------------

