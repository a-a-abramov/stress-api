import connexion
from flask import Response, json
import yaml
import subprocess
import uuid
import shutil
from pathlib import Path
import os

TMPDIR = "/tmp/stress-api-jobs"
SNG_FULLPATH = shutil.which("stress-ng")
TOKEN = os.environ.get("SNG_TOKEN")


def _run_inline(sng_args: list):
    result = subprocess.run(
        [SNG_FULLPATH] + sng_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"retcode": result.returncode, "info": result.stdout.decode()}


def _run_job(sng_job: str):
    job_id = str(uuid.uuid4())[:8]
    job_path = f'{TMPDIR}/{job_id}.job'
    result_path = f'{TMPDIR}/{job_id}.result'
    try:
        Path(TMPDIR).mkdir(exist_ok=True)
        with open(job_path, 'w') as f:
            f.write(sng_job)
        res = _run_inline(
            ["--quiet", "--yaml", result_path, "--job", job_path])

        if res["retcode"] == 0:
            with open(result_path, 'r') as f:
                yaml_result = yaml.safe_load(f)
            res["info"] = yaml_result
        return res
    except:
        raise
    finally:
        Path(job_path).unlink(missing_ok=True)
        Path(result_path).unlink(missing_ok=True)


def _response(result):
    return Response(response=json.dumps(result),
                    mimetype="application/json",
                    status=200 if result["retcode"] == 0 else 503)


def apikey_auth(provided_token):
    if provided_token != TOKEN:
        raise connexion.exceptions.OAuthProblem('Invalid token')
    return {'uid': 0}


def readiness():
    result = _run_inline(
        ["--vm", "1", "--vm-bytes", "4K", "--vm-ops", "1", "--timeout", "1s"])
    if result["retcode"] == 0:
        result["info"] = {"status": "ready"}
    return _response(result)


def runjob(jobfile):
    result = _run_job(str(jobfile, "utf-8"))
    return _response(result)


app = connexion.FlaskApp(__name__)
app.add_api('openapi.yaml',
            arguments={'title': 'Stress-ng REST API'},
            validate_responses=True)
application = app.app

# Leave this here for development purposes
if __name__ == '__main__':
    app.run(port=8080)
