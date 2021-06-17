#!/usr/bin/python3
#
# ---------------------------------------------------------------------------
# - 20210426 - baculabackupreport.py v1.0 - Initial release
# ---------------------------------------------------------------------------
#
# This is is my first foray into Python. Please be nice :)
#
# This script is a rewrite/port from my original baculabackupreport.sh script
# which was something that started out as a simple bash script which just
# sent a basic text email about recent Bacula jobs.
#
# Over time, and with a lot of requests, and great ideas, the script grew
# into a giant, unmaintainable mashup/combination of bash & awk.
#
# I always knew it would need to be rewritten in something like Python, so
# 1.5 years ago I started the parallel tasks of beginning to learn Python,
# while porting the original script. I made some pretty good progress
# relatively quickly, but then I gave up - Until this past week when I
# picked it up again.
#
# What follows is version 1.0 of my efforts. Is it pretty? No. Did I follow
# proper python coding conventions? I think that is also a big No. Does it
# produce a nice HTML email showing a lot of valuable information to a backup
# administrator? I say YES! Would I appreciate feedback? YES!
#
# ---------------------------------------------------------------------------
# BSD 2-Clause License
#
# Copyright (c) 2021, William A. Arlofski waa@revpol.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1.  Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

# Toggles and other formatting settings
# -------------------------------------
centerjobname = 'yes'               # Center the Job Name in HTML emails?
centerclientname = 'yes'            # Center the Client Name in HTML emails?
boldjobname = 'yes'                 # Bold the Job Name in HTML emails?
boldstatus = 'yes'                  # Bold the Status in HTML emails?
emailsummary = 'yes'                # Print a short summary after the Job list table? (Total Jobs, Files, Bytes, etc)
emailjobsummaries = 'no'            # Email all Job summaries? Be careful with this, it can generate very large emails
emailbadlogs = 'no'                 # Email logs of bad Jobs? Be careful with this, it can generate very large emails.
addsubjecticon = 'yes'              # Prepend the email Subject with UTF-8 icons? See (no|good|warn|bad)jobsicon variables below
addsubjectrunningorcreated = 'yes'  # Append "(## Jobs still runnning/queued)" to Subject if running or queued Jobs > 0?
starbadjobids = 'no'                # Wrap bad Jobs jobids with asterisks "*"?
sortfield = 'JobId'                 # Which catalog DB field to sort on? hint: multiple,fields,work,here
sortorder = 'DESC'                  # Which direction to sort?

# Set some utf-8 icon to prepend the subject with
# https://www.utf8-chartable.de/unicode-utf8-table.pl
# ---------------------------------------------------
nojobsicon = '=?utf-8?Q?=F0=9F=9A=AB?='      # utf-8 'no entry sign' subject icon when no Jobs have been run
goodjobsicon = '=?utf-8?Q?=F0=9F=9F=A9?='    # utf-8 'green square' subject icon when there are Jobs with errors etc
# goodjobsicon = '=?UTF-8?Q?=E2=9C=85?='     # utf-8 'white checkmark in green box' subject icon when all Jobs were "OK"
# goodjobsicon = '=?UTF-8?Q?=E2=98=BA?='     # utf-8 'smiley face' subject icon when all Jobs were "OK"
warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A7?='    # utf-8 'orange square' subject icon when all jobs are "OK", but some have errors/warnings
# warnjobsicon = '=?UTF-8?Q?=F0=9F=9F=A8?='  # utf-8 'yellow square' subject icon when all jobs are "OK", but some have errors/warnings
badjobsicon = '=?utf-8?Q?=F0=9F=9F=A5?='     # utf-8 'red square' subject icon when there are Jobs with errors etc
# badjobsicon = '=?utf-8?Q?=E2=9B=94?='      # utf-8 'red circle with white hypehn' subject icon when there are Jobs with errors etc
# badjobsicon = '=?utf-8?Q?=E2=9C=96?='      # utf-8 'black bold X' subject icon when there are Jobs with errors etc
# badjobsicon = '=?utf-8?Q?=E2=9D=8C?='      # utf-8 'red X' subject icon when there are Jobs with errors etc
# badjobsicon = '=?utf-8?Q?=E2=9D=97?='      # utf-8 'red !' subject icon when there are Jobs with errors etc
# badjobsicon = '=?utf-8?Q?=E2=98=B9?='      # utf-8 'sad face' subject icon when there are Jobs with errors etc

# Set the columns to display and their order
# ------------------------------------------
cols2show = 'jobid jobname client status joberrors type level jobfiles jobbytes starttime endtime runtime'
# cols2show = 'jobid jobname client status joberrors type level jobfiles jobbytes endtime runtime'
# cols2show = 'jobid jobname status joberrors type level jobfiles jobbytes endtime runtime'
# cols2show = 'jobname jobid client status joberrors type level jobfiles jobbytes starttime runtime'
# cols2show = 'jobname jobid status type level jobfiles jobbytes starttime runtime'
# cols2show = 'status jobid jobname starttime endtime runtime'

# Set the column to colorize for jobs that are always failing
# -----------------------------------------------------------
alwaysfailcolumn = 'jobname'  # Column to colorize for "always failing jobs" - column name, row, none

# HTML colors
# -----------
colorstatusbg = 'yes'            # Colorize the Status cell's background?
jobtablerowcolor = '#d4d4d4'     # Background color for the job rows in the HTML table
jobtableheadercolor = '#b0b0b0'  # Background color for the HTML table's header
runningjobcolor = '#4d79ff'      # Background color of the Status cell for "Running" jobs
createdjobcolor = '#add8e6'      # Background color of the Status cell for "Created, but not yet running" jobs
goodjobcolor = '#00f000'         # Background color of the Status cell for "OK" jobs
badjobcolor = '#cc3300'          # Background color of the Status cell for "Bad" jobs
warnjobcolor = '#ffc800'         # Background color of the Status cell for "Backup OK -- with warnings" jobs
errorjobcolor = '#cc3300'        # Background color of the Status cell for jobs with errors
alwaysfailcolor = '#ebd32a'      # Background color of the entire row for "always failing in the past 'days' days" jobs

