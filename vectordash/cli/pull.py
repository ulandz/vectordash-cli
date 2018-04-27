import click
import requests
import json
import os
import subprocess
from colored import fg
from colored import stylize

from vectordash import API_URL, TOKEN_URL


@click.command()
@click.argument('machine', required=True, nargs=1)
@click.argument('from_path', required=True, nargs=1)
@click.argument('to_path', required=False, default='.', nargs=1, type=click.Path())
def pull(machine, from_path, to_path):
    """
    args: <machine> <from_path> <to_path>
    Argument @to_path is optional. If not provided, defaults to '.' (current dir).

    Pulls file(s) from machine

    """
    try:
        # retrieve the secret token from the config folder
        dot_folder = os.path.expanduser('~/.vectordash/')
        token = os.path.join(dot_folder, 'token')

        if os.path.isfile(token):
            with open(token) as f:
                secret_token = f.readline()

            # API endpoint for machine information
            full_url = API_URL + str(secret_token)
            r = requests.get(full_url)

            # API connection is successful, retrieve the JSON object
            if r.status_code == 200:
                data = r.json()

                # machine provided is one this user has access to
                if data.get(machine):
                    gpu_mach = (data.get(machine))

                    # Machine pem
                    pem = gpu_mach['pem']

                    # name for pem key file, formatted to be stored
                    machine_name = (gpu_mach['name'].lower()).replace(" ", "")
                    key_file = dot_folder + machine_name + '-key.pem'

                    # create new file ~/.vectordash/<key_file>.pem to write into
                    with open(key_file, "w") as h:
                        h.write(pem)

                    # give key file permissions for scp
                    os.chmod(key_file, 600)

                    # Port, IP address, and user information for pull command
                    port = str(gpu_mach['port'])
                    ip = str(gpu_mach['ip'])
                    user = str(gpu_mach['user'])

                    # execute pull command
                    pull_command = ["scp", "-r", "-P", port, "-i", key_file, user + "@" + ip + ":" + from_path, to_path]
                    print("Executing " + stylize(" ".join(pull_command), fg("blue")))
                    subprocess.check_call(pull_command)

                else:
                    print(stylize(machine + " is not a valid machine id.", fg("red")))
                    print("Please make sure you are connecting to a valid machine")

            else:
                print(stylize("Could not connect to Vectordash API with provided token", fg("red")))

        else:
            # If token is not stored, the command will not execute
            print(stylize("Unable to connect with stored token. Please make sure a valid token is stored.", fg("red")))
            print("Run " + stylize("vectordash secret <token>", fg("blue")))
            print("Your token can be found at " + stylize(str(TOKEN_URL), fg("blue")))

    except TypeError:
        type_err = "There was a problem with pull. Command should be of the format "
        cmd_1 = stylize("vectordash pull <id> <from_path> <to_path>", fg("blue"))
        cmd_2 = stylize("vectordash pull <id> <from_path>", fg("blue"))
        print(type_err + cmd_1 + " or " + cmd_2)
