import click
import requests
import json
import os


@click.command()
@click.argument('machine', required=True, nargs=1)
@click.argument('from_path', required=True, nargs=1)
@click.argument('to_path', required=False, default='.', nargs=1)
def pull(machine, from_path, to_path):
    """Pulls file(s) from machine with id @machine using secret user token and ssh key."""
    try:
        # retrieve the secret token from the config folder
        token = "./vectordash_config/token.txt"

        if os.path.isfile(token):
            with open(token) as f:
                token = f.readline()

            try:
                # API endpoint for machine information
                full_url = "https://84119199.ngrok.io/api/list_machines/" + token
                r = requests.get(full_url)

                # API connection is successful, retrieve the JSON object
                if r.status_code == 200:
                    data = r.json()

                    # machine provided is one this user has access to
                    if data.get(machine):
                        machine = (data.get(machine))
                        print("Machine exists. Connecting...")

                        # Machine pem
                        pem = machine['pem']

                        # name for pem key file, formatted to be stored
                        machine_name = (machine['name'].lower()).replace(" ", "")
                        key_file = "./vectordash_config/" + machine_name + "-key.pem"

                        # create new file ./vectordash_config/<key_file>.pem to write into
                        with open(key_file, "w") as h:
                            h.write(pem)

                        # give key file permissions for scp
                        os.system("chmod 600 " + key_file)

                        # Port, IP address, and user information for pull command
                        port = str(machine['port'])
                        ip = str(machine['ip'])
                        user = str(machine['user'])

                        # execute pull command
                        pull_command = "scp -r -P " + port + " -i " + key_file + " " + user + "@" + ip + ":" + from_path + " " + to_path
                        print(pull_command)
                        os.system(pull_command)

                    else:
                        print("Invalid machine id provided. Please make sure you are connecting to a valid machine")

                else:
                    print("Could not connect to vectordash API with provided token")

            except json.decoder.JSONDecodeError:
                print("Invalid token value. Please make sure you are using the most recently generated token.")

        else:
            # If token is not stored, the command will not execute
            print("Please make sure a valid token is stored. Run 'vectordash secret <token>'")

    except TypeError:
        print("There was a problem with pull. Command is of the format 'vectordash pull <id> <from_path> <to_path>' or "
              "'vectordash pull <id> <from_path>'")

# if __name__ == '__main__':
#     # When valid command A is given (i.e machine, from_path, to_path are provided)
#     if len(sys.argv) == 4:
#
#         # Retrieve secret machine, from_path, to_path from command and store it
#         machine = sys.argv[1]
#         from_path = sys.argv[2]
#         to_path = sys.argv[3]
#         pull_from_machine(machine, from_path, to_path)
#
#     # When valid command B is given (i.e machine, from_path are provided)
#     elif len(sys.argv) == 3:
#         machine = sys.argv[1]
#         from_path = sys.argv[2]
#         to_path = "."
#         pull_from_machine(machine, from_path, to_path)
#
#     else:
#         print("Incorrect number of arguments provided. Command is of the format 'vectordash pull <machine> <from_path> <to_path>' or 'vectordash push <machine> <from_path>'")