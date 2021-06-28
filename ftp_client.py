from ftplib import FTP

ftp = FTP('')
ftp.connect('3jk9901196.qicp.vip',46364)
ftp.login()
#ftp.cwd('directory_name') #replace with your directory
ftp.dir()
#ftp.retrlines('LIST')

def uploadFile():
    filename = 'test.jpg' #replace with your file in your home folder
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    ftp.quit()

def downloadFile():
    filename = 'test.jpg' #replace with your file in the directory ('directory_name')
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()

uploadFile()
#downloadFile()