"""
backend.api_interactions.cello_requests
2020 W.R. Jackson.

This is the Cello Python API rewritten slightly.

The base module does a lot of things that I like (I like the Click integration,
I think the way they're handling environment based variables as a means of
authentication is smart, I think its structure really exposes the 'ways'
users would think about interacting with this service.)

My critiques have only to do with my ardent fervor towards typical PEP-8
standards, function documentation, and typing.
"""
import json
import os
import pprint
import time
from typing import (
    Dict
)

from colorama import Fore
import requests
from Bio import SeqIO
from requests.auth import HTTPBasicAuth

REQUEST_RETRIES = 3


class CelloAuth:
    def __init__(
            self,
            url: str,
            username: str = None,
            password: str = None,
    ):
        self.url_root = url
        if username != password and None in [username, password]:
            raise RuntimeError(
                'Both user name and password have to be set during the use of '
                'the CelloAuth ctx manager or default to environment based '
                'tokens. (You need to pass in both or none at all)'
            )
        if username is None and password is None:
            env_username = os.environ.get('CELLOUSER')
            env_password = os.environ.get('CELLOPASS')
            if env_username is None or env_password is None:
                raise RuntimeError(
                    'Unable to locate Cello environment variables set in '
                    'the OS. Please reference README on how to correctly '
                    'set username and password based on operating'
                    'system.'
                )
            self.username = env_username
            self.password = env_password
        else:
            self.username = username
            self.password = password
        self.auth = HTTPBasicAuth(self.username, self.password)

    def validate_authentication(self):
        '''
        For module or package based APIs that have to deal with external
        services, I'm typically in favor of attempting AUTH before you actually
        deal with the meat and potatoes of what you're trying to pass back and
        forth.

        This adds some auto retry logic just in case people are trying to use
        this in an automated workflow to add some robustness to the interaction.

        Returns:
            Whether the username and password are valid.
        '''
        for i in range(REQUEST_RETRIES):
            if i - 1 >= REQUEST_RETRIES:
                raise RuntimeError(
                    'Unable to communicate with Cello  after three attempts. '
                    'Please investigate internet connection or Cello API Status'
                )
            resp = requests.get(
                f'{self.url_root}',
                auth=self.auth,
            )
            if resp != 200:
                print(
                    f"Failed to successfully communicate with Cello."
                    f" Retrying. Attempt {i}"
                )
                time.sleep(1)
                continue
            else:
                break

    def __enter__(self):
        '''
        This enforces authentication before we do any kind of operation on the
        remote API.

        Returns:
            An HTTP Auth object to pass into the requests get call
        '''
        self.validate_authentication()
        return self.auth

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Simple pass for when we exit the context manager.

        Args:
            exc_type: Execution Type
            exc_val: Execution Value
            exc_tb: Execution Traceback

        '''
        pass


class CelloAPI:
    '''
    Allows access to the CelloAPI as either an object or as a CLI entrypoint.

    The purpose of this division is to allow users to extend or automate their
    own interactions with CelloCAD or to allow a backwards compatible CLI.
    '''

    def __init__(
            self,
            url: str = 'http://cellocad.org:8080',
            routing_command: str = None,
            username: str = None,
            password: str = None,
            **kwargs,
    ):
        self.base_url = url
        self.auth = CelloAuth(url, username, password)
        self.cli_context = True if routing_command else False

        if self.cli_context:
            self.parse_cli_command(routing_command, kwargs)

    def parse_cli_command(self, routing_command: str, kwargs: Dict):
        '''
        Parses and routes CLI centric commands. Currently having some issues
        with communicating with Cello V2 remote API, so these are mostly
        placeholders.

        Args:
            routing_command: What command to execute.
            kwargs: Additional argument to the command line function.

        '''
        if routing_command == 'in_out':
            # Unpacking Kwargs goes here.
            print(Fore.GREEN + self.get_inputs_and_outpus(kwargs))
        if routing_command == 'netsynth':
            # Unpacking Kwargs goes here.
            print(Fore.GREEN + self.validate_verilog(kwargs))
        if routing_command == 'submit':
            print(Fore.GREEN + self.submit_to_cello(kwargs))
        if routing_command == 'results':
            print(Fore.GREEN + self.get_results())
        if routing_command == 'ucf':
            print(Fore.GREEN + self.get_ucf())

    def fetch_resource(
            self,
            end_point: str,
            additional_arguments: dict = None,
            operation: str = 'GET',
    ) -> requests.request:
        '''
        Interacts with an API endpoint.

        Args:
            end_point: Which endpoint to interact with.
            operation: What operation to use [`POST` | `GET` | `DELETE`]
            additional_arguments: Additional arguments to the end point.

        Returns:
            Unicode encoded message content.
        '''
        with self.auth as cello_auth:
            base_endpoint = f'{self.base_url}/{end_point}'
            if additional_arguments is not None:
                for argument in additional_arguments:
                    content = additional_arguments[argument]
                    base_endpoint += f'/{content}'
            if operation == 'GET':
                resp = requests.get(base_endpoint, auth=cello_auth)
            if operation == 'DELETE':
                resp = requests.delete(base_endpoint, auth=cello_auth)
            if resp.status_code != 200:
                # If we're already doing colored text why not...
                print(Fore.RED + f'Failed to receive response from Cello API.'
                                 f' Response content is: {resp.text}'
                      )
            if self.cli_context:
                pprint.pprint(Fore.GREEN + resp.text)
            return resp.text

    def get_results(
            self,
            job_id: str = None,
            keyword: str = None,
            extension: str = None,
            filename: str = None
    ):
        '''
        Gets result from end point

        Args:
            job_id: Job Identification Number
            keyword: Which keyword to search for, if passed in.
            extension: Which extension to search for, if passed in.
            filename: Which filename to search for, if passed in.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        params = {}
        if job_id is None:
            pass
        elif job_id is not None and filename is None:
            params = {'job_id': job_id}
            if keyword:
                params['keyword'] = keyword
            if extension:
                params['extension'] = extension
        elif job_id is not None and filename is not None:
            params = {
                'job_id': job_id,
                'filename': filename,
            }
        return self.fetch_resource(f'results', params)

    def get_inputs(self, name: str = None):
        '''
        Gets the valid inputs to repressors/gates. These are biological signals
        and their associated dna sequence.

        Args:
            name: What name to look for, if passed in. If not passed in we
            just get all possible inputs.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        if name is not None:
            params = {
                'filename': f'input_{name}.text'
            }
        else:
            params = {
                'keyword': 'input_',
                'extension:': '.txt',
            }
        return self.fetch_resource('in_out', params)

    def get_outputs(self, name: str = None):
        '''
        Gets the valid outputs for the genetic circuit. These are typically
        (in the toy problem) fluorescent proteins or common signaling outputs 
        and their associated genetic sequence. 

        Args:
            name: Which output to look for, if passed in. If not passed in we
                fetch all possible outputs.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        if name is not None:
            params = {
                'filename': f'output_{name}.text'
            }
        else:
            params = {
                'keyword': 'output_',
                'extension:': '.txt',
            }
        return self.fetch_resource('in_out', params)

    def post_input(
            self,
            name: str,
            low_signal: float,
            high_signal: float,
            dna_sequence: str,
    ):
        '''
        Creates an input file on the server.

        Args:
            name: Name of the input signal. (e.g., pLux, pTet)
            low_signal: Signal value when it's 'low'
            high_signal: Signal value when it's 'high'
            dna_sequence: The DNA sequence of the input signal.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        file_string = f'{name} {low_signal} {high_signal} {dna_sequence}\n'
        params = {
            'filename': f'input_{name}.text',
            'filetext': file_string,
        }
        return self.fetch_resource('in_out', params)

    def delete_input(self, name: str):
        '''
        Deletes an input.

        Args:
            name: The name of the input to delete.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        params = {
            'filename': f'input_{name}.text'
        }
        return self.fetch_resource('in_out', params, 'DELETE')

    def delete_output(self, name: str):
        '''
        Deletes an output.

        Args:
            name: The name of the output to delete

        Returns:
            Remote endpoint body content, encoded in unicode.

        '''
        params = {
            'filename': f'output_{name}.text'
        }
        return self.fetch_resource('in_out', params, 'DELETE')

    def netsynth(self, verilog_fp: str):
        '''
        Validates a passed in verilog specification file.

        (I'm a bit confused here, documentation says that this only serves
        as a mechanism for validation. I would assume that there might be some
        parsing of the verilog file into a valid circuit. Perhaps covered in
        Submit and this is just safety checking?)

        Args:
            verilog_fp: Filepath to verilog file.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        try:
            verilog_text = open(verilog_fp, 'r').read()
        except OSError as e:
            raise RuntimeError(
                f'Unable to locate passed in file {verilog_fp}. System '
                f'exception: {e}'
            )
        params = {
            'verilog_text': verilog_text
        }
        return self.fetch_resource('in_out', params)

    def submit(
            self,
            job_id: str,
            verilog_fp: str,
            inputs_fp: str,
            outputs_fp: str,
            options: str = None,
    ):
        '''
        Runs Cello.

        Args:
            job_id: Identification Number for the Job.
            verilog_fp: Filepath to the Verilog file.
            inputs_fp: Filepath to the inputs to the circuit.
            outputs_fp: Filepath to the outputs to the circuit.
            options: Additional Options. Example given in API documentation 
                are:
                    `-figures false -plasmid false -assignment_algorithm 
                    hill_climbing`

        Returns:
            Remote endpoint body content, encoded in unicode.

        '''
        try:
            verilog_text = open(verilog_fp, 'r').read()
            inputs = open(inputs_fp, 'r').read()
            outputs = open(outputs_fp, 'r').read()
        except OSError as e:
            raise RuntimeError(
                f'Unable to locate passed in filepath: {e}'
            )
        params = {
            'id': job_id,
            'input_promoter_data': inputs,
            'output_gene_data': outputs,
            'verilog_text': verilog_text,
            'options': options,
        }
        return self.fetch_resource('submit', params)

    def fetch_extension(
            self,
            job_id: str,
            extension: str,
            assignment: str = None,
    ):
        '''
        Fetches an extension.

        Args:
            job_id: Identification Number for the Job.
            extension: Which file extension to look for.
            assignment: Which assignment to look for, if passed in.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        params = {
            'job_id': job_id,
            'extension': extension,
        }
        if assignment is not None:
            if len(assignment) != 4 or assignment[0] != 'A':
                print('Invalid assignment name')
                return
            params['keyword'] = assignment
        resp = self.fetch_resource('results', params)
        return resp

    def show_parts(self, job_id: str, assignment: str = None):
        '''
        Prints all available parts to console/terminal.

        Args:
            job_id: Identification Number for the Job.
            assignment: Which assignment to look for, if passed in.
        '''
        resp = self.fetch_extension(job_id, assignment, 'parts_list.txt')
        filenames = json.loads(resp)
        params = {
            'job_id': job_id,
        }
        for filename in filenames:
            params['filename'] = filename
            resp = self.fetch_resource(f'results', params)
            parts = '[' + resp.split('[')[1]
            parts = parts.replace('[', '[\"')
            parts = parts.replace(']', '\"]')
            parts = parts.replace(', ', '\", \"')
            json.loads(parts)
            print(json.dumps(parts, indent=4))
            print('--------------------------')

    def show_files_contents(
            self,
            job_id,
            assignment,
            extension,
    ):
        '''
        Fetches file contents.
        
        Args:
            job_id: Identification Number for the Job
            assignment: Which assignment to look for
            extension:  Which file extension to look for

        '''

        resp = self.fetch_extension(job_id, assignment, extension)
        filenames = json.loads(resp)
        params = {
            'job_id': job_id
        }
        for filename in filenames:
            params['filename'] = filename
            print(Fore.GREEN + f"{self.fetch_resource('results', params)}")

    def show_reu_table(
            self,
            job_id: str,
            assignment: str,
    ):
        '''
        Shows the REU Table.
        
        Args:
            job_id: Identification Number for the Job.
            assignment: Which assignment to look for

        Returns:


        '''
        print(Fore.GREEN +
              f"{self.fetch_extension(job_id=job_id, assignment=assignment, extension='reutable.txt')}")

    def read_genbank(
            self,
            job_id: str,
            filename: str,
            seq: bool = False,
    ):
        '''
        Reads the passed in Genbank file.

        Args:
            job_id: Identification Number for the Job.
            filename: Filename of Genbank file.
            seq: Flag that determines if the sequence of the associated 
                Genbank file will be printed.

        '''
        # This is a bit interesting and deviates from the other established patterns.
        resp = self.fetch_resource('resultsroot')
        server_root = resp
        params = {
            'user_name': self.auth.username,
            'job_id': job_id,
            'filename': filename,
        }
        filepath = self.fetch_resource(server_root, params)
        genbank_record = SeqIO.read(open(filepath, 'r'), 'genbank')
        for feature in genbank_record.features:
            # The F-strings in the API are a problematic choice. I like how
            # they parse visually, and they are more performant than
            # standard formatting. As a culture most Bioinformatics users
            # tend to stick to older versions for everything and don't have
            # the option or were withal to update to newer python versions
            # so you're locking out a significant population of users you'd
            # want to adopt your tool. I'd probably default to what ever
            # the default installation version for the ubuntu kernel and
            # MacOS is and the options thereof if this were a distributed
            # package.
            print(Fore.GREEN +
                  f'{feature.location},'
                  f'{feature.type},'
                  f'{feature.qualifiers["label"]},'
                  f'{feature.extract(genbank_record.seq)}'
                  )
            if seq:
                print(Fore.GREEN + f'{feature.extract(genbank_record.seq)}')

    def post_ucf(self, name: str, filepath: str):
        '''
        Posts a UCF (User Constraint File) to the server.

        Args:
            name: Name of the file
            filepath: Filepath to the UCF file.

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        if not name.endswith('.UCF.json'):
            raise RuntimeError(
                'UCF File must end with proper extension. (`.UCF.json`)'
            )
        # The Load and then Dump strikes me as something that can be
        # simplified.
        filejson = json.loads(open(filepath, 'r').read())
        params = {
            'filetext': json.dumps(filejson),
        }
        return self.fetch_resource('ucf', params)

    def validate_ucf(self, name: str):
        '''
        Validates a UCF (User Constraint File) on the server.

        Args:
            name: Name of the file

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        if not name.endswith('.UCF.json'):
            raise RuntimeError(
                'UCF File must end with proper extension. (`.UCF.json`)'
            )
        params = {
            'name': name,
            'validate': 'validate',
        }
        return self.fetch_resource('ucf', params)

    def delete_ufc(self, name: str):
        '''
        Deletes a UCF (User Constraint File) on the server.

        Args:
            name: Name of the file

        Returns:
            Remote endpoint body content, encoded in unicode.
        '''
        if not name.endswith('.UCF.json'):
            raise RuntimeError(
                'UCF File must end with proper extension. (`.UCF.json`)'
            )
        params = {
            'name': name,
        }
        return self.fetch_resource('ucf', params, 'DELETE')