# HTML fonts
# ----------
fontfamily = 'Verdana, Arial, Helvetica, sans-serif'  # Font family to use for HTML emails
fontsize = '16px'         # Font size to use for email title (title removed from email for now)
fontsizejobinfo = '12px'  # Font size to use for job information inside of table
fontsizesumlog = '10px'   # Font size of job summaries and bad job logs

# --------------------------------------------------
# Nothing should need to be modified below this line
# --------------------------------------------------

# Import the required modules
# ---------------------------
import os
import re
import sys
import smtplib
from docopt import docopt
from socket import gaierror

# Set some variables
# ------------------
progname='Bacula Backup Report'
version = '1.9.9'
reldate = 'June 17, 2021'
prog_info = '<p style="font-size: 8px;">' \
          + progname + ' - v' + version \
          + ' - baculabackupreport.py<br>' \
          + 'By: Bill Arlofski waa@revpol.com (c) ' \
          + reldate + '</body></html>'
badjobset = {'A', 'D', 'E', 'f', 'I'}
valid_db_lst = ['pgsql', 'mysql', 'maria']
valid_col_lst = [
    'jobid', 'jobname', 'client', 'status',
    'joberrors', 'type', 'level', 'jobfiles',
    'jobbytes', 'starttime', 'endtime', 'runtime'
    ]

# Create a dictionary of column name to html strings
# so that they may be used in any order in the jobs table
# -------------------------------------------------------
col_hdr_dict = {
    'jobid':     '<td align="center"><b>Job ID</b></td>',
    'jobname':   '<td align="center"><b>Job Name</b></td>',
    'client':    '<td align="center"><b>Client</b></td>',
    'status':    '<td align="center"><b>Status</b></td>',
    'joberrors': '<td align="center"><b>Errors</b></td>',
    'type':      '<td align="center"><b>Type</b></td>',
    'level':     '<td align="center"><b>Level</b></td>',
    'jobfiles':  '<td align="center"><b>Files</b></td>',
    'jobbytes':  '<td align="center"><b>Bytes</b></td>',
    'starttime': '<td align="center"><b>Start Time</b></td>',
    'endtime':   '<td align="center"><b>End Time</b></td>',
    'runtime':   '<td align="center"><b>Run Time</b></td>'
    }

def usage():
    'Show the instructions'
    print(doc_str)
    sys.exit(1)

def cli_vs_env_vs_default_vars(var_name, env_name):
    'Assign/re-assign args[] vars based on if they came from cli, env, or defaults.'
    if var_name in sys.argv:
        if args['--dbname'] == '':
            print(print_opt_errors('dbname'))
            usage()
        else:
            return args[var_name]
    elif env_name in os.environ and os.environ[env_name] != '':
        return os.environ[env_name]
    else:
        return args[var_name]

def print_opt_errors(opt):
    'Print the command line option passed and the reason it is incorrect.'
    if opt in {'server', 'dbname', 'dbhost', 'dbuser', 'smtpserver'}:
        return '\nThe \'' + opt + '\' variable must not be empty.'
    elif opt in {'time', 'days', 'smtpport', 'dbport'}:
        return '\nThe \'' + opt + '\' variable must not be empty and must be an integer.'
    elif opt in {'email', 'fromemail'}:
        return '\nThe \'' + opt + '\' variable is either empty or it does not look like a valid email address.'
    elif opt == 'dbtype':
        return '\nThe \'' + opt + '\' variable must not be empty, and must be one of: ' + ', '.join(valid_db_lst)

