#!/usr/bin/python3

# import modules
import sys, os, pathlib, shutil, smtplib
from datetime import datetime

class EmailConfig(object):
    '''
    Individual Email configuration details.
    '''

    def __init__(self, *args):
        '''
        class EmailConfig constructor

        Set class attributes to initial values.

        Parameters:
            args[0]: email address of recipient
            args[1]: email address of user
            args[2]: pwd
            args[3]: server
            args[4]: port
        '''
        
        self.recipient  = args[0] 
        self.user = args[1] 
        self.pwd = args[2] 
        self.server = args[3]
        self.port = args[4] 

class Job(object):
    '''
    Individual job details.
    '''

    def __init__(self, *args):
        '''
        class Job constructor

        Set class attributes to initial values.

        Parameters:
            args[0]: job name
            args[1]: source file or directory
            args[2]: destination directory
        '''

        self.name = args[0]
        self.src = args[1]
        self.dst = args[2]

        self.errors = 0
        self.message = []
        self.datestring = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Determine type of backup job
        self.is_file_job = pathlib.Path(self.src).is_file()
        self.is_dir_job = pathlib.Path(self.src).is_dir()

        # Check job source and destination paths exist
        if not os.path.exists(self.src):
            self.message.append("Source " + self.src + " does not exist -> FAIL")
            self.errors += 1

        if not os.path.exists(self.dst):
            self.message.append("Destination directory " + self.dst + " does not exist -> FAIL")
            self.errors += 1

    def __eq__(self, other):
        '''
        Return:
            True when other is name
        '''

        return other == self.name

    def do_logfile(self, logfile):
        '''
        Output all log messages to logfile.
        '''

        file = open(logfile, "a")
        for msg in self.message:
            logmsg = self.datestring + " " + self.name + " " + msg
            file.write(logmsg + "\n")
        file.close()

    def do_email(self, email_config):
        '''
        Output all log message as email.
        '''
        
        header = 'To: ' + email_config.recipient + '\n' + 'From: ' + email_config.user + '\n' + 'Subject: Backup Error ' + self.name + '\n'
        msg = header + '\n'
        
        for item in self.message:
            msg = msg + item + '\n'
        msg = msg + '\n\n'

        smtpserver = smtplib.SMTP(email_config.server, email_config.port)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.login(email_config.user, email_config.pwd)
        smtpserver.sendmail(email_config.user, email_config.recipient, msg)
        smtpserver.quit()

    def do_backup(self, backup):
        '''
        Backup file system object to destination.
        '''

        # Construct source and destination paths
        src_path = pathlib.Path(self.src)
        src_path_only = pathlib.PurePath(self.src)
        self.dst_path = self.dst + "/" + src_path_only.name + "-" + self.datestring

        # Copy file system object to destination
        backup.do_backup(self)

class Backup(object):
    '''
    Backup a file system object.
    '''

class BackupFile(Backup):
    '''
    Backup a file system file.
    '''

    def do_backup(self, job):
        '''
        Backup source file to destination.
        '''

        # Copy source file to destination
        try:
            shutil.copy2(job.src, job.dst_path)
            job.message.append("Backup of file " + job.src + " -> SUCCEED")
        except:
            job.message.append("Backup of file " + job.src + " -> FAIL")
            job.errors += 1

class BackupDirectory(Backup):
    '''
    Backup a file system directory.
    '''

    def do_backup(self, job):
        '''
        Backup source directory to destination.
        '''

        # Copy source directory to destination
        try:
            shutil.copytree(job.src, job.dst_path)
            job.message.append("Backup of directory " + job.src + " -> SUCCEED")
        except:
            job.message.append("Backup of directory " + job.src + " -> FAIL")
            job.errors += 1
    
def main():
    '''
    Execute backup job from job list with a name matching the first command line argument.
    '''

    email_config = EmailConfig('dcleary@sunitafe.edu.au',
                               'dcleary@sunitafe.edu.au',
                               'xxxxxxxx',
                               'mail.example.com',
                               587)

    jobs = [Job('job1', '/home/ec2-user/environment/backupoo/test/dir1', '/home/ec2-user/environment/backupoo/backup'),
            Job('job2', '/home/ec2-user/environment/backupoo/test/file1','/home/ec2-user/environment/backupoo/backup'),
            Job('job3', '/home/ec2-user/environment/backupoo/test/fileX','/home/ec2-user/environment/backupoo/backup'),
            Job('job4', '/home/ec2-user/environment/backupoo/test/file1','/home/ec2-user/environment/backupoo/backupX')]

    usage_msg = 'Usage: python backup.py <job_name>'
    
    job_msg = 'Invalid job number.  Job number not in list of jobs.'
    
    logfile = '/home/ec2-user/environment/backupoo/backupoo.log'

    # Check correct number of command line arguments
    if len(sys.argv) != 2:

        print(usage_msg)

    else:

        # If job number from command line in jobs list then perform backup job
        job_name = sys.argv[1]

        if job_name not in jobs:

            print(job_msg)

        else:

            job = jobs[jobs.index(job_name)]


            # determine the job type
            if job.is_file_job:
                backup = BackupFile()

            elif job.is_dir_job:

                backup = BackupDirectory()

            # perform backup
            if not job.errors:
                job.do_backup(backup)

            # send errors as email
            if job.errors:
                pass
                # job.do_email(email_config)

            # record result in logfile
            job.do_logfile(logfile)

if __name__ == '__main__':
    main()

