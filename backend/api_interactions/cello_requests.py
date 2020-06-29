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
            if i-1 >= REQUEST_RETRIES:
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
        Upon
        Returns:

        '''
        self.validate_authentication()
        return self.auth

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CelloAPI:
    '''

    Returns:

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

        Returns:

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
    ):
        '''

        Args:
            end_point:
            operation:
            additional_arguments:

        Returns:

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

        Args:
            job_id:
            keyword:
            extension:
            filename:

        Returns:

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

        Args:
            name:

        Returns:

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

        Args:
            name:

        Returns:

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
            low: float,
            high: float,
            dnaseq: str,
    ):
        '''

        Args:
            name:
            low:
            high:
            dnaseq:

        Returns:

        '''
        file_string = f'{name} {low} {high} {dnaseq}\n'
        params = {
            'filename': f'input_{name}.text',
            'filetext': file_string,
        }
        return self.fetch_resource('in_out', params)

    def delete_input(self, name: str):
        '''

        Args:
            name:

        Returns:

        '''
        params = {
            'filename': f'input_{name}.text'
        }
        return self.fetch_resource('in_out', params, 'DELETE')

    def delete_output(self, name: str):
        '''

        Args:
            name:

        Returns:

        '''
        params = {
            'filename': f'output_{name}.text'
        }
        return self.fetch_resource('in_out', params, 'DELETE')

    def netsynth(self, verilog_fp: str):
        '''

        Args:
            verilog_fp:

        Returns:

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

        Args:
            job_id:
            verilog_fp:
            inputs_fp:
            outputs_fp:
            options:

        Returns:

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
            assignment: str,
            extension: str,
    ):
        '''

        Args:
            job_id:
            assignment:
            extension:

        Returns:

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

        Args:
            job_id:
            assignment:

        Returns:

        '''
        resp = self.fetch_extension(job_id, assignment, 'parts_list.txt')
        filenames = json.loads(resp)
        params = {
            'job_id': job_id,
        }
        for filename in filenames:
            params['filename'] = filename
            resp = self.fetch_resource(f'results', params)
            # TODO: This parsing dance might be simplified but I need to
            # investigate.
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

        resp = self.fetch_extension(job_id, assignment, extension)
        filenames = json.loads(resp)
        params = {
            'job_id': job_id
        }
        for filename in filenames:
            params['filename'] = filename
            self.fetch_resource('results', params)

    def show_reu_table(
            self,
            job_id: str,
            assignment: str,
    ):
        '''

        Args:
            job_id:
            assignment:

        Returns:

        '''
        self.fetch_extension(
            job_id=job_id,
            assignment=assignment,
            extension='reutable.txt'
        )

    def read_genbank(
            self,
            job_id: str,
            filename: str,
            seq: bool = False,
    ):
        '''

        Args:
            job_id:
            filename:
            seq:

        Returns:

        '''
        # This is a bit interesting and deviates from all of the other
        # established patterns.
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

        Args:
            name:
            filepath:

        Returns:

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
        # TODO: Test this, it deviates from the patterns set forth by the
        # other ones. I think he's actually trying to push arguments via
        # requests instead of just using the params thing as a way to create
        # filetree paths.
        return self.fetch_resource('ucf', params)

    def validate_ucf(self, name: str):
        '''

        Args:
            name:

        Returns:

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

        Args:
            name:

        Returns:

        '''
        if not name.endswith('.UCF.json'):
            raise RuntimeError(
                'UCF File must end with proper extension. (`.UCF.json`)'
            )
        params = {
            'name': name,
        }
        return self.fetch_resource('ucf', params, 'DELETE')
