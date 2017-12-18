#! /usr/bin/python2.7
"""Instance Group Creation"""

#Copyright 2017 lawny.co

import argparse
import os
import time
from six.moves import input
import googleapiclient.discovery
from oauth2client.client import GoogleCredentials
CREDENTIALS = GoogleCredentials.get_application_default()
COMPUTE = googleapiclient.discovery.build('compute', 'v1')

 #[START list_instance_groups]
def list_instance_groups(compute, project, zone):
    """ list all the instance groups in project/zone """
    result = compute.instanceGroups().list(project=project, zone=zone).execute()
    return result['items']
# [END list_instance_groups]

# [START create_instance_group]
def create_instance_group(compute, project, zone):
    """ Create the new instance group """
    network_response = compute.networks().get(
        project=project, network='devops-internal').execute()
    network = network_response['selfLink']
    config = {
        'description': 'Instance Group for build server',
        'name': 'buildservergroup',
        'network': network,
        'region': zone,
        }

    return compute.instanceGroups().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance_group]

# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    """ Check the status of the current operation """
    print 'Waiting for operation to finish...'
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print "done."
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]

# [Build the instance group]
def main(project, zone, wait=False):
    """ Execution of the steps """
    compute = googleapiclient.discovery.build('compute', 'v1')

    print 'Creating Instance Group...'

    operation = create_instance_group(compute, project, zone)
    wait_for_operation(compute, project, zone, operation['name'])

    instancegroups = list_instance_groups(compute, project, zone)

    print 'Instance groups in project %s and zone %s:' % (project, zone)
    for instancegroup in instancegroups:
        print ' - ' + instancegroup['name']

    print """
Instance Group Created
"""
    if wait:
        input()

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    PARSER.add_argument(
        '--project_id',
        default=os.environ.get('GOOGLE_PROJECT', None),
        help='Your Google Cloud project ID.')
    PARSER.add_argument(
        '--zone',
        default='us-west1-b',
        help='Compute Engine zone to deploy to.')
    PARSER.add_argument(
        '--name',
        default='buildservers',
        help='New instance name.'
    )

    ARGS = PARSER.parse_args()

    main(ARGS.project_id, ARGS.zone, ARGS.name)
# [END run]
