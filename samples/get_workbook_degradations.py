####
# This script demonstrates how to use the Tableau Server Client
# to view the functionality that would be lost if workbook were to
# downgrade to a specified product version.
#
# The option to specify a single workbook (by either ID or name)
# or project (by either ID or name) is given. If neither is specified,
# degradations will be returned for all workbooks on the server.
####
import sys
import argparse
import getpass
import logging
import os.path
import tableauserverclient as TSC
import xml.etree.ElementTree as ET

def main():
    #Either workbookId or workbookName can be specified
    #Either projectId or ProjectName can be specified
    #Both/either/neither a project and a workbook can be specified
    parser = argparse.ArgumentParser(description='Get workbook degradations.')
    parser.add_argument('--server', '-s', required = True, help = 'server address')
    parser.add_argument('--username', '-u', required = True, help = 'username to sign into server')
    parser.add_argument('--productVersion', '-v', required = True, help = 'product version to which to test downgrade of workbook')
    workbook_specified = parser.add_mutually_exclusive_group(required = False)
    workbook_specified.add_argument('--workbookId', help = 'Id of workbook upon which to test the degradation')
    workbook_specified.add_argument('--workbookName', help = 'Name of workbook upon which to test the degradation')
    project_specified = parser.add_mutually_exclusive_group(required = False)
    project_specified.add_argument('--projectId', help = 'Id of project: degradations for all workbooks in project will be returned')
    project_specified.add_argument('--projectName', help = 'Name of project: degradations for all workbooks in project will be returned')
    parser.add_argument('--logging-level', '-l', choices = ['debug', 'info', 'error'], default='error',
                        help ='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")
    sys.stderr.write("Fetching Degradations...\n")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)
    server.use_highest_version()

    overwrite_true = TSC.Server.PublishMode.Overwrite

    with server.auth.sign_in(tableau_auth):
        print("Workbook Name,Degradation Name,Severity")
        response=''
        all_workbooks, pagination_item = server.workbooks.get()
        if args.workbookId is not None:
            workbook = server.workbooks.get_by_id(args.workbookId)
            if args.projectId is None and args.projectName is None:
                response = server.workbooks.get_degradations(args.workbookId, args.productVersion, workbook.name)
            elif args.projectId is not None and args.projectId==workbook.project_id:
                response = server.workbooks.get_degradations(workbookId, args.productVersion, workbook.name)
            elif args.projectName is not None and args.projectName==workbook._project_name:
                response = server.workbooks.get_degradations(workbookId, args.productVersion, workbook.name)
            if response != '':
                root=ET.fromstring(response.content)
                child=root[0]
                for c in child:
                    print("\"{0}\",{1},{2}".format(workbook.name,c.get('name'),c.get('severity')))

        elif args.workbookName is not None:
            all_workbooks, pagination_item = server.workbooks.get()
            if args.projectId is None and args.projectName is None:
                for workbook in all_workbooks:
                    if workbook.name == args.workbookName:
                        response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name)
                        break
            elif args.projectId is not None:
                for workbook in all_workbooks:
                    if (workbook.name == args.workbookName and workbook.project_id == args.projectId):
                        response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name) 
                        break
            elif args.projectName is not None:
                for workbook in all_workbooks:
                    if (workbook.name == args.workbookName and workbook._project_name == args.projectName):
                        response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name)
                        break
            if response != '':
                root=ET.fromstring(response.content)
                child=root[0]
                for c in child:
                    print("\"{0}\",{1},{2}".format(workbook.name,c.get('name'),c.get('severity')))

        elif args.projectId is not None:
            all_workbooks, pagination_item = server.workbooks.get()
            for workbook in all_workbooks:
                if workbook.project_id == args.projectId:
                    response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name)
                    root=ET.fromstring(response.content)
                    child=root[0]
                    for c in child:
                        print("\"{0}\",{1},{2}".format(workbook.name,c.get('name'),c.get('severity')))

        elif args.projectName is not None:
            all_workbooks, pagination_item = server.workbooks.get()
            for workbook in all_workbooks:
                if workbook._project_name == args.projectName:
                    response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name)
                    root=ET.fromstring(response.content)
                    child=root[0]
                    for c in child:
                        print("\"{0}\",{1},{2}".format(workbook.name,c.get('name'),c.get('severity')))

        else:
            for workbook in all_workbooks:
                response = server.workbooks.get_degradations(workbook._id, args.productVersion, workbook.name)
                root=ET.fromstring(response.content)
                child=root[0]
                for c in child:
                    print("\"{0}\",{1},{2}".format(workbook.name,c.get('name'),c.get('severity')))
    sys.stderr.write("Finished fetching degradations.\n")

if __name__ == '__main__':
    main()
