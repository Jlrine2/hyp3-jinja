import json
import yaml

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_docker_image_parameters(job_spec):
    return [{
        'name': f'{k}_image',
        'description': f'Link to {k.upper()} processing image to use when running {k.upper()} jobs.'
    } for k, v in job_spec.items()]


def get_job_definitions(job_spec):
    return [{
        'name': f'{k}_job_definition',
        'api_job_type': v['api_job_type'],
        'parameters': v['parameters'],
        'timeout': v['timeout']
    } for k, v in job_spec.items()]


def get_step_function_choices(job_spec):
    return [{
        'Variable': '$.job_type',
        'StringEquals': v['api_job_type'],
        'Next': v['api_job_type']
    } for k, v in job_spec.items()]


def get_step_function_tasks(job_definitions):
    return [
    {
        job_definition['api_job_type']:
            {
               'Type': 'Task',
               'Resource': 'arn:aws:states:::batch:submitJob.sync',
               'Parameters': {
                   'JobDefinition': f'${{{job_definition["name"]}}}',
                   'JobName.$': '$.job_id',
                   'JobQueue': '${JobQueueArn}',
                   'Parameters.$': '$.job_parameters'
               },
               'ResultPath': '$.results.job_processing',
               'Next': 'GET_FILES',
               'Retry': [
                   {
                       'ErrorEquals': [
                           'States.ALL'
                       ],
                       'MaxAttempts': 2
                   }
               ],
               'Catch': [
                   {
                       'ErrorEquals': [
                           'States.ALL'
                       ],
                       'Next': 'JOB_FAILED',
                       'ResultPath': '$.results.job_processing'
                   }
               ]
            }
    } for job_definition in job_definitions]


def generate_cloudformation():
    with open('job-types.yml') as f:
        job_spec = yaml.safe_load(f)
    docker_image_parameters = get_docker_image_parameters(job_spec)
    job_definitions = get_job_definitions(job_spec)
    step_function_job_choices = get_step_function_choices(job_spec)
    step_function_job_tasks = get_step_function_tasks(job_definitions)

    env = Environment(loader=FileSystemLoader('templates/'), autoescape=select_autoescape(['html', 'xml']))
    env.trim_blocks = True
    env.lstrip_blocks = True
    template = env.get_template('step-function-spec.json')


if __name__ == '__main__':
    generate_cloudformation()
