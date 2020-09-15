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
        'command': v['command'],
        'timeout': v['timeout']
    } for k, v in job_spec.items()]

def generate_cloudformation():
    with open('job-types.yml') as f:
        job_spec = yaml.safe_load(f)
    docker_image_parameters = get_docker_image_parameters(job_spec)
    job_definitions = get_job_definitions(job_spec)

    env = Environment(loader=FileSystemLoader('templates/'), autoescape=select_autoescape(['html', 'xml']))
    env.trim_blocks = True
    env.lstrip_blocks = True
    with open('tmp/sf-spec.json', 'w+') as f:
        template = env.get_template('step-function-spec.json')
        f.write(template.render(docker_image_parameters=docker_image_parameters, job_definitions=job_definitions))
    with open('tmp/root-cf.yml', 'w+') as f:
        template = env.get_template('root-cf.yml')
        f.write(template.render(docker_image_parameters=docker_image_parameters, job_definitions=job_definitions))
    with open('tmp/batch-cluster-cf.yml', 'w+') as f:
        template = env.get_template('batch-cluster-cf.yml')
        f.write(template.render(docker_image_parameters=docker_image_parameters, job_definitions=job_definitions))
    with open('tmp/step-function-cf.yml', 'w+') as f:
        template = env.get_template('step-function-cf.yml')
        f.write(template.render(docker_image_parameters=docker_image_parameters, job_definitions=job_definitions))

if __name__ == '__main__':
    generate_cloudformation()