def db_connect():
    'Connect to the db using the appropriate database connector and create the right cursor'
    global conn, cur
    if dbtype == 'pgsql':
        conn = psycopg2.connect(host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    elif dbtype in ('mysql', 'maria'):
        conn = mysql.connector.connect(host=dbhost, port=dbport, database=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor(dictionary=True)

def pn_job_id(ctrl_jobid, p_or_n):
    'Return a Previous or New jobid for Copy and Migration Control jobs.'
    # Given a Copy Ctrl or Migration Ctrl job's jobid, perform a re.sub()
    # on the joblog's job summary block of 20+ lines of text using a search
    # term of 'Prev' or 'New' as 'p_or_n' and return the previous or new jobid
    # ------------------------------------------------------------------------
    return re.sub('.*' + p_or_n + ' Backup JobId: +(.+?)\n.*', '\\1', ctrl_jobid['logtext'], flags = re.DOTALL)

def v_job_id(vrfy_jobid):
    'Return a "Verify JobId" for Verify jobs.'
    # Given a Verify job's jobid, perform a re.sub on the joblog's
    # job summary block of 20+ lines of text using a search term of
    # 'Verify JobId:' and return the jobid of the job it verified
    # -------------------------------------------------------------
    return re.sub('.*Verify JobId: +(.+?)\n.*', '\\1', vrfy_jobid['logtext'], flags = re.DOTALL)

def migrated_id(jobid):
    'For a given Migrated job, return the jobid that it was migrated to.'
    for t in pn_jobids:
        if pn_jobids[t][0] == str(jobid):
            return pn_jobids[t][1]

def translate_job_type(jobtype, jobid, priorjobid, jobstatus):
    'Job type is stored in the catalog as a single character. Do some special things for Copy and Migration jobs.'
    if jobtype == 'C' and priorjobid != '0':
        return 'Copy of ' + str(priorjobid)

    if jobtype == 'B' and priorjobid != 0:
        return 'Migrated from ' + str(priorjobid)

    if jobtype == 'M':
        # Part of this is a workaround for what I consider to be a bug in Bacula for jobs of
        # type 'B' which meet the criteria to be 'eligible' for migration, but have 0 files/bytes
        # The original backup Job's type gets changed from 'B' (Backup) to 'M' (Migrated), even
        # though nothing is migrated. https://bugs.bacula.org/view.php?id=2619
        # ---------------------------------------------------------------------------------------
        if 'pn_jobids' in globals() and migrated_id(jobid) != '0':
            return 'Migrated to ' + migrated_id(jobid)
        elif 'pn_jobids' in globals() and migrated_id(jobid) == '0':
            return 'Nothing to migrate'
        else:
            return 'Migrated'

    if jobtype == 'c':
        if jobstatus in ('R', 'C'):
            return 'Copy Ctrl'
        if jobstatus in badjobset:
            return 'Copy Ctrl: Failed'
        if '0' in pn_jobids[str(jobid)]:
            # This covers when the 'main' copy control job finds no eligable
            # jobs to copy at all both 'Prev JobId' and 'Next JobId' are '0'
            if pn_jobids[str(jobid)][0] == '0':
                return 'Copy Ctrl: No jobs to copy'
            else:
                return 'Copy Ctrl: ' + pn_jobids[str(jobid)][0] + '->No files to copy'
        else:
            return 'Copy Ctrl: ' + pn_jobids[str(jobid)][0] + '->' + pn_jobids[str(jobid)][1]

    if jobtype == 'g':
        if jobstatus in ('R', 'C'):
            return 'Migration Ctrl'
        if jobstatus in badjobset:
            return 'Migration Ctrl: Failed'
        if '0' in pn_jobids[str(jobid)]:
            return 'Migration Ctrl: No jobs to migrate'
        else:
            return 'Migration Ctrl: ' + pn_jobids[str(jobid)][0] + '->' + pn_jobids[str(jobid)][1]

    if jobtype == 'V':
        if '0' in v_jobids[str(jobid)]:
            return 'Verify: No job to verify'
        else:
            return 'Verify of ' + v_jobids[str(jobid)]

    return {'B': 'Backup', 'D': 'Admin', 'R': 'Restore'}[jobtype]

def translate_job_status(jobstatus, joberrors):
    'jobstatus is stored in the catalog as a single character, replace with words.'
    return {'A': 'Aborted', 'C': 'Created', 'D': 'Verify Diffs',
            'E': 'Errors', 'f': 'Failed', 'I': 'Incomplete',
            'R': 'Running', 'T': ('-OK-', 'OK/Warnings')[joberrors > 0]}[jobstatus]

def set_subject_icon():
    'Set the utf-8 subject icon.'
    if numjobs == 0:
        subjecticon = nojobsicon
    else:
        if numbadjobs != 0:
           subjecticon = badjobsicon
        elif jobswitherrors != 0:
           subjecticon = warnjobsicon
        else:
            subjecticon = goodjobsicon
    return subjecticon

def translate_job_level(joblevel, jobtype):
    'Job level is stored in the catalog as a single character, replace with a string.'
    # No real level for these job types
    # ---------------------------------
    if jobtype in ('D', 'R', 'g', 'c'):
        return '----'
    return {' ': '----', '-': 'Base', 'A': 'VVol', 'C': 'VCat', 'd': 'VD2C',
            'D': 'Diff', 'f': 'VFul', 'F': 'Full', 'I': 'Incr', 'O': 'VV2C', 'V': 'Init'}[joblevel]

def html_format_cell(content, bgcolor = '', star = '', col = '', jobstatus = '', jobtype = ''):
    'Format/modify some table cells based on settings and conditions.'
    # Set default tdo and tdc to wrap each cell
    # -----------------------------------------
    tdo = '<td align="center">'
    tdc = '</td>'

    # Colorize the Status cell?
    # Even if yes, don't override the table
    # row bgcolor if alwaysfailcolumn is 'row'
    # ----------------------------------------
    if not (alwaysfail == 'yes' and alwaysfailcolumn == 'row'):
        if colorstatusbg == 'yes' and col == 'status':
            if jobrow['jobstatus'] == 'C':
                bgcolor = createdjobcolor
            elif jobrow['jobstatus'] == 'E':
                bgcolor = errorjobcolor
            elif jobrow['jobstatus'] == 'T':
                if jobrow['joberrors'] == 0:
                    bgcolor = goodjobcolor
                else:
                    bgcolor = warnjobcolor
            elif jobrow['jobstatus'] in badjobset:
                bgcolor = badjobcolor
            elif jobrow['jobstatus'] == 'R':
                bgcolor = runningjobcolor
            elif jobrow['jobstatus'] == 'I':
                bgcolor = warnjobcolor
        tdo = '<td align="center" bgcolor="' + bgcolor + '">'

    if alwaysfail == 'yes' and col == alwaysfailcolumn:
        tdo = '<td align="center" bgcolor="' + alwaysfailcolor + '">'

    # Center the Client name and Job name?
    # -------------------------------------
    if col == 'jobname' and centerjobname != 'yes':
        tdo = '<td align="left">'
    if col == 'client' and centerclientname != 'yes':
        tdo = '<td align="left">'

    # Set the Job name and Status cells bold?
    # ---------------------------------------
    if col == 'jobname' and boldjobname == 'yes':
        tdo += '<b>'
        tdc = '</b>' + tdc
    if col == 'status' and boldstatus == 'yes':
        tdo += '<b>'
        tdc = '</b>' + tdc

    # Some specific modifications for Running or Created Jobs,
    # or special Jobs (Copy/Migration/Admin/etc) where no real
    # client is used, or when the Job is still running, there
    # will be no endtime, nor runtime
    # --------------------------------------------------------
    if content == '----' or ((col == 'client' or col == 'runtime') and content == 'None'):
        content = '<hr width="20%">'
    if content == 'None' and col == 'endtime' and jobstatus == 'R':
        content = 'Still Running'
    if jobstatus == 'C' and col == 'endtime':
        content = 'Created, not yet running'

    # Jobs with status: Created, Running ('C', 'R'), or
    # Jobs with type: Admin, Copy Ctrl, Migration Ctrl
    # ('D', 'c, 'g') will never have a value for jobfiles
    # nor jobbytes in the db, so we set them to a 20% hr
    # ---------------------------------------------------
    if (jobstatus in ('R', 'C') or jobtype in ('D', 'c', 'g')) and col in ('jobfiles', 'jobbytes'):
        content = '<hr width="20%">'

    # Return the wrapped and modified cell content
    # --------------------------------------------
    return tdo + star + content + star + tdc

def humanbytes(B):
    'Return the given bytes as a human friendly string.'
    # Thank you 'whereisalext' :)
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/31631711#31631711
    # -------------------------------------------------------------------------------------------------------------------------
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776
    PB = float(KB ** 5) # 1,125,899,906,842,624

    if B < KB:
       return '{0:.2f}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
       return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
       return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
       return '{0:.2f} GB'.format(B/GB)
    elif TB <= B < PB:
       return '{0:.2f} TB'.format(B/TB)
    elif PB <= B:
       return '{0:.2f} PB'.format(B/PB)

def send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport):
    'Send the email.'
    # Thank you to Aleksandr Varnin for this short and simple to implement solution
    # https://blog.mailtrap.io/sending-emails-in-python-tutorial-with-code-examples
    # -----------------------------------------------------------------------------
    message = f"""Content-Type: text/html\nMIME-Version: 1.0\nTo: {email}\nFrom: {fromemail}\nSubject: {subject}\n\n{msg}"""
    try:
        with smtplib.SMTP(smtpserver, smtpport) as server:
            if smtpuser != '' and smtppass != '':
                server.login(smtpuser, smtppass)
            server.sendmail(fromemail, email, message)
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
        sys.exit(1)
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
        sys.exit(1)
    except smtplib.SMTPException as e:
        print('Error occurred while communicating with SMTP server ' + smtpserver + ':' + str(smtpport))
        print('Error was: ' + str(e))
        sys.exit(1)

# def add_cp_mg_to_alljobids(copymigratejobids):
#     'For each Copy/Migration Ctrl jobid (c,g), find the job it copied/migrated, and append it to the alljobids list'
# TODO - See notes. This feature will be for jobs that have been
#        copied/migrated, but their original, inherited 'endtime'
#        is older than the 'time' hours we initially queried for
# ---------------------------------------------------------------

doc_str = """
Usage:
    baculabackupreport.py [-e <email>] [-f <fromemail>] [-s <server>] [-t <time>] [-d <days>] [-c <client>] [-j <jobname>]
                          [--dbtype <dbtype>] [--dbport <dbport>] [--dbhost <dbhost>] [--dbname <dbname>]
                          [--dbuser <dbuser>] [--dbpass <dbpass>]
                          [--smtpserver <smtpserver>] [--smtpport <smtpport>] [-u <smtpuser>] [-p <smtppass>]
    baculabackupreport.py -h | --help
    baculabackupreport.py -v | --version

Options:
    -e, --email <email>               Email address to send report to
    -f, --fromemail <fromemail>       Email address to be set in the From: field of the email
    -s, --server <server>             Name of the Bacula Server [default: Bacula]
    -t, --time <time>                 Time to report on in hours [default: 24]
    -d, --days <days>                 Days to check for "Always failing jobs" [default: 7]
    -c, --client <client>             Client to report on using SQL 'LIKE client' [default: %] (all clients)
    -j, --jobname <jobname>           Job name to report on using SQL 'LIKE jobname' [default: %] (all jobs)
    --dbtype (pgsql | mysql | maria)  Database type [default: pgsql]
    --dbport <dbport>                 Database port (defaults pgsql 5432, mysql & maria 3306)
    --dbhost <dbhost>                 Database host [default: localhost]
    --dbname <dbname>                 Database name [default: bacula]
    --dbuser <dbuser>                 Database user [default: bacula]
    --dbpass <dbpass>                 Database password
    --smtpserver <smtpserver>         SMTP server [default: localhost]
    --smtpport <smtpport>             SMTP port [default: 25]
    -u, --smtpuser <smtpuser>         SMTP user
    -p, --smtppass <smtppass>         SMTP password

    -h, --help                        Print this help message
    -v, --version                     Print the script name and version

Notes:
* Only the email variable is required. It must be set on the command line or via an environment variable
* Each '--varname' may instead be set using all caps environment variable names like: EMAIL="admin@example.com"
* Variable assignment precedence is: command line > environment variable > default

"""

# Assign command line variables using docopt
# ------------------------------------------
args = docopt(doc_str, version='\n' + progname + ' - v' + version + '\n' + reldate + '\n')

# Verify that the columns in cols2show are
# all valid and that the alwaysfailcolumn
# is also valid before we do anything else
# ----------------------------------------
c2sl = cols2show.split()
if not all(item in valid_col_lst for item in c2sl):
    print('\nThe \'cols2show\' variable is not valid!\n')
    print('Current \'cols2show\': ' + cols2show)
    print('Valid columns are: ' + ' '.join(valid_col_lst))
    usage()

if (alwaysfailcolumn not in c2sl or alwaysfailcolumn not in valid_col_lst) and alwaysfailcolumn not in ('row', 'none'):
    print('\n\'alwaysfailcolumn\' name \'' + alwaysfailcolumn + '\' not valid or not in cols2show.')
    print('\nValid settings for \'alwaysfailcolumn\' are: ' + ' '.join(valid_col_lst) + ' none row')
    print('\nWith current \'cols2show\' setting, valid settings for \'alwaysfailcolumn\' are: ' + cols2show + ' none row')
    usage()
elif alwaysfailcolumn == 'row':
    alwaysfailcolumn_str = 'entire row'
else:
    if alwaysfailcolumn == 'joberrors':
        alwaysfailcolumn_str = 'errors column'
    elif alwaysfailcolumn == 'jobfiles':
        alwaysfailcolumn_str = 'files column'
    elif alwaysfailcolumn == 'jobbytes':
        alwaysfailcolumn_str = 'bytes column'
    else:
        alwaysfailcolumn_str = alwaysfailcolumn + ' column'

# Set the default ports for the different databases if not set on command line
# ----------------------------------------------------------------------------
if args['--dbtype'] == 'pgsql' and args['--dbport'] == None:
    args['--dbport'] = '5432'
elif args['--dbtype'] in ('mysql', 'maria') and args['--dbport'] == None:
    args['--dbport'] = '3306'
elif args['--dbtype'] not in valid_db_lst:
    print(print_opt_errors('dbtype'))
    usage()

# Need to assign/re-assign args[] vars based on cli vs env vs defaults
# --------------------------------------------------------------------
for ced_tup in [
    ('--time', 'TIME'), ('--days', 'DAYS'), ('--email', 'EMAIL'),
    ('--client', 'CLIENT'), ('--server', 'SERVER'),
    ('--dbtype', 'DBTYPE'), ('--dbport', 'DBPORT'),
    ('--dbhost', 'DBHOST'), ('--dbname', 'DBNAME'),
    ('--dbuser', 'DBUSER'), ('--dbpass', 'DBPASS'),
    ('--jobname', 'JOBNAME'), ('--smtpport', 'SMTPPORT'),
    ('--smtpuser', 'SMTPUSER'), ('--smtppass', 'SMTPPASS'),
    ('--fromemail', 'FROMEMAIL'), ('--smtpserver', 'SMTPSERVER')
    ]:
    args[ced_tup[0]] = cli_vs_env_vs_default_vars(ced_tup[0], ced_tup[1])

# Do some basic sanity checking on variables
# ------------------------------------------
if args['--email'] is None or '@' not in args['--email']:
    print(print_opt_errors('email'))
    usage()
else:
    email = args['--email']
if args['--fromemail'] == None:
    fromemail = email
elif '@' not in args['--fromemail']:
    print(print_opt_errors('fromemail'))
    usage()
else:
    fromemail = args['--fromemail']
if not args['--time'].isnumeric():
    print(print_opt_errors('time'))
    usage()
else:
    time = args['--time']
if not args['--days'].isnumeric():
    print(print_opt_errors('days'))
    usage()
else:
    days = args['--days']
if not args['--smtpport'].isnumeric():
    print(print_opt_errors('smtpport'))
    usage()
else:
    smtpport = args['--smtpport']
if not args['--server']:
    print(print_opt_errors('server'))
    usage()
else:
    server = args['--server']
# dbtype is already tested and
# verified above, just assign
# and check the type to assign
# correct connector and cursor
# ----------------------------
dbtype = args['--dbtype']
if dbtype == 'pgsql':
    import psycopg2
    import psycopg2.extras
elif dbtype in ('mysql', 'maria'):
    import mysql.connector
if not args['--dbport'].isnumeric():
    print(print_opt_errors('dbport'))
    usage()
else:
    dbport = args['--dbport']
if not args['--dbname']:
    print(print_opt_errors('dbname'))
    usage()
else:
    dbname = args['--dbname']
if not args['--dbhost']:
    print(print_opt_errors('dbhost'))
    usage()
else:
    dbhost = args['--dbhost']
if not args['--dbuser']:
    print(print_opt_errors('dbuser'))
    usage()
else:
    dbuser = args['--dbuser']
if not args['--smtpserver']:
    print(print_opt_errors('smtpserver'))
    usage()
else:
    smtpserver = args['--smtpserver']
if args['--dbpass'] == None:
    dbpass = ''
else:
    dbpass = args['--dbpass']
if not args['--client']:
    client = '%'
else:
    client = args['--client']
if not args['--jobname']:
    jobname = '%'
else:
    jobname = args['--jobname']
if args['--smtpuser'] == None:
    smtpuser = ''
else:
    smtpuser = args['--smtpuser']
if args['--smtppass'] == None:
    smtppass = ''
else:
    smtppass = args['--smtppass']

# Connect to database and query for all
# matching jobs in the past 'time' hours
# --------------------------------------
try:
    db_connect()
    if dbtype == 'pgsql':
        query_str = "SELECT JobId, Client.Name AS Client, REPLACE(Job.Name,' ','_') AS JobName, \
            JobStatus, JobErrors, Type, Level, JobFiles, JobBytes, StartTime, EndTime, \
            PriorJobId, AGE(EndTime, StartTime) AS RunTime \
            FROM Job \
            INNER JOIN Client on Job.ClientID=Client.ClientID \
            WHERE (EndTime >= CURRENT_TIMESTAMP(2) - cast('" + time + " HOUR' as INTERVAL) \
            OR (JobStatus='R' OR JobStatus='C')) \
            AND Client.Name LIKE '" + client + "' \
            AND Job.Name LIKE '" + jobname + "' \
            ORDER BY " + sortfield + " " + sortorder + ";"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, CAST(Client.name as CHAR(50)) AS client, \
            REPLACE(CAST(Job.name as CHAR(50)),' ','_') AS jobname, CAST(jobstatus as CHAR(1)) AS jobstatus, \
            joberrors, CAST(type as CHAR(1)) AS type, CAST(level as CHAR(1)) AS level, jobfiles, jobbytes, \
            starttime, endtime, priorjobid, TIMEDIFF (endtime, starttime) as runtime \
            FROM Job \
            INNER JOIN Client on Job.clientid=Client.clientid \
            WHERE (endtime >= DATE_ADD(NOW(), INTERVAL -" + time + " HOUR) \
            OR (jobstatus='R' OR jobstatus='C')) \
            AND Client.Name LIKE '" + client + "' \
            AND Job.Name LIKE '" + jobname + "' \
            ORDER BY " + sortfield + " " + sortorder + ";"
    cur.execute(query_str)
    alljobrows = cur.fetchall()
except:
    print('Problem communicating with database \'' + dbname + '\' while fetching all jobs.')
    sys.exit(1)
finally:
    if (conn):
        cur.close()
        conn.close()

# -----------------------------------------------------------------------
# TODO/NOTE:  What about Copy/Migration jobs which
#             Copy/Migrate jobs older than 'time'?
#
# These "new" 'copied' jobs will not appear in the listing because they
# inherit the end time of the original backup job. Do we consider them
# to be within 'time' time because they are new, even though they retain
# the endtime of the job they are a copy of?  Good question?? I say 'yes'
#
# Idea: For each job of type=(c|g), query the log table, and find the new
# backup jobids from the Summary field.
#
# Then, for each of these "New Backup JobIds" we identify, we query the DB
# as in the cur.execute() above (will be a more simple query, minus the 'R'
# and 'C' and time restrictions in the INNER JOIN)
#
# Then, add the results to the list of alljobrows to work on... uff...
#
# Crazy?  Is it worth it? Will anyone care?
#--------------------------------------------------------------------------

# Assign some lists, lengths, and totals to variables for later
# -------------------------------------------------------------
alljobids = [r['jobid'] for r in alljobrows]
alljobnames = [r['jobname'] for r in alljobrows]
badjobids = [r['jobid'] for r in alljobrows if r['jobstatus'] in badjobset]
numjobs = len(alljobrows)
numbadjobs = len(badjobids)
total_backup_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'B'])
total_backup_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'B'])
total_restore_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'R'])
total_restore_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'R'])
total_verify_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'V'])
total_verify_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'V'])
total_copied_files = sum([r['jobfiles'] for r in alljobrows if r['type'] == 'C'])
total_copied_bytes = sum([r['jobbytes'] for r in alljobrows if r['type'] == 'C'])
jobswitherrors = len([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
totaljoberrors = sum([r['joberrors'] for r in alljobrows if r['joberrors'] > 0])
runningorcreated = len([r['jobstatus'] for r in alljobrows if r['jobstatus'] in ('R', 'C')])
ctrl_jobids = [r['jobid'] for r in alljobrows if r['type'] in ('c', 'g')]
vrfy_jobids = [r['jobid'] for r in alljobrows if r['type'] =='V']

# More silly OCD string manipulations
# -----------------------------------
hour = 'hour' if time == 1 else 'hours'
jobstr = 'all jobs' if jobname == '%' else 'jobname \'' + jobname + '\''
clientstr = 'all clients' if client == '%' else 'client \'' + client + '\''

# If there are no jobs to report
# on, just send the email & exit
# ------------------------------
if numjobs == 0:
    subject = server + ' - No jobs found for ' + clientstr + ' in the past ' + time + ' ' + hour + ' for ' + jobstr
    if addsubjecticon == 'yes':
        subject = set_subject_icon() + ' ' + subject
    msg = 'These are not the droids you are looking for.'
    send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)
    sys.exit(1)
else:
    # More silly OCD string manipulations
    # -----------------------------------
    job = 'job' if numjobs == 1 else 'jobs'

# Get a list of jobs that have always failed for the
# past 'days' days so that we can display a column
# or the entire row in the 'alwaysfailcolor' color
# --------------------------------------------------
try:
    db_connect()
    if dbtype == 'pgsql':
        query_str = "SELECT JobId, REPLACE(Job.Name,' ','_') AS JobName, JobStatus \
        FROM Job WHERE endtime >= (NOW()) - (INTERVAL '" + days + " DAY') ORDER BY jobid DESC;"
    elif dbtype in ('mysql', 'maria'):
        query_str = "SELECT jobid, REPLACE(CAST(Job.name as CHAR(50)),' ','_') AS jobname, \
        CAST(jobstatus as CHAR(1)) AS jobstatus FROM Job \
        WHERE endtime >= DATE_ADD(NOW(), INTERVAL -" + days + " DAY) ORDER BY jobid DESC;"
    cur.execute(query_str)
    alldaysjobrows = cur.fetchall()
except:
    print('Problem communicating with database \'' + dbname + '\' while fetching "always failing jobs" list.')
    sys.exit(1)
finally:
    if (conn):
        cur.close()
        conn.close()

# These are specific to the 'always failing jobs' features
# --------------------------------------------------------
good_days_jobs = [r['jobname'] for r in alldaysjobrows if r['jobstatus'] == 'T']
unique_bad_days_jobs = {r['jobname'] for r in alldaysjobrows if r['jobstatus'] not in ('T', 'R', 'C')}
always_fail_jobs = set(unique_bad_days_jobs.difference(good_days_jobs)).intersection(alljobnames)

# Do we append the 'Running or Created' message to the Subject?
# -------------------------------------------------------------
if addsubjectrunningorcreated == 'yes' and runningorcreated != 0:
    runningjob = 'job' if runningorcreated == 1 else 'jobs'
    runningorcreatedsubject = ' (' + str(runningorcreated) + ' ' + runningjob + ' queued/running)'
else:
    runningorcreatedsubject = ''

# Create the Subject
# ------------------
subject = server + ' - ' + str(numjobs) + ' ' + job + ' in the past ' \
        + str(time) + ' ' + hour + ': ' + str(numbadjobs) + ' bad, ' \
        + str(jobswitherrors) + ' with errors, for ' + clientstr + ', and ' \
        + jobstr + runningorcreatedsubject
if addsubjecticon == 'yes':
    subject = set_subject_icon() + ' ' + subject

# For each Copy/Migration Control Job (c, g),
# get the Job summary text from the log table
# -------------------------------------------
# - cji = Control Job Information
# -------------------------------
if len(ctrl_jobids) != 0:
    try:
        db_connect()
        if dbtype == 'pgsql':
            query_str = 'SELECT jobid, logtext FROM log WHERE jobid IN (' \
            + ', '.join([str(x) for x in ctrl_jobids]) + ') AND logtext LIKE \
            \'%Termination:%\' ORDER BY jobid DESC;'
        elif dbtype in ('mysql', 'maria'):
            query_str = 'SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (' + ', '.join([str(x) for x in ctrl_jobids]) \
            + ') AND logtext LIKE \'%Termination:%\' ORDER BY jobid DESC;'
        cur.execute(query_str)
        cji_rows = cur.fetchall()
    except:
        print('Problem communicating with database \'' + dbname + '\' while fetching control job info.')
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
    # For each row of the returned cji_rows (Ctrl Jobs), add to
    # the pn_jobids dict as [CtrlJobid: ('PrevJobId', 'NewJobId')]
    # ------------------------------------------------------------
    pn_jobids = {}
    for cji in cji_rows:
        pn_jobids[str(cji['jobid'])] = (pn_job_id(cji, 'Prev'), pn_job_id(cji, 'New'))

# For each Verify Job (V), get the Job summary text from the log table
# --------------------------------------------------------------------
# - vji = Verify Job Information
# ------------------------------
if len(vrfy_jobids) != 0:
    try:
        db_connect()
        if dbtype == 'pgsql':
            query_str = 'SELECT jobid, logtext FROM log WHERE jobid IN (' \
            + ', '.join([str(x) for x in vrfy_jobids]) + ') AND logtext LIKE \
            \'%Termination:%\' ORDER BY jobid DESC;'
        elif dbtype in ('mysql', 'maria'):
            query_str = 'SELECT jobid, CAST(logtext as CHAR(1000)) AS logtext \
            FROM Log WHERE jobid IN (' + ', '.join([str(x) for x in vrfy_jobids]) \
            + ') AND logtext LIKE \'%Termination:%\' ORDER BY jobid DESC;'
        cur.execute(query_str)
        vji_rows = cur.fetchall()
    except:
        print('Problem communicating with database \'' + dbname + '\' while fetching verify job info.')
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
    # For each row of the returned vji_rows (Vrfy Jobs), add
    # to the v_jobids dict as [VrfyJobid: 'Verified JobId']
    # ------------------------------------------------------
    v_jobids = {}
    for vji in vji_rows:
        v_jobids[str(vji['jobid'])] = v_job_id(vji)

# Do we email all job summaries?
# ------------------------------
if emailjobsummaries == 'yes':
    jobsummaries = '<pre>====================================\n' \
    + 'Job Summaries of All Terminated Jobs\n====================================\n'
    try:
        db_connect()
        for job_id in alljobids:
            if dbtype == 'pgsql':
                query_str = 'SELECT jobid, logtext FROM Log WHERE jobid=' \
                + str(job_id) + ' AND logtext LIKE \'%Termination:%\' ORDER BY jobid DESC;'
            elif dbtype in ('mysql', 'maria'):
                query_str = 'SELECT jobid, CAST(logtext as CHAR(2000)) AS logtext FROM Log WHERE jobid=' \
                + str(job_id) + ' AND logtext LIKE \'%Termination:%\' ORDER BY jobid DESC;'
            cur.execute(query_str)
            summaryrow = cur.fetchall()
            # Migrated (M) Jobs have no joblog
            # --------------------------------
            if len(summaryrow) != 0:
                jobsummaries += '==============\nJobID:' \
                + '{:8}'.format(summaryrow[0]['jobid']) \
                + '\n==============\n' + summaryrow[0]['logtext']
        jobsummaries += '</pre>'
    except:
        print('\nProblem communicating with database \'' + dbname + '\' while fetching all job summaries.\n')
        sys.exit(1)
    finally:
        if (conn):
            cur.close()
            conn.close()
else:
    jobsummaries = ''

# Do we email the bad job logs?
# -----------------------------
if emailbadlogs == 'yes':
    badjoblogs = '<pre>=================\nBad Job Full Logs\n=================\n'
    if len(badjobids) != 0:
        try:
            db_connect()
            for job_id in badjobids:
                if dbtype == 'pgsql':
                    query_str = 'SELECT jobid, time, logtext FROM log WHERE jobid=' \
                    + str(job_id) + ' ORDER BY jobid, time ASC;'
                elif dbtype in ('mysql', 'maria'):
                    query_str = 'SELECT jobid, time, CAST(logtext as CHAR(2000)) AS logtext \
                    FROM Log WHERE jobid=' + str(job_id) + ' ORDER BY jobid, time ASC;'
                cur.execute(query_str)
                badjobrow = cur.fetchall()
                badjoblogs += '==============\nJobID:' \
                + '{:8}'.format(job_id) + '\n==============\n'
                for r in badjobrow:
                    badjoblogs += str(r['time']) + ' ' + r['logtext']
            badjoblogs += '</pre>'
        except:
            print('\nProblem communicating with database \'' + dbname + '\' while fetching bad job logs.\n')
            sys.exit(1)
        finally:
            if (conn):
                cur.close()
                conn.close()
    else:
        badjoblogs += '\n===================\nNo Bad Jobs to List\n===================\n'
else:
    badjoblogs = ''

# Start creating the msg to send
# ------------------------------
msg = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' \
    + '<style>body {font-family:' + fontfamily + '; font-size:' + fontsize + ';} td {font-size:' \
    + fontsizejobinfo + ';} pre {font-size:' + fontsizesumlog + ';}</style></head><body>\n'

# Are we going to be highlighting Jobs that are always failing?
# If yes, let's build the banner and add it to the to beginning
# -------------------------------------------------------------
if alwaysfailcolumn != 'none' and len(always_fail_jobs) != 0:
    # Some silly OCD string manipulations
    # -----------------------------------
    if len(always_fail_jobs) == 1:
        job = 'job'
        have = 'has'
    else:
        job = 'jobs'
        have = 'have'
    msg += '<br><table align="left" border="0" cellpadding="2" cellspacing="0">' \
        +'<tr><td style="font-size: 14px;" bgcolor="' + alwaysfailcolor \
        + '"><b>The ' + str(len(always_fail_jobs)) + ' ' + job + ' who\'s ' \
        + alwaysfailcolumn_str + ' has this background color ' + have \
        + ' always failed in the past ' + days + ' days</b></td></tr></table><br><br>'

# Create the table header from the columns in the
# cols2show variable in the order they are defined
# ------------------------------------------------
msg += '<table width="100%" align="center" border="1" cellpadding="2" cellspacing="0">' \
    + '<tr bgcolor="' + jobtableheadercolor + '">'
for colname in c2sl:
    if colname not in valid_col_lst:
        print('\nColumn name \'' + colname + '\' not valid. Exiting!\n')
        print('Valid columns are: ' + ', '.join(valid_col_lst))
        usage()
    msg += col_hdr_dict[colname]
msg += '</tr>\n'

# Build the jobs table from the columns in the
# cols2show variable in the order they are defined
# ------------------------------------------------
for jobrow in alljobrows:
    # If this job is always failing, set the alwaysfail variable
    # ----------------------------------------------------------
    if len(always_fail_jobs) != 0 and jobrow['jobname'] in always_fail_jobs:
        alwaysfail = 'yes'
    else:
        alwaysfail = 'no'

    # Set the job row's default bgcolor
    # ---------------------------------
    if alwaysfail == 'yes' and alwaysfailcolumn == 'row':
        msg += '<tr bgcolor="' + alwaysfailcolor + '">'
    else:
        msg += '<tr bgcolor="' + jobtablerowcolor + '">'

    for colname in c2sl:
        if colname == 'jobid':
            msg += html_format_cell(str(jobrow['jobid']), col = 'jobid', star = '*' if starbadjobids == 'yes' and jobrow['jobstatus'] in badjobset else '')
        elif colname == 'jobname':
            msg += html_format_cell(jobrow['jobname'], col = 'jobname')
        elif colname == 'client':
            msg += html_format_cell(jobrow['client'], col = 'client')
        elif colname == 'status':
            msg+= html_format_cell(translate_job_status(jobrow['jobstatus'], jobrow['joberrors']), col = 'status')
        elif colname == 'joberrors':
            msg += html_format_cell(str('{:,}'.format(jobrow['joberrors'])), col = 'joberrors')
        elif colname == 'type':
            msg += html_format_cell(translate_job_type(jobrow['type'], jobrow['jobid'], jobrow['priorjobid'], jobrow['jobstatus']), col = 'type')
        elif colname == 'level':
            msg += html_format_cell(translate_job_level(jobrow['level'], jobrow['type']), col = 'level')
        elif colname == 'jobfiles':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobfiles'])), jobtype = jobrow['type'], jobstatus = jobrow['jobstatus'], col = 'jobfiles') 
        elif colname == 'jobbytes':
            msg += html_format_cell(str('{:,}'.format(jobrow['jobbytes'])), jobtype = jobrow['type'], jobstatus = jobrow['jobstatus'], col = 'jobbytes')
        elif colname == 'starttime':
            msg += html_format_cell(str(jobrow['starttime']), col = 'starttime', jobstatus = jobrow['jobstatus'])
        elif colname == 'endtime':
            msg += html_format_cell(str(jobrow['endtime']), col = 'endtime', jobstatus = jobrow['jobstatus'])
        elif colname == 'runtime':
            msg += html_format_cell(str(jobrow['runtime']), col = 'runtime')
    msg += '</tr>\n'
msg += '</table>'

# Email the summary table?
# ------------------------
if emailsummary == 'yes':
    summary = '<br><hr align="left" width="25%">' \
            + '<table width="25%">' \
            + '<tr><td><b>Total Jobs</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(numjobs) + '</b></td></tr>' \
            + '<tr><td><b>Bad Jobs</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(numbadjobs) + ' </b></td></tr>' \
            + '<tr><td><b>Jobs with Errors</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(jobswitherrors) + ' </b></td></tr>' \
            + '<tr><td><b>Total Job Errors</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(totaljoberrors) + ' </b></td></tr>' \
            + '<tr><td><b>Total Backup Files</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(total_backup_files) + '</b></td></tr>' \
            + '<tr><td><b>Total Backup Bytes</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + humanbytes(total_backup_bytes) + '</b></td></tr>' \
            + '<tr><td><b>Total Restore Files</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(total_restore_files) + '</b></td></tr>\n' \
            + '<tr><td><b>Total Restore Bytes</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + humanbytes(total_restore_bytes) + '</b></td></tr>' \
            + '<tr><td><b>Total Copied Files</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(total_copied_files) + '</b></td></tr>\n' \
            + '<tr><td><b>Total Copied Bytes</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + humanbytes(total_copied_bytes) + '</b></td></tr>' \
            + '<tr><td><b>Total Verify Files</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + '{:,}'.format(total_verify_files) + '</b></td></tr>' \
            + '<tr><td><b>Total Verify Bytes</b></td><td align="center"><b>:</b></td> <td align="right"><b>' \
            + humanbytes(total_verify_bytes) + '</b></td></tr></table>' \
            + '<hr align="left" width="25%">'
else:
    summary = ''

# Build the final message and send the email
# ------------------------------------------
msg = msg + summary + prog_info + jobsummaries + badjoblogs
send_email(email, fromemail, subject, msg, smtpuser, smtppass, smtpserver, smtpport)


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4
